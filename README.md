# Lighting Camera WiFi Automation

Local Phase 1 map-centred engineering application for importing customer KML/KMZ pole layouts, preserving source coordinates and metadata, assigning LITE/WIFI/SMART fixture types, recording pole height/status/notes edits, saving/reopening project JSON, and exporting updated KML.

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

Existing-pole mode is the only Phase 1 operating mode. No proposed poles are created and no customer coordinates are moved, corrected, or overwritten. Camera geometry, Wi-Fi analysis, IES calculations, and CAP recommendation are gated behind later reviewed phases.
