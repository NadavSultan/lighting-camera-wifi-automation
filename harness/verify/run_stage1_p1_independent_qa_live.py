"""Independent QA live MapLibre checks for Stage 1 P1. Does not mutate product files."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import TimeoutError as PlaywrightTimeout
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
KML = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
EXPECTED_SHA = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"
DATA = ROOT / "harness" / "tmp" / "stage1-p1-qa"
SHOTS = DATA / "screenshots"
OUT = ROOT / "harness" / "verify" / "2026-09-08-stage1-p1-independent-qa-live.json"
API_PORT = 8078
UI_PORT = 3078
API = f"http://127.0.0.1:{API_PORT}"
UI = f"http://127.0.0.1:{UI_PORT}/"
VIEWPORTS = [(1920, 855), (1440, 855), (1366, 768), (1024, 768)]

CANVAS_PROBE = """(selector) => {
  const canvas = document.querySelector(selector);
  if (!canvas) return { present: false };
  const copy = document.createElement('canvas');
  copy.width = canvas.width;
  copy.height = canvas.height;
  const copyCtx = copy.getContext('2d');
  copyCtx.drawImage(canvas, 0, 0);
  const data = copyCtx.getImageData(0, 0, copy.width, copy.height).data;
  let painted = 0;
  let blueish = 0;
  let grayish = 0;
  let redish = 0;
  let yellowish = 0;
  for (let i = 0; i < data.length; i += 16) {
    const a = data[i + 3];
    if (a <= 8) continue;
    painted += 1;
    const r = data[i];
    const g = data[i + 1];
    const b = data[i + 2];
    if (b > r + 20 && b > g) blueish += 1;
    if (r > 80 && g > 80 && b > 80 && Math.abs(r - g) < 40 && Math.abs(g - b) < 40) grayish += 1;
    if (r > g + 30 && r > b + 30) redish += 1;
    if (r > 150 && g > 150 && b < 120) yellowish += 1;
  }
  return {
    present: true,
    width: canvas.width,
    height: canvas.height,
    clientWidth: canvas.clientWidth,
    clientHeight: canvas.clientHeight,
    painted,
    blueish,
    grayish,
    redish,
    yellowish,
    dataUrlBytes: copy.toDataURL('image/png').length,
  };
}"""

LAYOUT_PROBE = """() => {
  const workspace = document.querySelector('.workspace');
  const inspector = document.querySelector('.side-panel.inspector');
  const shell = document.querySelector('.app-shell');
  const topbar = document.querySelector('.topbar');
  const wr = workspace ? workspace.getBoundingClientRect() : null;
  const ir = inspector ? inspector.getBoundingClientRect() : null;
  const sr = shell ? shell.getBoundingClientRect() : null;
  const tr = topbar ? topbar.getBoundingClientRect() : null;
  const collapseInspector = document.querySelector('[aria-label="Collapse properties inspector"]');
  const collapseLayers = document.querySelector('[aria-label="Collapse layer panel"]');
  return {
    innerWidth: window.innerWidth,
    innerHeight: window.innerHeight,
    documentScrollWidth: document.documentElement.scrollWidth,
    overflowX: document.documentElement.scrollWidth > window.innerWidth + 1,
    workspaceWidth: wr && wr.width,
    workspaceRight: wr && wr.right,
    inspectorRight: ir && ir.right,
    inspectorLeft: ir && ir.left,
    shellWidth: sr && sr.width,
    topbarRight: tr && tr.right,
    collapseInspectorVisible: Boolean(collapseInspector && collapseInspector.getBoundingClientRect().right <= window.innerWidth + 1),
    collapseLayersVisible: Boolean(collapseLayers && collapseLayers.getBoundingClientRect().right <= window.innerWidth + 1),
  };
}"""

CARD_PROBE = """() => {
  const card = document.querySelector('.lighting-result-card');
  if (!card) return { present: false };
  const stats = card.querySelector('.lighting-result-stats');
  const body = card.querySelector('.lighting-result-card-body');
  const name = card.querySelector('.lighting-result-card-header strong');
  const cardRect = card.getBoundingClientRect();
  const statsRect = stats ? stats.getBoundingClientRect() : null;
  const style = getComputedStyle(card);
  const labels = stats ? Array.from(stats.querySelectorAll('dt')).map((el) => el.textContent.trim()) : [];
  const values = {};
  if (stats) {
    for (const row of stats.querySelectorAll('div')) {
      const dt = row.querySelector('dt');
      const dd = row.querySelector('dd');
      if (dt && dd) values[dt.textContent.trim()] = dd.textContent.trim();
    }
  }
  return {
    present: true,
    areaName: name ? name.textContent.trim() : null,
    width: cardRect.width,
    height: cardRect.height,
    maxHeight: style.maxHeight,
    labels,
    values,
    statsFullyVisible: Boolean(statsRect && statsRect.top >= cardRect.top - 1 && statsRect.bottom <= cardRect.bottom + 1),
    bodyClientHeight: body ? body.clientHeight : null,
    bodyScrollHeight: body ? body.scrollHeight : null,
    assumptionsCollapsed: Boolean(card.querySelector('details.lighting-result-assumptions') && !card.querySelector('details.lighting-result-assumptions[open]')),
  };
}"""

LABEL_ATTACH_PROBE = """() => {
  const canvas = document.querySelector('canvas.lighting-point-labels');
  const circles = document.querySelector('canvas.maplibregl-canvas');
  if (!canvas) return { present: false };
  const copy = document.createElement('canvas');
  copy.width = canvas.width;
  copy.height = canvas.height;
  const ctx = copy.getContext('2d');
  ctx.drawImage(canvas, 0, 0);
  const dpr = window.devicePixelRatio || 1;
  const data = ctx.getImageData(0, 0, copy.width, copy.height).data;
  function paintedAt(cssX, cssY, radius) {
    let count = 0;
    const x0 = Math.max(0, Math.floor((cssX - radius) * dpr));
    const y0 = Math.max(0, Math.floor((cssY - radius) * dpr));
    const x1 = Math.min(copy.width - 1, Math.floor((cssX + radius) * dpr));
    const y1 = Math.min(copy.height - 1, Math.floor((cssY + radius) * dpr));
    for (let y = y0; y <= y1; y += 1) {
      for (let x = x0; x <= x1; x += 1) {
        if (data[(y * copy.width + x) * 4 + 3] > 8) count += 1;
      }
    }
    return count;
  }
  return {
    present: true,
    painted: (() => {
      let n = 0;
      for (let i = 3; i < data.length; i += 16) if (data[i] > 8) n += 1;
      return n;
    })(),
    mapCanvas: circles ? { width: circles.width, height: circles.height } : null,
    sampleNearCenter: paintedAt(canvas.clientWidth / 2, canvas.clientHeight / 2, 80),
  };
}"""


def wait_http(url: str, timeout: float = 90.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            httpx.get(url, timeout=2.0)
            return
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}: {last}")


def stop_proc(proc: subprocess.Popen | None) -> None:
    if proc is None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except subprocess.TimeoutExpired:
        proc.kill()


def layout_ok(item: dict) -> bool:
    inner = item.get("innerWidth") or 0
    return (
        (item.get("workspaceRight") or 0) <= inner + 1
        and (item.get("inspectorRight") or 0) <= inner + 1
        and (item.get("topbarRight") or 0) <= inner + 1
        and not item.get("overflowX")
    )


def click_until_pole_selected(page, attempts: int = 24) -> bool:
    box = page.locator(".map-container").bounding_box()
    if not box:
        return False
    offsets = [
        (0.50, 0.50), (0.45, 0.50), (0.55, 0.50), (0.50, 0.45), (0.50, 0.55),
        (0.42, 0.48), (0.58, 0.52), (0.47, 0.42), (0.53, 0.58), (0.40, 0.40),
        (0.60, 0.60), (0.38, 0.52), (0.62, 0.48), (0.48, 0.38), (0.52, 0.62),
        (0.35, 0.50), (0.65, 0.50), (0.50, 0.35), (0.50, 0.65), (0.44, 0.56),
        (0.56, 0.44), (0.41, 0.59), (0.59, 0.41), (0.33, 0.45),
    ]
    for index, (fx, fy) in enumerate(offsets[:attempts]):
        page.mouse.click(box["x"] + box["width"] * fx, box["y"] + box["height"] * fy)
        try:
            page.locator("#fixture-model").wait_for(state="visible", timeout=1200)
            return True
        except PlaywrightTimeout:
            continue
    return page.locator("#fixture-model").count() > 0


def configure_selected_smart(page) -> None:
    page.locator("#fixture-model").scroll_into_view_if_needed()
    page.locator("#fixture-model").select_option("phoenix-1-smart")
    page.locator("#pole-height").fill("8")
    page.locator("#fixture-azimuth").wait_for(timeout=10000)
    page.locator("#fixture-azimuth").fill("0")
    page.locator("#fixture-azimuth").press("Tab")


def fill_test_only_cap(page) -> None:
    page.locator("#cap-field-operation_mode").select_option("recommend")
    page.locator("#cap-field-mode_permission").select_option("recommend_from_approved_pool")
    page.locator("#cap-field-gateway_appliance_counting").select_option("excluded")
    page.locator("#cap-field-colocated_fixture_counting").select_option("distinct_managed_node_once")
    page.locator("#cap-field-redundancy").select_option("single_allowed_with_warning")
    page.locator("#cap-field-node-LITE").select_option("non_node")
    page.locator("#cap-field-node-WIFI").select_option("non_node")
    page.locator("#cap-field-node-SMART").select_option("node")
    page.locator("#cap-field-product_mapping").fill("JNET1-TEST-ONLY")
    page.locator("#cap-field-variant").fill("JGW-JNET1-915-ID-TEST-ONLY")
    page.locator("#cap-field-band_and_jurisdiction").fill("915 MHz test-only")
    page.locator("#cap-field-link_distance_m").fill("20")
    page.locator("#cap-field-node_limit").fill("100")
    page.locator("#cap-field-child_limit").fill("16")
    page.locator("#cap-field-hop_limit").fill("64")


def run_session(page, record: dict, mode: str, full: bool = True) -> None:
    prefix = f"{mode}-"
    page.set_viewport_size({"width": 1920, "height": 855})
    page.goto(UI, wait_until="load", timeout=90000)
    page.wait_for_selector("text=Import KML/KMZ", timeout=30000)

    page.set_input_files("input[accept='.kml,.kmz']", str(KML))
    page.locator(".count-card strong").filter(has_text="74").first.wait_for(timeout=60000)
    summaries = httpx.get(f"{API}/api/projects", timeout=15.0).json()
    project_id = max(summaries, key=lambda item: item.get("updated_at") or "").get("id") if summaries else None
    imported = httpx.get(f"{API}/api/projects/{project_id}", timeout=30.0).json() if project_id else {}
    record[f"{mode}_import"] = {
        "id": imported.get("id"),
        "pole_count": len((imported.get("source") or {}).get("poles") or []),
        "source_sha256": ((imported.get("source") or {}).get("file") or {}).get("sha256"),
    }
    page.wait_for_timeout(2500)
    page.screenshot(path=str(SHOTS / f"{prefix}01-imported.png"), full_page=False)

    unconfigured = page.evaluate(CANVAS_PROBE, "canvas.fixture-direction-arrows")
    record[f"{mode}_arrows_unconfigured"] = unconfigured
    page.screenshot(path=str(SHOTS / f"{prefix}02-unconfigured-arrows.png"), full_page=False)

    selected = click_until_pole_selected(page)
    record[f"{mode}_pole_selected"] = selected
    if not selected:
        raise RuntimeError("could not select a pole on the map")
    page.locator("#fixture-model").wait_for(timeout=10000)
    with page.expect_response(lambda response: "/api/fixture-directions/preview" in response.url and response.request.method == "POST", timeout=30000):
        configure_selected_smart(page)
    page.wait_for_timeout(2500)
    page.evaluate("() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)))")
    configured = page.evaluate(CANVAS_PROBE, "canvas.fixture-direction-arrows")
    record[f"{mode}_arrows_configured"] = configured
    handle_count = page.locator(".azimuth-handle").count()
    record[f"{mode}_azimuth_handle_count"] = handle_count
    page.screenshot(path=str(SHOTS / f"{prefix}03-configured-smart.png"), full_page=False)
    try:
        page.locator("canvas.fixture-direction-arrows").screenshot(path=str(SHOTS / f"{prefix}03b-arrow-canvas.png"))
        page.locator("canvas.lighting-point-labels").screenshot(path=str(SHOTS / f"{prefix}03c-label-canvas.png"))
    except Exception as exc:  # noqa: BLE001
        record[f"{mode}_overlay_canvas_screenshot_error"] = str(exc)
    if not full:
        page.get_by_role("button", name="Draw Calculation Area").click()
        box = page.locator(".map-container").bounding_box()
        assert box
        for fx, fy in ((0.46, 0.46), (0.58, 0.46), (0.58, 0.58), (0.46, 0.58)):
            page.mouse.click(box["x"] + box["width"] * fx, box["y"] + box["height"] * fy)
            page.wait_for_timeout(150)
        page.get_by_role("button", name="Validate and save polygon").click()
        page.get_by_role("button", name="Calculate Lighting").click()
        page.locator(".lighting-result-card").wait_for(timeout=60000)
        page.wait_for_timeout(1000)
        record[f"{mode}_card"] = page.evaluate(CARD_PROBE)
        record[f"{mode}_labels_before"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
        page.screenshot(path=str(SHOTS / f"{prefix}05-lighting-card.png"), full_page=False)
        return

    viewports = []
    for width, height in VIEWPORTS:
        page.set_viewport_size({"width": width, "height": height})
        page.wait_for_timeout(500)
        metrics = page.evaluate(LAYOUT_PROBE)
        viewports.append({"width": width, "height": height, **metrics})
        page.screenshot(path=str(SHOTS / f"{prefix}layout-{width}.png"), full_page=False)
    record[f"{mode}_viewports"] = viewports

    page.set_viewport_size({"width": 1920, "height": 855})
    page.wait_for_timeout(400)
    page.get_by_role("button", name="Collapse layer panel").click()
    page.get_by_role("button", name="Collapse properties inspector").click()
    page.wait_for_timeout(400)
    collapsed = page.evaluate(LAYOUT_PROBE)
    record[f"{mode}_collapsed"] = collapsed
    page.screenshot(path=str(SHOTS / f"{prefix}04-collapsed.png"), full_page=False)
    page.get_by_role("button", name="Expand Layers").click()
    page.get_by_role("button", name="Expand Properties").click()
    page.wait_for_timeout(400)

    page.get_by_role("button", name="Draw Calculation Area").click()
    box = page.locator(".map-container").bounding_box()
    assert box
    points = [(0.46, 0.46), (0.58, 0.46), (0.58, 0.58), (0.46, 0.58)]
    for fx, fy in points:
        page.mouse.click(box["x"] + box["width"] * fx, box["y"] + box["height"] * fy)
        page.wait_for_timeout(200)
    page.get_by_role("button", name="Validate and save polygon").click()
    page.wait_for_timeout(800)
    page.get_by_role("button", name="Calculate Lighting").click()
    page.locator(".lighting-result-card").wait_for(timeout=60000)
    page.wait_for_timeout(1500)
    card = page.evaluate(CARD_PROBE)
    record[f"{mode}_card"] = card
    page.screenshot(path=str(SHOTS / f"{prefix}05-lighting-card.png"), full_page=False)
    labels_before = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
    record[f"{mode}_labels_before"] = labels_before
    page.screenshot(path=str(SHOTS / f"{prefix}06-labels-before-motion.png"), full_page=False)
    try:
        page.locator("canvas.lighting-point-labels").screenshot(path=str(SHOTS / f"{prefix}06b-label-canvas.png"))
        page.locator(".map-stage").screenshot(path=str(SHOTS / f"{prefix}06c-map-stage.png"))
    except Exception as exc:  # noqa: BLE001
        record[f"{mode}_label_canvas_screenshot_error"] = str(exc)

    zoom_in = page.locator(".maplibregl-ctrl-zoom-in")
    for _ in range(6):
        if zoom_in.count():
            zoom_in.first.click()
            page.wait_for_timeout(250)
    page.wait_for_timeout(800)
    record[f"{mode}_labels_zoomed"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
    page.screenshot(path=str(SHOTS / f"{prefix}06d-labels-zoomed.png"), full_page=False)
    try:
        page.locator(".map-stage").screenshot(path=str(SHOTS / f"{prefix}06e-map-stage-zoomed.png"))
    except Exception:
        pass

    map_box = page.locator(".map-container").bounding_box()
    assert map_box
    page.mouse.move(map_box["x"] + map_box["width"] * 0.55, map_box["y"] + map_box["height"] * 0.55)
    page.mouse.down()
    page.mouse.move(map_box["x"] + map_box["width"] * 0.35, map_box["y"] + map_box["height"] * 0.40, steps=12)
    page.mouse.up()
    page.wait_for_timeout(800)
    record[f"{mode}_labels_after_pan"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
    page.screenshot(path=str(SHOTS / f"{prefix}07-labels-after-pan.png"), full_page=False)

    page.mouse.wheel(0, -800)
    page.wait_for_timeout(800)
    record[f"{mode}_labels_after_zoom"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
    page.screenshot(path=str(SHOTS / f"{prefix}08-labels-after-zoom.png"), full_page=False)

    map_box = page.locator(".map-container").bounding_box()
    if map_box:
        page.keyboard.down("Control")
        page.mouse.move(map_box["x"] + map_box["width"] * 0.55, map_box["y"] + map_box["height"] * 0.50)
        page.mouse.down()
        page.mouse.move(map_box["x"] + map_box["width"] * 0.70, map_box["y"] + map_box["height"] * 0.50, steps=16)
        page.mouse.up()
        page.keyboard.up("Control")
    page.wait_for_timeout(800)
    record[f"{mode}_labels_after_rotate"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
    page.screenshot(path=str(SHOTS / f"{prefix}09-labels-after-rotate.png"), full_page=False)

    page.set_viewport_size({"width": 1440, "height": 855})
    page.wait_for_timeout(800)
    record[f"{mode}_labels_after_resize"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
    page.screenshot(path=str(SHOTS / f"{prefix}10-labels-after-resize.png"), full_page=False)
    page.set_viewport_size({"width": 1920, "height": 855})
    page.wait_for_timeout(500)

    card_box = page.locator(".lighting-result-card-header").bounding_box()
    arrows_before_drag = page.evaluate(CANVAS_PROBE, "canvas.fixture-direction-arrows")
    if card_box:
        page.mouse.move(card_box["x"] + 40, card_box["y"] + 10)
        page.mouse.down()
        page.mouse.move(card_box["x"] + 160, card_box["y"] + 80, steps=10)
        page.mouse.up()
        page.wait_for_timeout(400)
    arrows_after_drag = page.evaluate(CANVAS_PROBE, "canvas.fixture-direction-arrows")
    record[f"{mode}_card_drag"] = {
        "arrows_painted_before": arrows_before_drag.get("painted"),
        "arrows_painted_after": arrows_after_drag.get("painted"),
        "arrow_size_before": (arrows_before_drag.get("width"), arrows_before_drag.get("height")),
        "arrow_size_after": (arrows_after_drag.get("width"), arrows_after_drag.get("height")),
    }
    page.screenshot(path=str(SHOTS / f"{prefix}11-card-drag.png"), full_page=False)

    page.locator("#cap-planning-panel").scroll_into_view_if_needed()
    fill_test_only_cap(page)
    click_until_pole_selected(page)
    add_site = page.get_by_role("button", name="Add selected pole as CAP site")
    record[f"{mode}_add_cap_site_enabled"] = add_site.is_enabled() if add_site.count() else False
    if add_site.count() and add_site.is_enabled():
        add_site.scroll_into_view_if_needed()
        add_site.click()
    feasible = page.get_by_role("button", name="Mark test-only feasible")
    if feasible.count():
        feasible.first.scroll_into_view_if_needed()
        feasible.first.click()
        page.wait_for_timeout(400)
        recommend = page.get_by_role("button", name="Recommend CAP")
        record[f"{mode}_recommend_enabled"] = recommend.is_enabled()
        if recommend.is_enabled():
            recommend.click()
            page.get_by_text("Recommended CAP units:").wait_for(timeout=30000)
            show = page.get_by_role("button", name="Show selected sites on map")
            show.click()
            page.wait_for_timeout(1500)
            record[f"{mode}_labels_after_cap_show"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")
            page.screenshot(path=str(SHOTS / f"{prefix}12-after-cap-show.png"), full_page=False)
        else:
            record[f"{mode}_labels_after_cap_show"] = {"skipped": True, "reason": "Recommend CAP remained disabled"}
            page.screenshot(path=str(SHOTS / f"{prefix}12-cap-disabled.png"), full_page=False)
    else:
        record[f"{mode}_recommend_enabled"] = False
        record[f"{mode}_labels_after_cap_show"] = {"skipped": True, "reason": "Mark test-only feasible was not available"}
        page.screenshot(path=str(SHOTS / f"{prefix}12-cap-no-candidate.png"), full_page=False)

    record[f"{mode}_arrows_final"] = page.evaluate(CANVAS_PROBE, "canvas.fixture-direction-arrows")
    record[f"{mode}_labels_final"] = page.evaluate(CANVAS_PROBE, "canvas.lighting-point-labels")


def start_backend() -> subprocess.Popen:
    env = os.environ.copy()
    env["LCWA_DATA_DIR"] = str(DATA / "projects")
    env["LCWA_CATALOG_DIR"] = str(DATA / "catalogs")
    (DATA / "projects").mkdir(parents=True, exist_ok=True)
    (DATA / "catalogs").mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(API_PORT)],
        cwd=str(ROOT / "backend"),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def start_frontend(command: list[str], extra_env: dict[str, str] | None = None) -> subprocess.Popen:
    env = os.environ.copy()
    env["NEXT_PUBLIC_API_URL"] = API
    env["PORT"] = str(UI_PORT)
    if extra_env:
        env.update(extra_env)
    if os.name == "nt":
        return subprocess.Popen(
            subprocess.list2cmdline(command),
            cwd=str(ROOT / "frontend"),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
    return subprocess.Popen(
        command,
        cwd=str(ROOT / "frontend"),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def main() -> int:
    DATA.mkdir(parents=True, exist_ok=True)
    SHOTS.mkdir(parents=True, exist_ok=True)
    kml_sha = hashlib.sha256(KML.read_bytes()).hexdigest()
    record: dict = {
        "kml_sha256": kml_sha,
        "expected_sha256": EXPECTED_SHA,
        "api": API,
        "ui": UI,
        "errors": [],
    }
    backend = start_backend()
    frontend = None
    try:
        wait_http(f"{API}/api/health")
        record["live_health"] = httpx.get(f"{API}/api/health", timeout=5.0).json()

        if os.environ.get("LCWA_QA_DEV_ONLY") == "1":
            frontend = start_frontend(["corepack", "pnpm", "exec", "vinext", "dev", "-p", str(UI_PORT), "-H", "127.0.0.1"])
            wait_http(UI, timeout=120)
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1920, "height": 855})
                run_session(page, record, "dev", full=False)
                browser.close()
            prod_import = record.get("dev_import") or {}
            record["hash_ok"] = kml_sha == EXPECTED_SHA and prod_import.get("source_sha256") == EXPECTED_SHA and prod_import.get("pole_count") == 74
            record["layout_ok"] = True
            card = record.get("dev_card") or {}
            required = {"Eavg", "Emin", "Emax", "Emin/Eavg", "Emin/Emax"}
            record["card_ok"] = (
                card.get("present")
                and required.issubset(set(card.get("labels") or []))
                and card.get("statsFullyVisible")
                and "220px" not in str(card.get("maxHeight") or "")
            )
            arrows = record.get("dev_arrows_configured") or {}
            record["arrows_painted"] = bool(arrows.get("painted"))
            labels = record.get("dev_labels_before") or {}
            record["labels_painted"] = bool(labels.get("painted"))
            DEV_OUT = ROOT / "harness" / "verify" / "2026-09-08-stage1-p1-independent-qa-dev.json"
            DEV_OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
            print(json.dumps({key: record.get(key) for key in (
                "hash_ok", "card_ok", "arrows_painted", "labels_painted",
                "dev_import", "dev_arrows_configured", "dev_card", "live_health",
            )}, indent=2))
            return 0
            build = subprocess.run(
                "corepack pnpm run build",
                cwd=str(ROOT / "frontend"),
                shell=True,
                env={**os.environ, "NEXT_PUBLIC_API_URL": API},
            )
            if build.returncode != 0:
                raise RuntimeError(f"frontend production rebuild for isolated API failed with {build.returncode}")
        frontend = start_frontend(["corepack", "pnpm", "exec", "vinext", "start", "-p", str(UI_PORT), "-H", "127.0.0.1"])
        wait_http(UI, timeout=120)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 855})
            run_session(page, record, "prod")
            browser.close()
        stop_proc(frontend)
        frontend = None

        frontend = start_frontend(["corepack", "pnpm", "exec", "vinext", "dev", "-p", str(UI_PORT), "-H", "127.0.0.1"])
        wait_http(UI, timeout=120)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 855})
            run_session(page, record, "dev", full=False)
            browser.close()

        prod_import = record.get("prod_import") or {}
        record["hash_ok"] = kml_sha == EXPECTED_SHA and prod_import.get("source_sha256") == EXPECTED_SHA and prod_import.get("pole_count") == 74
        record["layout_ok"] = all(layout_ok(item) for item in record.get("prod_viewports") or [])
        card = record.get("prod_card") or {}
        required = {"Eavg", "Emin", "Emax", "Emin/Eavg", "Emin/Emax"}
        record["card_ok"] = (
            card.get("present")
            and required.issubset(set(card.get("labels") or []))
            and card.get("statsFullyVisible")
            and "220px" not in str(card.get("maxHeight") or "")
        )
        arrows = record.get("prod_arrows_configured") or {}
        record["arrows_painted"] = bool(arrows.get("painted"))
        labels = record.get("prod_labels_after_pan") or {}
        record["labels_painted"] = bool(labels.get("painted"))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps({key: record[key] for key in (
            "hash_ok", "layout_ok", "card_ok", "arrows_painted", "labels_painted",
            "prod_import", "prod_arrows_unconfigured", "prod_arrows_configured",
            "prod_card", "prod_recommend_enabled", "live_health",
        ) if key in record}, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        record["errors"].append(str(exc))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps(record, indent=2)[:8000])
        raise
    finally:
        stop_proc(frontend)
        stop_proc(backend)


if __name__ == "__main__":
    raise SystemExit(main())
