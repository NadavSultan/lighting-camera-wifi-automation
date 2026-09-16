"""Independent Stage 2 browser QA against isolated production services."""
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
OUT = ROOT / "harness" / "verify" / "2026-09-16-stage2-bl-012-017-018-independent-qa-live.json"
SHOTS = ROOT / "harness" / "tmp" / "stage2-independent-qa" / "screenshots"
API = "http://127.0.0.1:8039"
UI = "http://127.0.0.1:3039/"
EXPECTED_SHA = "2f89f9f2be306c18221c643c98d5c1a9abdb6449aab8a77ea4b76b3694e8e328"


def wait_http(url: str, timeout: float = 90) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            if httpx.get(url, timeout=2).status_code < 500:
                return
        except Exception:
            pass
        time.sleep(0.4)
    raise RuntimeError(f"timeout waiting for {url}")


def metrics(page) -> dict:
    return page.evaluate("""() => {
      const panel=document.querySelector('aside.side-panel:not(.inspector)');
      const scroll=panel?.querySelector('.panel-scroll');
      const stage=document.querySelector('.map-stage')?.getBoundingClientRect();
      return {
        innerWidth, panelClientWidth:panel?.clientWidth, panelScrollWidth:panel?.scrollWidth,
        overflowX:panel ? panel.scrollWidth > panel.clientWidth + 1 : null,
        scrollOverflowX:scroll ? getComputedStyle(scroll).overflowX : null,
        tabs:[...document.querySelectorAll('.discipline-switcher button')].map(b=>({label:b.textContent.trim(),selected:b.getAttribute('aria-selected')==='true'})),
        stage:stage&&{left:stage.left,top:stage.top,width:stage.width,height:stage.height}
      };
    }""")


def card_metrics(page, vertex: dict) -> dict:
    return page.evaluate("""vertex => {
      const c=document.querySelector('.lighting-result-card'); const s=document.querySelector('.map-stage');
      if(!c||!s) return null; const r=c.getBoundingClientRect(), m=s.getBoundingClientRect();
      return {vertex, card:{left:r.left,top:r.top,right:r.right,bottom:r.bottom,width:r.width,height:r.height},
        stage:{left:m.left,top:m.top,right:m.right,bottom:m.bottom,width:m.width,height:m.height},
        offset:{x:r.left-vertex.x,y:r.top-vertex.y}, inside:r.left>=m.left-1&&r.top>=m.top-1&&r.right<=m.right+1&&r.bottom<=m.bottom+1,
        css:{left:parseFloat(c.style.left||'0'),top:parseFloat(c.style.top||'0')}, text:c.innerText};
    }""", vertex)


def draw(page, frac, name: str, close: bool = True) -> dict:
    page.get_by_role("tab", name="Lighting").click()
    page.get_by_role("button", name="Draw Calculation Area").click()
    canvas=page.locator('.maplibregl-canvas').first
    box=canvas.bounding_box()
    if not box: raise RuntimeError('map canvas missing')
    fx,fy=frac
    pts=[(max(.03,fx-.035),max(.05,fy-.045)),(min(.97,fx+.035),max(.05,fy-.045)),(fx,min(.95,fy+.045))]
    vertex=None
    for x,y in pts:
        page.evaluate("""p => document.querySelector('.maplibregl-canvas').dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:p.x,clientY:p.y}))""", {'x':box['x']+box['width']*x,'y':box['y']+box['height']*y})
        vertex={'x':box['x']+box['width']*x,'y':box['y']+box['height']*y}
    page.locator('.polygon-draft-guide').get_by_role('button',name='Finish').click()
    page.get_by_role('button',name='Calculate Lighting').click()
    page.locator('.lighting-result-card').wait_for(timeout=60000)
    page.wait_for_timeout(250)
    result=card_metrics(page,vertex)
    page.screenshot(path=str(SHOTS/f'{name}.png'))
    if close:
        page.get_by_role('button',name='Close lighting result').click()
    return result


