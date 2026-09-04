# Lighting Camera WiFi Automation

Local Phase 7 map-centred engineering application for importing customer KML/KMZ pole layouts, preserving source coordinates and metadata, managing fixture/IES/camera catalogs, calculating fixed-mount camera geometry, simplified direct horizontal illuminance, conceptual Wi-Fi geometry, CAP / JNET1 distance-graph planning, saving/reopening project JSON, exporting updated KML, and generating a deterministic multi-format report package for engineering review.

## Run locally

Prerequisites: Python 3.12+ and Node.js 22+.

Backend (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".\backend[dev]"
Set-Location .\backend
..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Frontend, in another terminal:

```powershell
Set-Location .\frontend
pnpm install
pnpm run dev
```

Open `http://127.0.0.1:3000`. The frontend connects to `http://127.0.0.1:8000` by default; set `NEXT_PUBLIC_API_URL` before starting it to use another local API address.

## Verify

```powershell
Set-Location .\backend
..\.venv\Scripts\python.exe -m pytest --basetemp ..\harness\tmp\pytest\run

Set-Location ..\frontend
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build
```

## Scope and safety

Existing-pole mode remains mandatory. No proposed poles are created and no customer coordinates are moved, corrected, or overwritten. Phase 4 lighting is a simplified direct-light Type C model and is not independently validated against AGi32 or another professional reference tool. Phase 5 Wi-Fi and Phase 6 CAP outputs are conceptual graph/geometry planning only—not verified RF coverage, performance, compliance, or installation validation. Phase 7 report packages are engineering-review artifacts with explicit limitations; they do not recalculate results or claim professional/RF/compliance approval.
