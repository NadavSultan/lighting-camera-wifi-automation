"""Stage 2 live checks for BL-012 / BL-017 / BL-018 against the current frontend dist."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import httpx
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[2]
KML = ROOT / "Input" / "Miracle_Mile_Lighting_Poles.kml"
EXPECTED_SHA = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"
OUT = ROOT / "harness" / "verify" / "2026-09-08-stage2-bl-012-017-018-live.json"
API = "http://127.0.0.1:8000"
UI = "http://127.0.0.1:3012/"


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
          const lightingVisible = !document.querySelector('h3') ? false : [...document.querySelectorAll('h3')].some((h) => h.textContent.includes('Lighting calculation areas') && h.offsetParent !== null);
          const capVisible = !!(document.getElementById('cap-planning-panel') && document.getElementById('cap-planning-panel').offsetParent);
          return {
            innerWidth: window.innerWidth,
            panelClientWidth: panel && panel.clientWidth,
            panelScrollWidth: panel && panel.scrollWidth,
            panelOverflowX: panel ? panel.scrollWidth > panel.clientWidth + 1 : null,
            scrollOverflowXStyle: scroll ? getComputedStyle(scroll).overflowX : null,
            scrollClientWidth: scroll && scroll.clientWidth,
            scrollScrollWidth: scroll && scroll.scrollWidth,
            contentFits: scroll ? scroll.scrollWidth <= scroll.clientWidth + 1 : null,
            switcher,
            lightingVisible,
            capVisible,
            mapStage: (() => {
              const stage = document.querySelector('.map-stage');
              const rect = stage && stage.getBoundingClientRect();
              return rect ? { left: rect.left, top: rect.top, width: rect.width, height: rect.height } : null;
            })(),
          };
        }"""
    )