def main() -> int:
    SHOTS.mkdir(parents=True,exist_ok=True)
    previous = json.loads(OUT.read_text(encoding='utf-8')) if OUT.exists() else {}
    record={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            'kml_sha256':hashlib.sha256(KML.read_bytes()).hexdigest(),'errors':[],
            'anchors': previous.get('anchors', {})}
    data_dir=Path(tempfile.mkdtemp(prefix='lcwa-stage2-qa-'))
    api_env=os.environ.copy(); api_env['LCWA_DATA_DIR']=str(data_dir)
    ui_env=os.environ.copy(); ui_env['NEXT_PUBLIC_API_URL']=API
    api=ui=None
    try:
        api=subprocess.Popen([str(ROOT/'.venv/Scripts/python.exe'),'-m','uvicorn','app.main:app','--host','127.0.0.1','--port','8039'],cwd=ROOT/'backend',env=api_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        ui=subprocess.Popen(['corepack','pnpm','exec','vinext','start','--host','127.0.0.1','--port','3039'],cwd=ROOT/'frontend',env=ui_env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
        wait_http(API+'/api/health'); wait_http(UI)
        record['health']=httpx.get(API+'/api/health').json(); record['isolated_store']=str(data_dir)
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
            page=browser.new_page(viewport={'width':1920,'height':855})
            page.goto(UI,wait_until='load',timeout=60000)
            page.locator('.discipline-switcher').wait_for(timeout=30000)
            page.set_input_files("input[accept='.kml,.kmz']",str(KML))
            page.locator('.count-card strong').filter(has_text='74').first.wait_for(timeout=60000)
            summaries=httpx.get(API+'/api/projects',timeout=10).json()
            project_id=summaries[0]['id']
            record['after_import']=metrics(page)
            record['viewports']=[]
            for w,h in ((1920,855),(1024,768)):
                page.set_viewport_size({'width':w,'height':h}); page.wait_for_timeout(250)
                record['viewports'].append(metrics(page))
            page.set_viewport_size({'width':1920,'height':855}); page.wait_for_timeout(250)
            page.get_by_role('tab',name='CAP').click(); page.wait_for_timeout(150)
            record['cap']={'metrics':metrics(page),'panelVisible':page.locator('#cap-planning-panel').is_visible(),
                           'blockerText':page.locator('#cap-planning-panel').inner_text()[:1200]}
            page.get_by_role('tab',name='Lighting').click()
            page.get_by_role('button',name='Draw Calculation Area').click()
            canvas=page.locator('.maplibregl-canvas').first; box=canvas.bounding_box()
            for x in (.35,.45): page.evaluate("""p => document.querySelector('.maplibregl-canvas').dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:p.x,clientY:p.y}))""",{'x':box['x']+box['width']*x,'y':box['y']+box['height']*.4})
            before=page.locator('.polygon-draft-guide').inner_text()
            page.get_by_role('tab',name='Camera').click(); page.get_by_role('tab',name='Wi-Fi').click(); page.get_by_role('tab',name='Lighting').click()
            record['draft_preserved']={'before':before,'after':page.locator('.polygon-draft-guide').inner_text()}
            page.locator('.polygon-draft-guide').get_by_role('button',name='Cancel').click()
            for name,frac in {'top_left':(.08,.12),'top_right':(.92,.12),'bottom_left':(.08,.88),'bottom_right':(.86,.80),'center':(.5,.5)}.items():
                if name not in record['anchors']:
                    record['anchors'][name]=draw(page,frac,name)
            center=draw(page,(.5,.5),'center-interaction',close=False)
            record['interaction_center_initial']=center
            page.wait_for_timeout(1500)
            json_before_drag=httpx.get(API+f'/api/projects/{project_id}',timeout=10).json()
            header=page.locator('.lighting-result-card-header'); hb=header.bounding_box()
            page.mouse.move(hb['x']+40,hb['y']+20); page.mouse.down(); page.mouse.move(hb['x']+170,hb['y']+90,steps=5); page.mouse.up(); page.wait_for_timeout(150)
            record['dragged']=card_metrics(page,center['vertex'])
            json_after_drag=httpx.get(API+f'/api/projects/{project_id}',timeout=10).json()
            serialized_after=json.dumps(json_after_drag,sort_keys=True)
            record['session_only_drag']={'project_json_equal_before_after_drag':json_before_drag==json_after_drag,
                'project_json_equal_excluding_async_camera_geometry':{k:v for k,v in json_before_drag.items() if k!='camera_geometry'}=={k:v for k,v in json_after_drag.items() if k!='camera_geometry'},
                'changed_top_level_keys':[key for key in sorted(set(json_before_drag)|set(json_after_drag)) if json_before_drag.get(key)!=json_after_drag.get(key)],
                'forbidden_position_keys_present':any(key in serialized_after for key in ('draggedPosition','dragged_position','cardPosition','card_position'))}
            page.get_by_role('button',name='Reset position').click(); page.wait_for_timeout(150)
            record['reset']=card_metrics(page,center['vertex'])
            page.screenshot(path=str(SHOTS/'drag-reset.png'))
            canvas=page.locator('.maplibregl-canvas').first; cb=canvas.bounding_box()
            before_move=record['reset']['card']
            page.mouse.move(cb['x']+cb['width']*.6,cb['y']+cb['height']*.6); page.mouse.down(); page.mouse.move(cb['x']+cb['width']*.5,cb['y']+cb['height']*.5,steps=5); page.mouse.up(); page.mouse.wheel(0,-500); page.wait_for_timeout(500)
            record['after_pan_zoom']={'before':before_move,'after':card_metrics(page,center['vertex'])['card']}
            page.get_by_role('button',name='Collapse layer panel').click(); page.wait_for_timeout(200)
            record['collapsed']={'metrics':metrics(page),'card':card_metrics(page,center['vertex'])}
            page.get_by_role('button',name='Expand Layers').click(); page.wait_for_timeout(150)
            record['restored']={'metrics':metrics(page),'card':card_metrics(page,center['vertex'])}
            record['report_toolbar']=page.get_by_role('button',name='Report Package',exact=True).is_visible()
            record['project_json']=httpx.get(API+'/api/projects').status_code
            record['lux_dom']={'card':page.locator('.lighting-result-card').inner_text()[:800]}
            browser.close()
        record['hash_ok']=record['kml_sha256']==EXPECTED_SHA
        record['bl012_matrix_pass']={
            'five_positions_inside':all(record['anchors'].get(k,{}).get('inside') for k in ('top_left','top_right','bottom_left','bottom_right','center')),
            'center_offset_about_12px':abs(record['anchors']['center']['offset']['x']-12)<2 and abs(record['anchors']['center']['offset']['y']-12)<2,
            'drag_moved_card':record['dragged']['card']['left'] != record['interaction_center_initial']['card']['left'] or record['dragged']['card']['top'] != record['interaction_center_initial']['card']['top'],
            'reset_returned_to_anchor':abs(record['reset']['card']['left']-record['interaction_center_initial']['card']['left'])<2 and abs(record['reset']['card']['top']-record['interaction_center_initial']['card']['top'])<2,
            'pan_zoom_moved_card':record['after_pan_zoom']['before'] != record['after_pan_zoom']['after'],
            'collapse_restore_worked':record['collapsed']['metrics']['stage']['left'] < record['restored']['metrics']['stage']['left'],
            'drag_session_only':not record['session_only_drag']['forbidden_position_keys_present'] and record['session_only_drag']['project_json_equal_excluding_async_camera_geometry'],
        }
        OUT.write_text(json.dumps(record,indent=2),encoding='utf-8')
        print(json.dumps({'out':str(OUT),'hash_ok':record['hash_ok'],'viewports':record['viewports'],'anchors':{k:{'offset':v['offset'],'inside':v['inside']} for k,v in record['anchors'].items()},'draft':record['draft_preserved'],'report_toolbar':record['report_toolbar']},indent=2))
        return 0
    except Exception as exc:
        record['errors'].append(repr(exc)); OUT.write_text(json.dumps(record,indent=2),encoding='utf-8'); print(ascii(exc)); return 1
    finally:
        for proc in (ui,api):
            if proc:
                proc.terminate()
                try: proc.wait(timeout=8)
                except Exception: proc.kill()


if __name__=='__main__': raise SystemExit(main())
