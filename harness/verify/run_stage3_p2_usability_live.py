"""Stage 3 P2 live checks against an isolated production UI and isolated FastAPI store."""
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
OUT = ROOT / "harness" / "verify" / "2026-09-16-stage3-p2-usability-live.json"
API_PORT = 8042
UI_PORT = 3046
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
            httpx.get(url, timeout=2.0)
            return
        except Exception as exc:  # noqa: BLE001
            last = exc
            time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}: {last}")


def panel_metrics(page) -> dict:
    return page.evaluate(
        """() => {
          const panel = document.querySelector('aside.side-panel:not(.inspector)');
          const scroll = panel && panel.querySelector('.panel-scroll');
          const switcher = [...document.querySelectorAll('.discipline-switcher button')].map((button) => ({
            label: button.textContent.trim(),
            selected: button.getAttribute('aria-selected') === 'true',
          }));
          const errors = window.__stage3ConsoleErrors || [];
          return {
            innerWidth: window.innerWidth,
            panelOverflowX: panel ? panel.scrollWidth > panel.clientWidth + 1 : null,
            scrollOverflowXStyle: scroll ? getComputedStyle(scroll).overflowX : null,
            switcher,
            showResultsCount: [...document.querySelectorAll('button')].filter((b) => b.textContent.trim() === 'Show results').length,
            showResultsEnabled: [...document.querySelectorAll('button')].filter((b) => b.textContent.trim() === 'Show results' && !b.disabled).length,
            lightingCardCount: document.querySelectorAll('.lighting-result-card').length,
            capPrimary: (() => {
              const button = [...document.querySelectorAll('button')].find((item) => item.textContent.trim() === 'Calculate CAP recommendation');
              return button ? { disabled: button.disabled, visible: button.offsetParent !== null } : null;
            })(),
            capNotCalculated: [...document.querySelectorAll('p')].some((p) => p.textContent.includes('No current CAP result')),
            capInputsDetails: !!document.querySelector('#cap-planning-panel details.cap-required-inputs'),
            projectionBoundary: [...document.querySelectorAll('.camera-projection-legend')].map((el) => el.innerText).join('\\n'),
            consoleErrors: errors,
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
    last_vertex = None
    for x_frac, y_frac in offsets:
        x = box["x"] + box["width"] * x_frac
        y = box["y"] + box["height"] * y_frac
        page.mouse.click(x, y)
        page.wait_for_timeout(300)
        last_vertex = {"x": x, "y": y}
    return last_vertex


def main() -> int:
    kml_bytes = KML.read_bytes()
    record: dict = {
        "kml_sha256": hashlib.sha256(kml_bytes).hexdigest(),
        "expected_sha256": EXPECTED_SHA,
        "api": API,
        "ui": UI,
        "errors": [],
        "viewports": [],
    }
    data_dir = Path(tempfile.mkdtemp(prefix="lcwa-stage3-p2-"))
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
        ui_proc = subprocess.Popen(
            ["corepack", "pnpm", "exec", "vinext", "start", "--port", str(UI_PORT)],
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
            page.add_init_script("window.__stage3ConsoleErrors = []; window.addEventListener('error', (e) => window.__stage3ConsoleErrors.push(String(e.message || e.error)));")
            page.on("pageerror", lambda exc: record["errors"].append(f"pageerror:{exc}"))
            page.goto(UI, wait_until="load", timeout=60000)
            page.locator(".discipline-switcher").wait_for(timeout=30000)
            page.set_input_files("input[accept='.kml,.kmz']", str(KML))
            page.locator(".count-card strong").filter(has_text="74").first.wait_for(timeout=60000)
            record["pole_count"] = 74
            projects = httpx.get(f"{API}/api/projects", timeout=10.0).json()
            record["api_projects"] = projects if isinstance(projects, list) else list((projects or {}).keys()) if isinstance(projects, dict) else projects
            record["after_open"] = panel_metrics(page)

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            draw_triangle(page, [(0.46, 0.46), (0.58, 0.46), (0.58, 0.58)])
            record["first_draft_after_clicks"] = page.locator(".polygon-draft-guide").inner_text()
            page.locator(".polygon-draft-guide span").filter(has_text="3 vertices").wait_for(timeout=15000)
            page.locator(".polygon-draft-guide").get_by_role("button", name="Finish").click()
            page.wait_for_timeout(400)
            page.get_by_role("button", name="Calculate Lighting").click()
            page.locator(".lighting-result-card").wait_for(timeout=60000)
            record["first_card"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  if (!card) return null;
                  const rect = card.getBoundingClientRect();
                  return { left: rect.left, top: rect.top, cssLeft: parseFloat(card.style.left || '0'), cssTop: parseFloat(card.style.top || '0'), text: card.innerText.slice(0, 240), count: document.querySelectorAll('.lighting-result-card').length };
                }"""
            )
            header = page.locator(".lighting-result-card-header")
            box = header.bounding_box()
            if box:
                page.mouse.move(box["x"] + 20, box["y"] + 8)
                page.mouse.down()
                page.mouse.move(box["x"] + 90, box["y"] + 70)
                page.mouse.up()
            page.wait_for_timeout(200)
            record["first_card_dragged"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  if (!card) return null;
                  return { cssLeft: parseFloat(card.style.left || '0'), cssTop: parseFloat(card.style.top || '0') };
                }"""
            )

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            record["draft_during_second"] = panel_metrics(page)
            page.get_by_role("tab", name="Camera").click()
            page.wait_for_timeout(200)
            record["draft_after_camera_switch"] = {
                "guideVisible": page.locator(".polygon-draft-guide").count() > 0 and page.locator(".polygon-draft-guide").first.is_visible(),
                "vertexText": page.locator(".polygon-draft-guide").inner_text() if page.locator(".polygon-draft-guide").count() else None,
            }
            page.get_by_role("tab", name="Lighting").click()
            page.wait_for_timeout(200)
            draw_triangle(page, [(0.56, 0.38), (0.70, 0.38), (0.63, 0.52)])
            page.locator(".polygon-draft-guide span").filter(has_text="3 vertices").wait_for(timeout=8000)
            page.locator(".polygon-draft-guide").get_by_role("button", name="Finish").click()
            page.wait_for_timeout(400)
            page.get_by_role("button", name="Calculate Lighting").click()
            page.locator(".lighting-result-card").wait_for(timeout=60000)
            record["second_card"] = page.evaluate(
                """() => {
                  const cards = [...document.querySelectorAll('.lighting-result-card')];
                  return { count: cards.length, text: cards[0] ? cards[0].innerText.slice(0, 240) : null, cssLeft: cards[0] ? parseFloat(cards[0].style.left || '0') : null };
                }"""
            )
            show_buttons = page.get_by_role("button", name="Show results")
            record["show_results_count"] = show_buttons.count()
            page.locator(".calculation-row").filter(has_text="Calculation area 2").get_by_role("button", name="Show results").click()
            page.wait_for_timeout(400)
            record["opened_second"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  if (!card) return null;
                  return { count: document.querySelectorAll('.lighting-result-card').length, cssLeft: parseFloat(card.style.left || '0'), cssTop: parseFloat(card.style.top || '0'), text: card.innerText.slice(0, 240) };
                }"""
            )
            page.locator(".calculation-row").filter(has_text="Calculation area 1").get_by_role("button", name="Show results").click()
            page.wait_for_timeout(400)
            record["reopened_first"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  if (!card) return null;
                  return { count: document.querySelectorAll('.lighting-result-card').length, cssLeft: parseFloat(card.style.left || '0'), cssTop: parseFloat(card.style.top || '0'), text: card.innerText.slice(0, 240) };
                }"""
            )

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            page.locator(".polygon-draft-guide").get_by_role("button", name="Cancel").click()
            page.wait_for_timeout(200)
            record["after_cancel_draft"] = panel_metrics(page)
            page.locator(".calculation-row").filter(has_text="Calculation area 2").get_by_role("button", name="Delete").click()
            page.wait_for_timeout(300)
            record["after_delete_area_2"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  return {
                    rows: [...document.querySelectorAll('.calculation-row strong')].map((el) => el.textContent),
                    showResultsEnabled: [...document.querySelectorAll('button')].filter((b) => b.textContent.trim() === 'Show results' && !b.disabled).length,
                    cardText: card ? card.innerText.slice(0, 80) : null,
                    cardCount: document.querySelectorAll('.lighting-result-card').length,
                  };
                }"""
            )

            page.get_by_role("tab", name="CAP").click()
            page.wait_for_timeout(300)
            record["cap_pane"] = panel_metrics(page)
            page.locator("summary").filter(has_text="Required CAP inputs").click()
            page.wait_for_timeout(150)
            record["cap_inputs_open"] = page.evaluate(
                """() => {
                  const details = [...document.querySelectorAll('#cap-planning-panel details.cap-required-inputs')];
                  return details.map((item) => ({ summary: item.querySelector('summary')?.textContent, open: item.open, hasOperationMode: !!item.querySelector('#cap-field-operation_mode'), hasCandidates: item.id === 'cap-section-candidates' || !!item.querySelector('#manual-cap-longitude') }));
                }"""
            )

            page.get_by_role("tab", name="Camera").click()
            page.wait_for_timeout(200)
            record["camera_pane"] = panel_metrics(page)

            for width, height in ((1920, 855), (1024, 768)):
                page.set_viewport_size({"width": width, "height": height})
                page.wait_for_timeout(400)
                record["viewports"].append({"width": width, "height": height, **panel_metrics(page)})

            page.get_by_role("tab", name="Lighting").click()
            page.wait_for_timeout(200)
            page.get_by_role("button", name="Collapse layer panel").click()
            page.wait_for_timeout(300)
            record["collapsed"] = panel_metrics(page)
            browser.close()

        record["hash_ok"] = record["kml_sha256"] == EXPECTED_SHA
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
        record["cap_primary_present"] = bool((record.get("cap_pane") or {}).get("capPrimary"))
        record["cap_primary_disabled_before_profile"] = bool(((record.get("cap_pane") or {}).get("capPrimary") or {}).get("disabled"))
        record["projection_boundary_ok"] = "flat local ground plane" in ((record.get("camera_pane") or {}).get("projectionBoundary") or "")
        record["draft_preserved_across_discipline"] = bool((record.get("draft_after_camera_switch") or {}).get("guideVisible"))
        record["cancel_kept_results"] = (record.get("after_cancel_draft") or {}).get("showResultsEnabled", 0) >= 2
        record["delete_kept_other_card"] = "Calculation area 1" in ((record.get("after_delete_area_2") or {}).get("cardText") or "") and (record.get("after_delete_area_2") or {}).get("cardCount") == 1
        record["no_page_errors"] = not any(item.startswith("pageerror:") for item in record["errors"])
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        summary = {k: record.get(k) for k in (
            "hash_ok", "switcher_default_lighting", "overflow_ok", "one_card",
            "show_results_present", "reopened_first_is_area_1", "opened_second_is_area_2", "session_restore_ok",
            "cap_primary_present", "cap_primary_disabled_before_profile",
            "projection_boundary_ok", "draft_preserved_across_discipline", "cancel_kept_results", "delete_kept_other_card", "no_page_errors",
        )}
        print(json.dumps(summary, indent=2))
        failed = [key for key, value in summary.items() if value is not True]
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