def main() -> int:
    kml_bytes = KML.read_bytes()
    record: dict = {
        "kml_sha256": hashlib.sha256(kml_bytes).hexdigest(),
        "expected_sha256": EXPECTED_SHA,
        "errors": [],
        "viewports": [],
    }
    env = os.environ.copy()
    frontend = None
    try:
        try:
            wait_http(UI, timeout=5.0)
            record["frontend_mode"] = "reused-3012"
        except Exception:
            frontend = subprocess.Popen(
                ["corepack", "pnpm", "exec", "vinext", "start", "--port", "3012"],
                cwd=str(ROOT / "frontend"),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                shell=True,
            )
            wait_http(UI)
            record["frontend_mode"] = "started-3012"
        wait_http(f"{API}/api/health")
        record["live_health"] = httpx.get(f"{API}/api/health", timeout=5.0).json()
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 1920, "height": 855})
            page.goto(UI, wait_until="load", timeout=60000)
            page.locator(".discipline-switcher").wait_for(timeout=30000)
            page.set_input_files("input[accept='.kml,.kmz']", str(KML))
            try:
                page.locator(".count-card strong").filter(has_text="74").first.wait_for(timeout=60000)
            except Exception:
                record["import_debug"] = {
                    "toast": page.locator(".toast").inner_text() if page.locator(".toast").count() else None,
                    "status": page.locator(".status-message").inner_text() if page.locator(".status-message").count() else None,
                    "title": page.title(),
                }
                raise
            record["pole_count"] = 74
            record["after_open"] = panel_metrics(page)

            for width, height in ((1920, 855), (1024, 768)):
                page.set_viewport_size({"width": width, "height": height})
                page.wait_for_timeout(400)
                record["viewports"].append({"width": width, "height": height, **panel_metrics(page)})

            page.set_viewport_size({"width": 1920, "height": 855})
            page.wait_for_timeout(300)
            page.get_by_role("tab", name="CAP").click()
            page.wait_for_timeout(200)
            record["cap_pane"] = panel_metrics(page)
            page.get_by_role("tab", name="Lighting").click()
            page.wait_for_timeout(200)
            record["lighting_pane"] = panel_metrics(page)

            page.get_by_role("button", name="Draw Calculation Area").click()
            page.locator(".polygon-draft-guide span").filter(has_text="0 vertices").wait_for(timeout=10000)
            page.wait_for_timeout(500)
            canvas = page.locator(".maplibregl-canvas").first
            canvas.wait_for(state="visible")
            box = canvas.bounding_box()
            if not box:
                raise RuntimeError("map canvas missing")
            clicks = [
                (box["width"] * 0.38, box["height"] * 0.42),
                (box["width"] * 0.52, box["height"] * 0.42),
                (box["width"] * 0.45, box["height"] * 0.56),
            ]
            last_vertex = None
            for x, y in clicks:
                canvas.click(position={"x": x, "y": y})
                page.wait_for_timeout(250)
                last_vertex = {"x": box["x"] + x, "y": box["y"] + y}
            page.locator(".polygon-draft-guide span").filter(has_text="3 vertices").wait_for(timeout=8000)
            page.locator(".polygon-draft-guide").get_by_role("button", name="Finish").click()
            page.wait_for_timeout(400)
            page.get_by_role("button", name="Calculate Lighting").click()
            page.locator(".lighting-result-card").wait_for(timeout=60000)
            record["card"] = page.evaluate(
                """(lastVertex) => {
                  const card = document.querySelector('.lighting-result-card');
                  const stage = document.querySelector('.map-stage');
                  if (!card || !stage) return null;
                  const cardRect = card.getBoundingClientRect();
                  const stageRect = stage.getBoundingClientRect();
                  const text = card.innerText;
                  return {
                    lastVertex,
                    card: { left: cardRect.left, top: cardRect.top, width: cardRect.width, height: cardRect.height },
                    stage: { left: stageRect.left, top: stageRect.top, width: stageRect.width, height: stageRect.height },
                    offsetFromVertex: { x: cardRect.left - lastVertex.x, y: cardRect.top - lastVertex.y },
                    cssLeft: parseFloat(card.style.left || '0'),
                    cssTop: parseFloat(card.style.top || '0'),
                    textSample: text.slice(0, 400),
                    hasLt001: text.includes('<0.01'),
                    hasZeroLx: /\\b0\\.00 lx\\b/.test(text),
                    hasEmDash: text.includes('—'),
                  };
                }""",
                last_vertex,
            )
            page.get_by_role("button", name="Reset position").click()
            page.wait_for_timeout(200)
            record["card_after_reset"] = page.evaluate(
                """() => {
                  const card = document.querySelector('.lighting-result-card');
                  if (!card) return null;
                  const cardRect = card.getBoundingClientRect();
                  return { left: cardRect.left, top: cardRect.top, cssLeft: parseFloat(card.style.left || '0'), cssTop: parseFloat(card.style.top || '0') };
                }"""
            )
            page.get_by_role("button", name="Collapse layer panel").click()
            page.wait_for_timeout(300)
            record["collapsed"] = panel_metrics(page)
            browser.close()
        record["hash_ok"] = record["kml_sha256"] == EXPECTED_SHA
        after = record.get("after_open") or {}
        lighting_selected = any(item.get("selected") and item.get("label") == "Lighting" for item in after.get("switcher") or [])
        record["switcher_default_lighting"] = lighting_selected
        record["overflow_ok"] = all(not item.get("panelOverflowX") for item in record["viewports"])
        card = record.get("card") or {}
        offset = card.get("offsetFromVertex") or {}
        record["card_not_clamped_to_left_margin"] = (card.get("cssLeft") or 0) > 20
        record["stage_not_page_origin"] = bool(card.get("stage") and (card["stage"]["left"] > 1 or card["stage"]["top"] > 1))
        record["card_offset"] = offset
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(json.dumps({k: record[k] for k in ("hash_ok", "switcher_default_lighting", "overflow_ok", "card_not_clamped_to_left_margin", "stage_not_page_origin", "card_offset") if k in record}, indent=2))
        return 0
    except Exception as exc:  # noqa: BLE001
        record["errors"].append(str(exc))
        OUT.write_text(json.dumps(record, indent=2), encoding="utf-8")
        print(exc)
        return 1
    finally:
        if frontend is not None:
            frontend.terminate()
            try:
                frontend.wait(timeout=8)
            except Exception:  # noqa: BLE001
                frontend.kill()


if __name__ == "__main__":
    raise SystemExit(main())
