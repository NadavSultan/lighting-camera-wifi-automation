"""Independent Stage 3 P2 QA live checks. Isolated production UI + isolated FastAPI store."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import tempfile
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
KML = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
EXPECTED_SHA = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"
OUT = ROOT / "harness" / "verify" / "2026-09-16-stage3-p2-usability-independent-qa-live.json"
SHOTS = ROOT / "harness" / "tmp" / "stage3-p2-independent-qa" / "screenshots"
API_PORT = 8057
UI_PORT = 3057
API = f"http://127.0.0.1:{API_PORT}"
UI = f"http://127.0.0.1:{UI_PORT}/"


def stop_proc(proc: subprocess.Popen | None) -> None:
    if proc is None or proc.poll() is not None:
        return
    if os.name == "nt" and proc.pid:
        subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"], capture_output=True, check=False)
        return
    proc.terminate()
    try:
        proc.wait(timeout=8)
    except Exception:  # noqa: BLE001
        proc.kill()


def wait_http(url: str, timeout: float = 90.0) -> None:
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            response = httpx.get(url, timeout=2.0)
            if response.status_code < 500:
                return
            last = f"HTTP {response.status_code}"
        except Exception as exc:  # noqa: BLE001
            last = exc
        time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}: {last}")


def panel_metrics(page) -> dict:
    return page.evaluate(
        """() => {
          const panel = document.querySelector('aside.side-panel:not(.inspector)');
          const scroll = panel && panel.querySelector('.panel-scroll');
          const errors = window.__stage3QaConsoleErrors || [];
          const show = [...document.querySelectorAll('button')].filter((b) => b.textContent.trim() === 'Show results');
          const primary = [...document.querySelectorAll('button')].find((item) => item.textContent.trim() === 'Calculate CAP recommendation');
          const rows = [...document.querySelectorAll('.calculation-row')].map((row) => ({
            text: row.innerText.slice(0, 240),
            showDisabled: (() => {
              const button = [...row.querySelectorAll('button')].find((item) => item.textContent.trim() === 'Show results');
              return button ? button.disabled : null;
            })(),
          }));
          return {
            innerWidth: window.innerWidth,
            panelOverflowX: panel ? panel.scrollWidth > panel.clientWidth + 1 : null,
            scrollOverflowXStyle: scroll ? getComputedStyle(scroll).overflowX : null,
            switcher: [...document.querySelectorAll('.discipline-switcher button')].map((button) => ({
              label: button.textContent.trim(),
              selected: button.getAttribute('aria-selected') === 'true',
            })),
            showResultsCount: show.length,
            showResultsEnabled: show.filter((button) => !button.disabled).length,
            lightingCardCount: document.querySelectorAll('.lighting-result-card').length,
            lightingCardText: document.querySelector('.lighting-result-card')?.innerText.slice(0, 240) || null,
            calculationRows: rows,
            capPrimary: primary ? { disabled: primary.disabled, visible: primary.offsetParent !== null, className: primary.className } : null,
            capNotCalculated: [...document.querySelectorAll('p')].some((p) => p.textContent.includes('No current CAP result')),
            capCurrentBanner: [...document.querySelectorAll('strong')].some((el) => el.textContent.trim() === 'Current CAP result'),
            capError: [...document.querySelectorAll('strong')].some((el) => el.textContent.includes('CAP calculation error')),
            capZeroSelected: [...document.querySelectorAll('p')].some((p) => p.textContent.includes('Current result has zero selected CAP sites')),
            capUnresolved: [...document.querySelectorAll('strong')].some((el) => /unresolved node/.test(el.textContent)),
            capRecommended: [...document.querySelectorAll('strong')].some((el) => el.textContent.includes('Recommended CAP units:')),
            capInputsDetails: !!document.querySelector('#cap-planning-panel details.cap-required-inputs'),
            projectionBoundary: [...document.querySelectorAll('.camera-projection-legend')].map((el) => el.innerText).join('\\n'),
            mapLayerIds: (() => {
              const canvas = document.querySelector('.maplibregl-canvas');
              return canvas ? 'present' : 'missing';
            })(),
            extraCameraLayers: !!document.querySelector('.pixel-density-layer, .projection-boundary-layer'),
            consoleErrors: errors,
          };
        }"""
    )


def card_css(page) -> dict | None:
    return page.evaluate(
        """() => {
          const card = document.querySelector('.lighting-result-card');
          if (!card) return null;
          return {
            count: document.querySelectorAll('.lighting-result-card').length,
            cssLeft: parseFloat(card.style.left || '0'),
            cssTop: parseFloat(card.style.top || '0'),
            text: card.innerText.slice(0, 240),
          };
        }"""
    )


def draw_triangle(page, offsets):
    page.locator(".maplibregl-canvas").first.wait_for(state="visible")
    page.wait_for_function(
        "() => { const canvas = document.querySelector('.maplibregl-canvas'); return canvas && canvas.width > 0 && canvas.height > 0; }",
        timeout=30000,
    )
    page.wait_for_timeout(800)
    box = page.locator(".map-container").bounding_box()
    if not box:
        raise RuntimeError("map container missing")
    for x_frac, y_frac in offsets:
        page.mouse.click(box["x"] + box["width"] * x_frac, box["y"] + box["height"] * y_frac)
        page.wait_for_timeout(300)


def close_lighting_card(page) -> None:
    closer = page.get_by_role("button", name="Close lighting results")
    if closer.count() and closer.first.is_visible():
        closer.first.click()
        page.wait_for_timeout(200)


def finish_polygon(page) -> None:
    panel = page.get_by_role("button", name="Validate and save polygon")
    if panel.count() and panel.first.is_visible():
        panel.first.click()
        return
    page.locator(".polygon-draft-guide").get_by_role("button", name="Finish").click(force=True)


def fill_test_only_cap(page) -> None:
    page.locator("#cap-field-operation_mode").select_option("recommend")
    page.locator("#cap-field-mode_permission").select_option("recommend_from_approved_pool")
    page.locator("#cap-field-gateway_appliance_counting").select_option("excluded")
    page.locator("#cap-field-colocated_fixture_counting").select_option("distinct_managed_node_once")
    page.locator("#cap-field-redundancy").select_option("single_allowed_with_warning")
    page.locator("#cap-field-node-LITE").select_option("non_node")
    page.locator("#cap-field-node-WIFI").select_option("non_node")
    page.locator("#cap-field-node-SMART").select_option("non_node")
    page.locator("#cap-field-product_mapping").fill("JNET1-TEST-ONLY")
    page.locator("#cap-field-variant").fill("JGW-JNET1-915-ID-TEST-ONLY")
    page.locator("#cap-field-band_and_jurisdiction").fill("915 MHz test-only")
    page.locator("#cap-field-link_distance_m").fill("20")
    page.locator("#cap-field-node_limit").fill("100")
    page.locator("#cap-field-child_limit").fill("16")
    page.locator("#cap-field-hop_limit").fill("64")


def main() -> int:
    SHOTS.mkdir(parents=True, exist_ok=True)
    kml_bytes = KML.read_bytes()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    record: dict = {
        "identity": "independent-qa",
        "head": head,
        "kml_sha256": hashlib.sha256(kml_bytes).hexdigest(),
        "expected_sha256": EXPECTED_SHA,
        "api": API,
        "ui": UI,
        "errors": [],
        "lighting_calculate_requests": [],
        "viewports": [],
    }
    data_dir = Path(tempfile.mkdtemp(prefix="lcwa-stage3-p2-qa-"))
    record["data_dir"] = str(data_dir)
    env = os.environ.copy()
    env["LCWA_DATA_DIR"] = str(data_dir)
    api_proc = None
    ui_proc = None
    try:
        api_proc = subprocess.Popen(
            [str(ROOT / ".venv" / "Scripts" / "python.exe"), "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", str(API_PORT)],
            cwd=str(ROOT / "backend"),
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        ui_env = os.environ.copy()
        ui_env["NEXT_PUBLIC_API_URL"] = API
        ui_proc = subprocess.Popen(
            ["corepack", "pnpm", "exec", "vinext", "start", "--host", "127.0.0.1", "--port", str(UI_PORT)],
            cwd=str(ROOT / "frontend"),
            env=ui_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=True,
        )
        wait_http(f"{API}/api/health")
        wait_http(UI)
        record["live_health"] = httpx.get(f"{API}/api/health", timeout=5.0).json()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 855})
            page.add_init_script(
                "window.__stage3QaConsoleErrors = [];"
                "window.addEventListener('error', (e) => window.__stage3QaConsoleErrors.push(String(e.message || e.error)));"
                "window.addEventListener('unhandledrejection', (e) => window.__stage3QaConsoleErrors.push(String(e.reason)));"
            )
            page.on("pageerror", lambda exc: record["errors"].append(f"pageerror:{exc}"))
            page.on("console", lambda msg: record["errors"].append(f"console:{msg.type}:{msg.text}") if msg.type == "error" else None)

            def on_request(request):
                if "/lighting/calculate/" in request.url:
                    record["lighting_calculate_requests"].append({"url": request.url, "method": request.method})

            page.on("request", on_request)
            page.goto(UI, wait_until="load", timeout=60000)
            page.locator(".discipline-switcher").wait_for(timeout=30000)
            page.set_input_files("input[accept='.kml,.kmz']", str(KML))
            page.locator(".count-card strong").filter(has_text="74").first.wait_for(timeout=60000)
            record["pole_count"] = 74
            projects = httpx.get(f"{API}/api/projects", timeout=10.0).json()
            record["api_projects"] = projects
            imported = None
            if isinstance(projects, list) and projects:
                imported = httpx.get(f"{API}/api/projects/{projects[0]['id']}", timeout=30.0).json()
            record["import_sha256"] = ((imported or {}).get("source") or {}).get("file", {}).get("sha256")
            record["mode"] = (imported or {}).get("mode")
            record["after_open"] = panel_metrics(page)
            page.screenshot(path=str(SHOTS / "01-imported.png"))

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            draw_triangle(page, [(0.42, 0.42)])
            page.wait_for_timeout(200)
            before_switch = page.locator(".polygon-draft-guide").inner_text()
            for tab in ("Camera", "Wi-Fi", "CAP", "Lighting"):
                page.get_by_role("tab", name=tab).click()
                page.wait_for_timeout(150)
            record["draft_preserved_all_disciplines"] = {
                "before": before_switch,
                "after": page.locator(".polygon-draft-guide").inner_text() if page.locator(".polygon-draft-guide").count() else None,
                "guideVisible": page.locator(".polygon-draft-guide").count() > 0 and page.locator(".polygon-draft-guide").first.is_visible(),
            }
            page.locator(".polygon-draft-guide").get_by_role("button", name="Cancel").click()
            page.wait_for_timeout(200)

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            draw_triangle(page, [(0.46, 0.46), (0.58, 0.46), (0.58, 0.58)])
            page.locator(".polygon-draft-guide span").filter(has_text="3 vertices").wait_for(timeout=15000)
            finish_polygon(page)
            page.wait_for_timeout(400)
            calc_before_first = len(record["lighting_calculate_requests"])
            page.get_by_role("button", name="Calculate Lighting").click()
            page.locator(".lighting-result-card").wait_for(timeout=60000)
            record["first_card"] = card_css(page)
            record["after_first_calculate"] = panel_metrics(page)
            header = page.locator(".lighting-result-card-header")
            box = header.bounding_box()
            if box:
                page.mouse.move(box["x"] + 20, box["y"] + 8)
                page.mouse.down()
                page.mouse.move(box["x"] + 110, box["y"] + 90, steps=8)
                page.mouse.up()
            page.wait_for_timeout(250)
            record["first_card_dragged"] = card_css(page)
            close_lighting_card(page)

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            draw_triangle(page, [(0.56, 0.38), (0.70, 0.38), (0.63, 0.52)])
            page.locator(".polygon-draft-guide span").filter(has_text="3 vertices").wait_for(timeout=8000)
            finish_polygon(page)
            page.wait_for_timeout(400)
            page.get_by_role("button", name="Calculate Lighting").click()
            page.locator(".lighting-result-card").wait_for(timeout=60000)
            record["second_card"] = card_css(page)
            header = page.locator(".lighting-result-card-header")
            box = header.bounding_box()
            if box:
                page.mouse.move(box["x"] + 20, box["y"] + 8)
                page.mouse.down()
                page.mouse.move(box["x"] + 40, box["y"] + 40, steps=6)
                page.mouse.up()
            page.wait_for_timeout(250)
            record["second_card_dragged"] = card_css(page)
            record["show_results_count"] = page.get_by_role("button", name="Show results").count()
            record["after_two_areas"] = panel_metrics(page)
            calc_before_show = len(record["lighting_calculate_requests"])

            page.locator(".calculation-row").filter(has_text="Calculation area 1").get_by_role("button", name="Show results").click()
            page.wait_for_timeout(400)
            record["opened_first"] = card_css(page)
            page.locator(".calculation-row").filter(has_text="Calculation area 2").get_by_role("button", name="Show results").click()
            page.wait_for_timeout(400)
            record["opened_second"] = card_css(page)
            page.locator(".calculation-row").filter(has_text="Calculation area 1").get_by_role("button", name="Show results").click()
            page.wait_for_timeout(400)
            record["reopened_first"] = card_css(page)
            record["show_results_did_not_calculate"] = len(record["lighting_calculate_requests"]) == calc_before_show
            record["calculate_request_count_after_first"] = calc_before_first
            page.screenshot(path=str(SHOTS / "02-lighting-restore.png"))

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            page.locator(".polygon-draft-guide").get_by_role("button", name="Cancel").click()
            page.wait_for_timeout(200)
            record["after_cancel_draft"] = panel_metrics(page)

            page.locator(".calculation-row").filter(has_text="Calculation area 2").get_by_role("button", name="Show results").click()
            page.wait_for_timeout(300)
            record["area2_card_before_invalidate"] = card_css(page)
            page.locator(".calculation-row").filter(has_text="Calculation area 2").get_by_role("button", name="Edit").click()
            page.locator("#calculation-area-name").fill("Area 2 edited")
            page.get_by_role("button", name="Save details").click()
            page.wait_for_timeout(400)
            record["after_invalidate_area_2"] = panel_metrics(page)
            record["after_invalidate_card"] = card_css(page)

            page.locator(".calculation-row").filter(has_text="Area 2 edited").get_by_role("button", name="Delete").click()
            page.wait_for_timeout(300)
            record["after_delete_area_2"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  return {
                    rows: [...document.querySelectorAll('.calculation-row strong')].map((el) => el.textContent),
                    showResultsEnabled: [...document.querySelectorAll('button')].filter((b) => b.textContent.trim() === 'Show results' && !b.disabled).length,
                    cardText: card ? card.innerText.slice(0, 120) : null,
                    cardCount: document.querySelectorAll('.lighting-result-card').length,
                  };
                }"""
            )
            if record["after_delete_area_2"].get("showResultsEnabled") == 1:
                page.locator(".calculation-row").filter(has_text="Calculation area 1").get_by_role("button", name="Show results").click()
                page.wait_for_timeout(300)
                record["area1_after_delete_other"] = card_css(page)

            page.get_by_role("tab", name="CAP").click()
            page.wait_for_timeout(300)
            record["cap_pane_initial"] = panel_metrics(page)
            record["cap_pane_text_initial"] = page.locator("#cap-planning-panel").inner_text()[:1800]
            review = page.locator("#cap-planning-panel").get_by_role("button", name="Review input")
            record["cap_review_count"] = review.count()
            review_probe = """() => {
              const active = document.activeElement;
              const field = document.getElementById('cap-field-product_mapping');
              const fieldDetails = field ? field.closest('details') : null;
              return {
                activeId: active && active.id,
                activeTag: active && active.tagName,
                productMappingDetailsOpen: fieldDetails ? fieldDetails.open : null,
                productMappingVisible: !!(field && field.offsetParent !== null),
                blockers: [...document.querySelectorAll('.cap-blocker-list li')].map((li) => li.innerText.trim()),
              };
            }"""
            if review.count():
                review.first.click()
                page.wait_for_timeout(250)
                record["cap_review_focus_collapsed"] = page.evaluate(review_probe)
            page.locator("summary").filter(has_text="Required CAP inputs").click()
            page.wait_for_timeout(150)
            page.locator("summary").filter(has_text="Candidates and locks").click()
            page.wait_for_timeout(150)
            add_site = page.get_by_role("button", name="Add selected pole as CAP site")
            record["cap_add_site_enabled"] = add_site.is_enabled() if add_site.count() else False
            try:
                if add_site.count() and add_site.is_enabled():
                    add_site.click()
                feasible = page.get_by_role("button", name="Mark test-only feasible")
                try:
                    feasible.first.wait_for(state="attached", timeout=8000)
                except Exception:
                    page.locator("#manual-cap-longitude").fill("-80.26")
                    page.locator("#manual-cap-latitude").fill("25.75")
                    page.get_by_role("button", name="Add distinct manual non-pole CAP site").click()
                    feasible.first.wait_for(state="attached", timeout=20000)
                feasible.first.scroll_into_view_if_needed()
                feasible.first.click()
                page.wait_for_timeout(800)
                record["cap_candidate_rows"] = page.locator("#cap-section-candidates .priority-row").count()
            except Exception as exc:  # noqa: BLE001
                record["cap_candidate_error"] = str(exc)
            fill_test_only_cap(page)
            page.wait_for_timeout(400)
            if review.count():
                review.first.click()
                page.wait_for_timeout(250)
                record["cap_review_focus_open"] = page.evaluate(review_probe)
            record["cap_after_profile"] = panel_metrics(page)
            record["cap_after_profile_text"] = page.locator("#cap-planning-panel").inner_text()[:2200]
            primary = page.get_by_role("button", name="Calculate CAP recommendation")
            try:
                page.wait_for_function(
                    """() => {
                      const button = [...document.querySelectorAll('button')].find((item) => item.textContent.trim() === 'Calculate CAP recommendation');
                      return button && !button.disabled;
                    }""",
                    timeout=20000,
                )
            except Exception as exc:  # noqa: BLE001
                record["cap_primary_enable_wait_error"] = str(exc)
            record["cap_primary_after_profile"] = {
                "count": primary.count(),
                "disabled": primary.is_disabled() if primary.count() else None,
            }
            if primary.count() and not primary.is_disabled():
                primary.click()
                page.wait_for_timeout(800)
                try:
                    page.get_by_text("Recommended CAP units:").wait_for(timeout=30000)
                except Exception as exc:  # noqa: BLE001
                    record["cap_recommend_wait_error"] = str(exc)
                record["cap_zero_selected_live"] = panel_metrics(page)
                record["cap_zero_selected_text"] = page.locator("#cap-planning-panel").inner_text()[:2000]
                page.screenshot(path=str(SHOTS / "03-cap-zero.png"))
                page.locator("#cap-field-node-LITE").select_option("node")
                page.wait_for_timeout(400)
                try:
                    page.wait_for_function(
                        """() => {
                          const button = [...document.querySelectorAll('button')].find((item) => item.textContent.trim() === 'Calculate CAP recommendation');
                          return button && !button.disabled;
                        }""",
                        timeout=20000,
                    )
                except Exception as exc:  # noqa: BLE001
                    record["cap_second_enable_wait_error"] = str(exc)
                if not page.get_by_role("button", name="Calculate CAP recommendation").is_disabled():
                    page.get_by_role("button", name="Calculate CAP recommendation").click()
                    try:
                        page.get_by_text("Recommended CAP units:").wait_for(timeout=30000)
                    except Exception as exc:  # noqa: BLE001
                        record["cap_second_recommend_wait_error"] = str(exc)
                    record["cap_after_lite_node"] = panel_metrics(page)
                    record["cap_after_lite_node_text"] = page.locator("#cap-planning-panel").inner_text()[:2200]
                    page.screenshot(path=str(SHOTS / "04-cap-after-nodes.png"))
            else:
                record["cap_recommend_skipped"] = "primary remained disabled after filling existing UI test-only inputs"
            page.locator("summary").filter(has_text="Advanced operations").click()
            page.wait_for_timeout(150)
            record["cap_advanced_visible"] = page.get_by_role("button", name="Calculate / rank").count() > 0 and page.get_by_role("button", name="Validate").count() > 0
            record["cap_inputs_open"] = page.evaluate(
                """() => {
                  const details = [...document.querySelectorAll('#cap-planning-panel details.cap-required-inputs')];
                  return details.map((item) => ({
                    summary: item.querySelector('summary')?.textContent,
                    open: item.open,
                    hasOperationMode: !!item.querySelector('#cap-field-operation_mode'),
                    hasCandidates: item.id === 'cap-section-candidates' || !!item.querySelector('#manual-cap-longitude'),
                  }));
                }"""
            )

            page.get_by_role("tab", name="Camera").click()
            page.wait_for_timeout(200)
            record["camera_pane"] = panel_metrics(page)
            record["camera_legend_text"] = page.locator(".camera-projection-legend").inner_text() if page.locator(".camera-projection-legend").count() else None
            page.screenshot(path=str(SHOTS / "05-camera.png"))

            for width, height in ((1920, 855), (1024, 768)):
                page.set_viewport_size({"width": width, "height": height})
                page.wait_for_timeout(400)
                record["viewports"].append({"width": width, "height": height, **panel_metrics(page)})
            page.set_viewport_size({"width": 1920, "height": 855})
            page.wait_for_timeout(200)
            page.get_by_role("tab", name="Lighting").click()
            page.wait_for_timeout(200)
            page.get_by_role("button", name="Collapse layer panel").click()
            page.wait_for_timeout(300)
            record["collapsed"] = panel_metrics(page)
            page.screenshot(path=str(SHOTS / "06-collapsed.png"))
            browser.close()

        record["hash_ok"] = record["kml_sha256"] == EXPECTED_SHA and record.get("import_sha256") in (EXPECTED_SHA, None)
        after = record.get("after_open") or {}
        record["switcher_default_lighting"] = any(item.get("selected") and item.get("label") == "Lighting" for item in after.get("switcher") or [])
        record["overflow_ok"] = all(not item.get("panelOverflowX") for item in record["viewports"])
        record["one_card"] = (record.get("second_card") or {}).get("count") == 1 and (record.get("reopened_first") or {}).get("count") == 1
        record["show_results_present"] = record.get("show_results_count", 0) >= 2
        record["reopened_first_is_area_1"] = "Calculation area 1" in ((record.get("reopened_first") or {}).get("text") or "")
        record["opened_second_is_area_2"] = "Calculation area 2" in ((record.get("opened_second") or {}).get("text") or "")
        dragged = record.get("first_card_dragged") or {}
        restored = record.get("reopened_first") or {}
        record["session_restore_delta"] = {
            "left": abs((restored.get("cssLeft") or 0) - (dragged.get("cssLeft") or 0)),
            "top": abs((restored.get("cssTop") or 0) - (dragged.get("cssTop") or 0)),
        }
        record["session_restore_ok"] = record["session_restore_delta"]["left"] <= 8 and record["session_restore_delta"]["top"] <= 8
        record["cap_primary_present"] = bool((record.get("cap_pane_initial") or {}).get("capPrimary"))
        record["cap_primary_disabled_before_profile"] = bool(((record.get("cap_pane_initial") or {}).get("capPrimary") or {}).get("disabled"))
        record["projection_boundary_ok"] = "flat local ground plane" in ((record.get("camera_pane") or {}).get("projectionBoundary") or "") and "not detection range" in ((record.get("camera_pane") or {}).get("projectionBoundary") or "")
        record["draft_preserved_across_discipline"] = bool((record.get("draft_preserved_all_disciplines") or {}).get("guideVisible"))
        record["cancel_kept_results"] = (record.get("after_cancel_draft") or {}).get("showResultsEnabled", 0) >= 2
        deleted = record.get("after_delete_area_2") or {}
        record["delete_closed_active_card"] = deleted.get("cardCount") == 0
        record["delete_kept_other_area"] = any("Calculation area 1" in str(row) for row in deleted.get("rows") or []) and deleted.get("showResultsEnabled") == 1
        restored_after_delete = record.get("area1_after_delete_other") or {}
        record["delete_kept_other_session"] = "Calculation area 1" in (restored_after_delete.get("text") or "") and restored_after_delete.get("count") == 1
        record["no_page_errors"] = not any(str(item).startswith("pageerror:") for item in record["errors"])
        record["no_new_camera_layer"] = not bool((record.get("camera_pane") or {}).get("extraCameraLayers"))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        summary = {k: record.get(k) for k in (
            "hash_ok", "switcher_default_lighting", "overflow_ok", "one_card",
            "show_results_present", "reopened_first_is_area_1", "opened_second_is_area_2", "session_restore_ok",
            "show_results_did_not_calculate", "cap_primary_present", "cap_primary_disabled_before_profile",
            "projection_boundary_ok", "draft_preserved_across_discipline", "cancel_kept_results",
            "delete_closed_active_card", "delete_kept_other_area", "delete_kept_other_session",
            "no_page_errors", "no_new_camera_layer",
        )}
        print(json.dumps(summary, indent=2))
        failed = [key for key, value in summary.items() if value is not True]
        print("FAILED_KEYS", failed)
        return 0 if not failed else 1
    except Exception as exc:  # noqa: BLE001
        record["errors"].append(str(exc))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(str(exc).encode("ascii", "replace").decode("ascii"))
        return 1
    finally:
        stop_proc(ui_proc)
        stop_proc(api_proc)


if __name__ == "__main__":
    raise SystemExit(main())
