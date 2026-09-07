# LCWA frontend

React/TypeScript map workspace for Lighting Camera WiFi Automation Phase 1, built with Vinext and MapLibre.

## Commands

```powershell
pnpm install
pnpm run dev
pnpm run test
pnpm run typecheck
pnpm run lint
pnpm run build
```

The development server opens at `http://localhost:3000/` and expects the local FastAPI service at `http://127.0.0.1:8000`. Set `NEXT_PUBLIC_API_URL` before starting the frontend to change the API origin.

Map background: **Standard** is the existing OpenStreetMap raster. **Satellite** is session-only and uses a public HTTPS XYZ template from the environment. Copy `frontend/.env.example` to a local env file and set the `NEXT_PUBLIC_SATELLITE_*` names; do not put the provider, mosaic year, or tile URL in project JSON. If satellite config is missing or tiles fail, the standard map stays available and the UI offers **Use standard map**. The first authorized satellite backend is the free non-commercial EOX public WMTS; the product labels remain Standard vs Satellite so that backend can be replaced later without a schema change.

The D1, authentication, and deployment-compatible worker files are inherited scaffold seams and are not used by the local Phase 1 product. Phase 1 state is persisted by FastAPI on the local filesystem.
