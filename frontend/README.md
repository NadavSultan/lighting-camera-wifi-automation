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

The D1, authentication, and deployment-compatible worker files are inherited scaffold seams and are not used by the local Phase 1 product. Phase 1 state is persisted by FastAPI on the local filesystem.
