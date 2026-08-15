# Lighting Camera WiFi Automation

Local Phase 3 map-centred engineering application for importing customer KML/KMZ pole layouts, preserving source coordinates and metadata, managing fixture/IES/camera catalogs, assigning fixed-mount SMART cameras, calculating flat-ground FOV/overlap/priority intersections, saving/reopening project JSON, and exporting updated KML.

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
..\.venv\Scripts\python.exe -m pytest

Set-Location ..\frontend
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build
```

## Scope and safety

Existing-pole mode remains mandatory. No proposed poles are created and no customer coordinates are moved, corrected, or overwritten. Phase 3 renders geometric camera FOV, overlap, and priority areas only. It does not calculate Wi-Fi coverage, illuminance, CAP recommendations, analytics suitability, or automatic pole placement.
