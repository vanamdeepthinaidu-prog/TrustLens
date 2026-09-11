# VisionTrust AI (TrustLens)
## SIH26228 — Trustworthy Computer Vision Integrity Assurance for Data, Models, and Inference Outputs in Multi-Contributor Pipelines

**Organization:** Ministry of Defence  
**Department:** Indian Army / DGIS  
**Category:** Software | **Theme:** Blockchain & Cybersecurity  

---

## 1. Overview
VisionTrust AI is an evidence-based, offline-first AI assurance platform designed to verify whether computer-vision datasets, trained models, and inference outputs can be trusted in mission-critical environments.

The platform provides multi-layer defense across:
- **Layer A — Dataset Integrity**: Perceptual and cryptographic hashing, duplicate clustering, out-of-distribution (OOD) sample detection, and label consistency audits.
- **Layer B — Model Integrity**: Architectural fingerprinting, parameter digests, model substitution detection against reference weights, and trigger sensitivity checks.
- **Layer C — Inference & Provenance Integrity**: Cryptographic binding of `input_hash`, `model_hash`, `preprocessing_hash`, `result_hash`, `nonce`, `sequence`, and `timestamp` into tamper-evident hash-chained provenance logs with replay detection.
- **Layer D — Distribution Shift**: Statistical and embedding-level distribution monitoring to detect environmental drift and domain shifts.
- **Layer E — Trust & Assurance Engine**: Transparent scoring (30% Dataset, 30% Model, 25% Inference, 15% Distribution) delivering a clear analyst disposition: `ACCEPT`, `REVIEW`, or `QUARANTINE`.

---

## 2. Air-Gapped / Offline-First Guarantee
VisionTrust AI is architected strictly for air-gapped deployment with zero external API dependencies (no OpenAI, Gemini, Groq, or cloud storage calls). All hashing, model evaluation, and ledger operations execute locally.

---

## 3. Team Member Division & Responsibilities
- **M1 (Core Platform & Ledger Engineer - Lead):** Monorepo skeleton, FastAPI bootstrap, SQLite/SQLAlchemy schemas, deterministic hashing engine, tamper-evident hash-chain ledger, API contracts, Docker setup, and local RBAC auth.
- **M2 (CV / Dataset Integrity Engineer):** Image hashing, duplicate detection, OOD anomaly detector, and label consistency.
- **M3 (Model & Inference Security Engineer):** Local CV inference, model fingerprinting, substitution check, provenance binding, and tamper/replay detection.
- **M4 (Risk Engine & Attack Simulator Engineer):** Distribution shift analyzer, 9-attack simulation lab, 18-step demo orchestrator, and automated PDF/JSON report generation.
- **M5 (Frontend / Dashboard Engineer):** React security console, SOC-style dark dashboard, pipeline visualizer, verification panel, and evidence explorer.

---

## 4. Quick Start (Local)

### Prerequisites
- Python 3.10+
- Node.js 18+ (for frontend)
- Docker & Docker Compose (optional for containerized run)

### Backend Setup
```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Documentation (Swagger UI): `http://localhost:8000/docs`
- Health & Offline Status: `http://localhost:8000/api/system/status`

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Dashboard will be available at `http://localhost:5173`.

### Docker Compose
```bash
docker compose up --build
```
Runs frontend on port `5173` and backend on port `8000`.

---

## 5. Running Automated Verification
```bash
cd backend
pytest tests/ -v
```
Verifies deterministic file and directory hashing, canonical JSON digests, ledger block generation, hash-chain integrity, and tamper detection.
