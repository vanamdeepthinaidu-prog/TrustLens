# TrustLens Frontend — Member 5

React + Vite + Tailwind dashboard for the TrustLens AI Assurance Platform (SIH26228).

## Quick Start

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173
```

Production build:
```bash
npm run build
```

## Environment

Copy `.env` and set:
```
VITE_API_BASE_URL=http://localhost:8000   # local
# or
VITE_API_BASE_URL=https://your-render-app.onrender.com  # hosted
```

## Pages

| Route | Section | Description |
|-------|---------|-------------|
| `/dashboard` | §26 | Trust score hero, 4 component cards, 4 charts |
| `/dataset-integrity` | §9–11 | Duplicates, OOD, label check, verify tab |
| `/model-integrity` | §12–13 | Fingerprint, hash verification, trigger sensitivity |
| `/inference-verification` | §14–17 | Provenance record, tamper test, replay detection |
| `/distribution-shift` | §19 | Shift score, feature comparison, embedding distance |
| `/security-lab` | §24 | 9 attack simulations + results table |
| `/evidence-explorer` | §29 | Filterable evidence list + detail drawer |
| `/audit-trail` | §30 | Hash-linked timeline |
| `/assurance-reports` | §31 | JSON + PDF report generation |
| `/system-information` | §32 | Config, detection coverage, roles |

## Key Features

- **Pipeline Visualizer** (§27): DATASET→MODEL→INFERENCE→OUTPUT node graph with status per node
- **Verification Panel** (§28): Client-side SHA-256 via Web Crypto API, drag-and-drop
- **Demo Orchestrator** (§34): 18-step animated progress modal with phase breakdown
- **Evidence Explorer** (§29): ACCEPT / REVIEW / QUARANTINE disposition workflow

## Tech Stack

- React 18 + React Router v6
- Vite 8 + @tailwindcss/vite
- Recharts (all dashboard charts)
- Lucide React (icons)
- axios (API calls, proxied to :8000)

## Wiring real endpoints

All pages import mock data from `src/mock/mockData.js`.
Swap each mock import for a real `client.js` API call as teammates' routes land.
The Vite proxy in `vite.config.js` forwards `/api/*` to `http://localhost:8000`.
