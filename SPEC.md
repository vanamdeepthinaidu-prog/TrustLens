You are a senior AI/ML engineer, cybersecurity engineer, computer vision engineer,
backend engineer, frontend engineer, and product architect.

Build a complete, production-quality Smart India Hackathon 2026 software solution
for the following problem statement:

============================================================
SIH26228
TRUSTWORTHY COMPUTER VISION INTEGRITY ASSURANCE FOR DATA,
MODELS AND INFERENCE OUTPUTS IN MULTI-CONTRIBUTOR PIPELINES
============================================================

Organization:
Ministry of Defence

Department:
Indian Army / DGIS

Category:
Software

Theme:
Blockchain & Cybersecurity

IMPORTANT:
This is NOT a simple image classification project.

The goal is to build an offline/air-gapped AI assurance platform that determines
whether computer-vision datasets, trained models, and inference outputs can be
trusted.

The system must identify suspicious behavior, provide evidence for its decisions,
calculate risk/severity, maintain tamper-evident provenance, and give an analyst
a clear final disposition.

Possible dispositions:
1. ACCEPT
2. REVIEW
3. QUARANTINE

The platform must clearly communicate confidence, evidence, limitations,
assumptions, and unsupported attack classes.

============================================================
1. CORE PRODUCT
============================================================

Create a platform called:

"VisionTrust AI"

Tagline:

"Evidence-based integrity assurance for computer vision pipelines."

The platform analyzes four major layers:

A. DATASET INTEGRITY
B. MODEL INTEGRITY
C. INFERENCE/OUTPUT INTEGRITY
D. DISTRIBUTION SHIFT / ENVIRONMENTAL ANOMALY

Then combine all evidence into:

E. TRUST & ASSURANCE REPORT

The user should be able to upload a dataset/model/inference package and receive
a detailed security and integrity assessment.

============================================================
2. IMPORTANT CONSTRAINT
============================================================

The entire core system must work OFFLINE.

Do NOT depend on:
- OpenAI APIs
- Gemini APIs
- Groq APIs
- cloud ML APIs
- cloud storage
- external inference services

The system must be suitable for an air-gapped environment.

All ML/CV analysis should run locally.

If an optional external service is added, it must never be required for the
core functionality.

============================================================
3. HIGH-LEVEL ARCHITECTURE
============================================================

Build the following architecture:

                    ┌─────────────────────┐
                    │   React Dashboard   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    └──────────┬──────────┘
                               │
          ┌────────────────────┼────────────────────┐
          ▼                    ▼                    ▼
 ┌────────────────┐   ┌────────────────┐   ┌─────────────────┐
 │ Dataset Engine │   │ Model Analyzer │   │ Provenance      │
 │                │   │                │   │ Engine          │
 └────────────────┘   └────────────────┘   └─────────────────┘
          │                    │                    │
          └────────────────────┼────────────────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Distribution Shift  │
                    │ Detection Engine    │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Assurance / Risk    │
                    │ Scoring Engine      │
                    └──────────┬──────────┘
                               ▼
                    ┌─────────────────────┐
                    │ Evidence & Audit    │
                    │ Report Generator    │
                    └─────────────────────┘


TECH STACK:

Frontend:
- React
- Vite
- Tailwind CSS
- Recharts
- Lucide React

Backend:
- Python
- FastAPI
- Pydantic
- Uvicorn

AI/ML:
- PyTorch
- TorchVision
- ONNX Runtime
- OpenCV
- NumPy
- scikit-learn
- Pillow

Data:
- SQLite for simple local deployment
OR
- PostgreSQL if needed

Security:
- SHA-256
- SHA-512 where appropriate
- HMAC
- cryptographic signatures
- nonce
- timestamps
- hash chains

Deployment:
- Docker
- docker-compose

============================================================
4. FRONTEND
============================================================

Create a professional cybersecurity/defense-grade dashboard.

DO NOT make it look like a generic student CRUD application.

Design language:
- professional
- analytical
- modern
- dark/light mode
- minimal
- security dashboard style
- clear status indicators
- charts
- evidence cards
- severity badges
- confidence indicators

Main navigation:

1. Dashboard
2. Dataset Integrity
3. Model Integrity
4. Inference Verification
5. Distribution Shift
6. Attack Simulator
7. Evidence Explorer
8. Audit Trail
9. Assurance Reports
10. System Information

============================================================
5. DASHBOARD
============================================================

Create a main dashboard containing:

Overall Trust Score
Integrity Status
Dataset Risk
Model Risk
Inference Risk
Distribution Shift Risk
Provenance Status

Example:

OVERALL TRUST SCORE
82 / 100

STATUS
REVIEW

DATASET
LOW RISK

MODEL
MEDIUM RISK

INFERENCE
VERIFIED

DISTRIBUTION SHIFT
MEDIUM

Also show:

- number of datasets analyzed
- number of models analyzed
- suspicious samples
- detected anomalies
- verified inference records
- tampered records
- quarantined assets
- recent audit events

Add charts:

1. Risk over time
2. Dataset anomaly distribution
3. Severity distribution
4. Provenance verification results

============================================================
6. DATASET INTEGRITY ENGINE
============================================================

This is one of the most important modules.

Support:

- COCO datasets
- YOLO datasets
- image folders
- CSV metadata where applicable

Analyze the dataset for:

A. Label flipping
B. Systematic mislabeling
C. Suspicious/anomalous samples
D. Near-duplicate flooding
E. Out-of-distribution samples
F. Class imbalance anomalies
G. Contributor/source risk
H. Image corruption
I. Suspicious image manipulation
J. unusual metadata patterns

------------------------------------------------------------
6.1 IMAGE QUALITY ANALYSIS
------------------------------------------------------------

For every image calculate:

- resolution
- aspect ratio
- brightness
- contrast
- blur
- noise
- file size
- image format
- duplicate hash
- perceptual hash

Detect:

- corrupted files
- extremely blurry images
- suspiciously identical images
- unusual image dimensions
- unusual compression patterns

------------------------------------------------------------
6.2 DUPLICATE DETECTION
------------------------------------------------------------

Implement:

Exact duplicate detection:
SHA-256

Near duplicate detection:
Perceptual hashing

Optional:
Image embeddings

Use:

- pHash
- dHash
- cosine similarity

Group visually similar images.

Display:

Cluster #1
Images: 127
Similarity: 96%

Flag suspicious clusters.

------------------------------------------------------------
6.3 LABEL CONSISTENCY ANALYSIS
------------------------------------------------------------

Analyze whether image content and labels appear inconsistent.

Implement a lightweight local approach.

For example:

- class distribution
- visual similarity within classes
- embedding clustering
- nearest-neighbor class consistency

Flag:

"Potential label inconsistency"

Do NOT claim certainty.

Use wording:

"Potential anomaly detected"

instead of:

"Confirmed malicious sample"

because the system must distinguish evidence from assumptions.

------------------------------------------------------------
6.4 OUT-OF-DISTRIBUTION DETECTION
------------------------------------------------------------

Use image embeddings and anomaly detection.

Possible methods:

- pretrained local feature extractor
- PCA
- Isolation Forest
- Local Outlier Factor
- distance-based anomaly detection

For each sample calculate:

OOD score:
0-1

Example:

Image 0342
OOD score: 0.91
Severity: HIGH

Reason:

"Visual embedding is significantly distant from the reference
dataset distribution."

============================================================
7. MODEL INTEGRITY ENGINE
============================================================

Support:

- ONNX
- PyTorch
- TorchScript

The system should NOT require model retraining.

When a model is uploaded:

Calculate:

- SHA-256 model hash
- file size
- architecture information
- input shape
- output shape
- parameter count where available
- framework
- model metadata

Display:

MODEL FINGERPRINT

Model:
vision_model.onnx

SHA-256:
abc123...

Framework:
ONNX

Input:
640x640x3

------------------------------------------------------------
7.1 MODEL BEHAVIORAL FINGERPRINTING
------------------------------------------------------------

Create a reference test dataset.

Run the model on the test dataset.

Record:

- predictions
- confidence
- class distribution
- output statistics
- feature statistics where available

Generate a behavioral fingerprint.

Example:

Model Fingerprint

Class distribution:
Normal: 72%
Suspicious: 18%
Other: 10%

Average confidence:
0.84

Entropy:
0.31

------------------------------------------------------------
7.2 MODEL SUBSTITUTION DETECTION
------------------------------------------------------------

If a trusted/reference model exists:

Compare:

reference model hash
uploaded model hash

If hashes differ:

FLAG:

"Model binary differs from trusted reference."

Then optionally compare behavior.

Do not automatically call it malicious.

Severity depends on evidence.

============================================================
8. BACKDOOR / TRIGGER ANALYSIS
============================================================

Implement a practical demonstration-grade trigger analysis system.

Create a controlled test mode.

Generate synthetic trigger patches such as:

- square patch
- corner patch
- stripe
- small geometric pattern

Test the model with:

normal image
+
trigger patch

Compare predictions.

Calculate:

Prediction change rate

Example:

Normal prediction:
Vehicle — 91%

Triggered prediction:
Person — 97%

Prediction change:
86%

If a repeated trigger causes abnormal consistent behavior,
flag:

"Potential trigger-sensitive behavior."

IMPORTANT:

Use wording such as:

"Potential backdoor-like behavior"

NOT:

"Confirmed backdoor."

Clearly display:

Evidence
Confidence
Limitations

============================================================
9. PARAMETER / ACTIVATION ANALYSIS
============================================================

When white-box access is available:

Analyze:

- parameter statistics
- weight distribution
- activation statistics
- unusually large values
- layer anomalies

When white-box access is unavailable:

Gracefully fallback to behavioral analysis.

Display:

Analysis mode:
BLACK-BOX

or

Analysis mode:
WHITE-BOX

============================================================
10. INFERENCE PROVENANCE ENGINE
============================================================

This is another major differentiator.

Every inference record must cryptographically bind:

1. input image hash
2. model identifier
3. model weight digest
4. preprocessing configuration
5. inference result
6. timestamp
7. sequence number
8. nonce
9. operator/session identifier

Generate a cryptographic record.

Example:

{
    "input_hash": "...",
    "model_hash": "...",
    "preprocessing_hash": "...",
    "result_hash": "...",
    "timestamp": "...",
    "sequence": 102,
    "nonce": "...",
    "record_hash": "..."
}

Generate:

SHA-256(record_contents)

============================================================
11. TAMPER-EVIDENT AUDIT LOG
============================================================

Implement a hash-chain based audit log.

Example:

Record 001
hash = ABC

Record 002
previous_hash = ABC
hash = DEF

Record 003
previous_hash = DEF
hash = XYZ

If someone modifies Record 002:

the chain becomes invalid.

Dashboard should show:

AUDIT CHAIN
✓ VERIFIED

or:

AUDIT CHAIN
✕ TAMPER DETECTED

Allow the user to intentionally modify a demo record
and demonstrate detection.

This must be one of the main hackathon demo features.

============================================================
12. REPLAY ATTACK DETECTION
============================================================

Use:

- sequence number
- timestamp
- nonce
- record hash

Detect:

- duplicated inference records
- repeated nonce
- invalid sequence
- old record replay
- timestamp inconsistency

Example:

Record #104
Status:
REPLAY DETECTED

Reason:
"Sequence number already observed."

============================================================
13. POST-HOC OUTPUT TAMPERING
============================================================

Create a verification page.

Original inference:

Vehicle
Confidence:
0.94

Stored hash:
ABC123

Current record hash:
ABC123

STATUS:
VERIFIED

If result is changed:

Vehicle → Person

Hash changes.

Show:

STATUS:
TAMPER DETECTED

Evidence:

Original result hash
Current result hash

============================================================
14. DISTRIBUTION SHIFT ENGINE
============================================================

The system must distinguish normal environmental changes
from suspicious manipulation where evidence supports it.

Analyze changes caused by:

- lighting
- weather
- season
- sensor
- viewpoint
- image quality
- terrain/environment

Calculate distribution differences.

Use:

- embedding distributions
- brightness distributions
- color distributions
- feature statistics
- KL divergence where appropriate
- cosine distance
- Wasserstein distance where appropriate

Display:

REFERENCE DISTRIBUTION
vs
CURRENT DISTRIBUTION

Example:

Reference:
Normal environment

Current:
Low-light environment

Shift:
0.62

Interpretation:

"Moderate distribution shift detected.
Evidence does not establish malicious manipulation."

This distinction is VERY IMPORTANT.

============================================================
15. CONTRIBUTOR RISK
============================================================

For every dataset/model contributor create a profile.

Example:

Contributor:
Contributor-A

Assets:
14

Anomalies:
3

High-risk samples:
2

Risk:
MEDIUM

Possible signals:

- repeated anomalies
- suspicious duplication
- unusual label patterns
- unexpected metadata
- model behavior deviation

Do NOT claim a contributor is malicious.

Use:

"Contributor risk indicator"

instead of:

"Malicious contributor."

============================================================
16. ASSURANCE / RISK ENGINE
============================================================

Create a transparent scoring system.

Example:

Dataset Integrity = 85
Model Integrity = 72
Inference Provenance = 98
Distribution Stability = 81

Overall:

0-30 = CRITICAL
31-50 = HIGH
51-70 = MEDIUM
71-85 = LOW
86-100 = TRUSTED

Calculate overall score using weighted components.

Example:

Dataset = 30%
Model = 30%
Inference = 25%
Distribution = 15%

Make weights configurable.

IMPORTANT:

Never create an unexplained black-box trust score.

The dashboard must show exactly why the score was produced.

============================================================
17. EVIDENCE ENGINE
============================================================

Every alert must contain:

- What happened
- Why it was flagged
- Evidence
- Severity
- Confidence
- Affected asset
- Recommended action
- Limitations

Example:

-------------------------------------------------
POTENTIAL DATA POISONING INDICATOR
-------------------------------------------------

Asset:
dataset/images/img_0342.jpg

Severity:
HIGH

Confidence:
0.87

Evidence:

• Label differs from local neighborhood pattern
• Image embedding is anomalous
• Similar samples appear 37 times
• Contributor has previous anomalies

Recommended action:
REVIEW / QUARANTINE

Limitation:
"This analysis does not establish malicious intent."
-------------------------------------------------

============================================================
18. ANALYST DISPOSITION
============================================================

For every flagged asset provide buttons:

[ ACCEPT ]

[ REVIEW ]

[ QUARANTINE ]

When analyst selects an action:

Store:

- analyst action
- timestamp
- asset ID
- reason
- previous state
- new state
- audit hash

============================================================
19. ATTACK SIMULATOR
============================================================

This module is extremely important for the hackathon demo.

Create a controlled "Security Lab".

Allow the user to generate synthetic attack scenarios.

Available attacks:

1. Label flipping
2. Near-duplicate flooding
3. OOD insertion
4. Image corruption
5. Dataset poisoning
6. Trigger injection
7. Model substitution
8. Inference result tampering
9. Replay attack
10. Metadata manipulation

The simulator must operate only on demo/test data.

NEVER modify the original source data without creating a copy.

Example:

[Generate Label Flip Attack]

Original:
car

Modified:
person

Then run the assurance pipeline.

Show:

ATTACK SIMULATION
↓
ANALYSIS
↓
EVIDENCE
↓
RISK SCORE
↓
DISPOSITION

============================================================
20. REPRODUCIBILITY
============================================================

Every attack simulation should have:

Simulation ID

Example:

SIM-2026-00042

Store:

- attack type
- dataset
- model
- parameters
- random seed
- timestamp
- resulting artifacts

This allows the demo to be reproduced.

============================================================
21. EVIDENCE EXPLORER
============================================================

Create a page where analysts can inspect every finding.

Filters:

- severity
- asset
- contributor
- attack type
- confidence
- date
- disposition

Each finding should open a detailed evidence panel.

Include:

Image preview
Embedding/anomaly information
Hashes
Model information
Timeline
Audit records

============================================================
22. AUDIT TRAIL
============================================================

Create a chronological timeline:

10:01 Dataset uploaded
10:02 14 suspicious duplicates detected
10:03 Model uploaded
10:04 Model fingerprint generated
10:05 Trigger analysis completed
10:06 Inference package verified
10:07 Tampering detected
10:08 Analyst selected REVIEW

Every event should contain a cryptographic hash.

============================================================
23. REPORT GENERATION
============================================================

Generate a professional assurance report.

Formats:

PDF
JSON

Report structure:

1. Executive Summary
2. Asset Information
3. Dataset Integrity Results
4. Model Integrity Results
5. Inference Provenance Results
6. Distribution Shift Results
7. Detected Anomalies
8. Risk Score
9. Evidence
10. Analyst Disposition
11. Audit Trail
12. Assumptions
13. Limitations
14. Unsupported Attack Classes

Example final conclusion:

OVERALL STATUS:
REVIEW REQUIRED

TRUST SCORE:
68/100

PRIMARY REASONS:

• Potential dataset anomalies
• Model behavioral deviation
• Valid inference provenance
• Moderate environmental distribution shift

============================================================
24. UNSUPPORTED ATTACK CLASSES
============================================================

This section MUST exist.

Never pretend the system detects every possible attack.

Create a visible section:

"Current Detection Coverage"

Supported:
✓ Label anomalies
✓ Duplicate flooding
✓ OOD samples
✓ Trigger-sensitive behavior
✓ Model substitution
✓ Inference tampering
✓ Replay
✓ Distribution shift

Partially supported:
~ Advanced stealth backdoors
~ Sophisticated adversarial attacks
~ Unknown poisoning strategies

Unsupported:
✕ Clearly list anything not implemented

This increases technical credibility.

============================================================
25. DATASET DEMO
============================================================

Provide a built-in sample dataset.

Create synthetic demo datasets for:

1. Clean dataset
2. Label-flipped dataset
3. Duplicate-heavy dataset
4. OOD dataset
5. Mixed attack dataset

The application must work immediately after installation
without requiring the user to find datasets online.

============================================================
26. MODEL DEMO
============================================================

Provide at least one small local vision model.

Prefer:

MobileNet / ResNet / YOLO-compatible example

Provide:

- clean model
- reference model
- modified/demo model

The system should be able to compare them.

============================================================
27. INFERENCE DEMO
============================================================

Create sample inference records.

Provide:

Normal records
Tampered records
Replay records
Invalid hash records

Include a button:

"Run Integrity Verification"

Expected output:

✓ 87 records verified
⚠ 5 records require review
✕ 3 records tampered
✕ 2 replay attacks detected

============================================================
28. DATABASE DESIGN
============================================================

Create database tables:

users
datasets
dataset_samples
contributors
models
model_fingerprints
inference_records
anomalies
attack_simulations
audit_logs
assurance_reports
analyst_actions

Use proper foreign keys.

============================================================
29. API DESIGN
============================================================

Create FastAPI endpoints.

Examples:

POST /api/datasets/upload

POST /api/datasets/analyze

GET /api/datasets/{id}

POST /api/models/upload

POST /api/models/analyze

POST /api/models/fingerprint

POST /api/models/trigger-analysis

POST /api/inference/verify

POST /api/inference/tamper-test

POST /api/inference/replay-test

POST /api/distribution/analyze

POST /api/simulator/create

POST /api/assurance/run

GET /api/assurance/{id}

GET /api/audit

POST /api/audit/verify

POST /api/assets/{id}/disposition

GET /api/reports/{id}

GET /api/system/status

Document all APIs.

============================================================
30. PROJECT STRUCTURE
============================================================

Create a clean monorepo:

visiontrust-ai/

├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── charts/
│   │   ├── services/
│   │   ├── hooks/
│   │   └── utils/
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── security/
│   │   ├── cv/
│   │   ├── ml/
│   │   ├── provenance/
│   │   ├── analytics/
│   │   └── reports/
│   ├── tests/
│   └── requirements.txt
│
├── data/
│   ├── demo/
│   ├── clean/
│   ├── poisoned/
│   └── inference/
│
├── models/
│
├── simulator/
│
├── reports/
│
├── docker/
│
├── docker-compose.yml
│
├── README.md
│
└── LICENSE

============================================================
31. SECURITY REQUIREMENTS
============================================================

Implement:

- input validation
- file type validation
- file size limits
- secure file names
- path traversal protection
- API validation
- cryptographic hashes
- audit logging
- no arbitrary code execution from uploaded files
- isolated processing where possible

Never execute uploaded model files as arbitrary Python code.

Prefer safe formats such as ONNX for untrusted models.

============================================================
32. PERFORMANCE
============================================================

The application must not freeze while processing large datasets.

Implement:

- background jobs
- progress indicators
- batch processing
- pagination
- caching where appropriate

Frontend must show:

Analysis:
23%

Analysis:
67%

Analysis:
100%

============================================================
33. USER EXPERIENCE
============================================================

Main workflow must be simple:

STEP 1
Upload Asset

↓

STEP 2
Select Analysis

Dataset
Model
Inference
Full Pipeline

↓

STEP 3
Run Assurance

↓

STEP 4
View Findings

↓

STEP 5
Inspect Evidence

↓

STEP 6
Choose:

ACCEPT
REVIEW
QUARANTINE

↓

STEP 7
Generate Report

============================================================
34. TRUST SCORE VISUALIZATION
============================================================

Create a large circular trust score.

Example:

        82
    TRUST SCORE

Use animated visualization.

Below it:

Dataset Integrity     85
Model Integrity       72
Inference Integrity   98
Distribution Stability 81

Clicking each component opens its evidence.

============================================================
35. IMPORTANT DEMO MODE
============================================================

Create a "Hackathon Demo Mode".

The demo should take approximately 5 minutes.

Scenario:

STEP 1:
Load clean dataset.

Result:
TRUSTED

STEP 2:
Inject duplicate samples.

Result:
Potential anomaly detected.

STEP 3:
Inject label-flipped samples.

Result:
Potential label inconsistency.

STEP 4:
Load modified model.

Result:
Model fingerprint mismatch.

STEP 5:
Run trigger analysis.

Result:
Potential trigger-sensitive behavior.

STEP 6:
Run inference.

Result:
Inference record created.

STEP 7:
Tamper with inference result.

Result:
TAMPERING DETECTED.

STEP 8:
Replay an inference record.

Result:
REPLAY DETECTED.

STEP 9:
Show audit chain.

Result:
TAMPER-EVIDENT LOG VERIFIED.

STEP 10:
Generate assurance report.

Result:
REVIEW REQUIRED.

This complete flow should be extremely polished.

============================================================
36. EXPLAINABILITY
============================================================

Every AI result must explain:

WHAT
WHY
EVIDENCE
CONFIDENCE
LIMITATION
ACTION

Never simply show:

"AI detected attack."

Instead show:

"Potential anomaly detected because:
• embedding distance is high
• duplicate similarity is 97%
• label differs from neighboring samples

Confidence: 0.86

Limitation:
This does not prove malicious intent."

============================================================
37. ERROR HANDLING
============================================================

The application must gracefully handle:

- invalid files
- unsupported models
- corrupted images
- missing metadata
- empty datasets
- invalid annotations
- unavailable model weights
- inference failures
- database failures

Never crash the complete application.

Display useful messages.

============================================================
38. TESTING
============================================================

Create automated tests for:

Dataset analyzer
Duplicate detection
OOD detection
Hash generation
Audit chain
Replay detection
Tamper detection
Model fingerprint
Risk scoring
API endpoints

Also create integration tests.

============================================================
39. DOCUMENTATION
============================================================

Create a high-quality README containing:

1. Problem statement
2. Why the problem matters
3. Solution
4. Architecture
5. Features
6. Technology stack
7. Installation
8. Running locally
9. Docker deployment
10. Demo instructions
11. Dataset formats
12. Model formats
13. Security architecture
14. Risk scoring
15. Attack simulation
16. Limitations
17. Future scope

============================================================
40. FUTURE SCOPE
============================================================

Include architecture that can later support:

- federated learning assurance
- zero-knowledge proofs
- blockchain anchoring
- confidential computing
- hardware-backed attestation
- advanced adversarial robustness
- SBOM/model cards
- automated red-team testing
- secure multi-party model contribution
- post-quantum cryptographic algorithms

DO NOT implement these if they unnecessarily increase complexity.

Design the architecture so they can be added later.

============================================================
41. IMPORTANT: DO NOT OVERENGINEER
============================================================

This is a hackathon project.

Prioritize:

1. Working system
2. Strong demo
3. Correctness
4. Explainability
5. Security
6. Visual quality
7. Reproducibility

Do not spend most development time building unnecessary enterprise features.

Every major feature must actually work.

Avoid fake buttons and placeholder functionality.

============================================================
42. FINAL ACCEPTANCE CRITERIA
============================================================

The project is considered complete only when:

✓ Dataset can be uploaded
✓ Dataset can be analyzed
✓ Duplicate anomalies can be detected
✓ OOD samples can be identified
✓ Label anomalies can be flagged
✓ Model can be uploaded
✓ Model hash can be generated
✓ Model fingerprint can be generated
✓ Model comparison works
✓ Trigger simulation works
✓ Inference records can be generated
✓ Inference records can be verified
✓ Tampering can be detected
✓ Replay can be detected
✓ Hash-chain audit log works
✓ Distribution shift can be analyzed
✓ Trust score is generated
✓ Evidence is shown
✓ Analyst can ACCEPT/REVIEW/QUARANTINE
✓ PDF/JSON report is generated
✓ Demo attack simulator works
✓ Offline mode works
✓ Docker deployment works
✓ README is complete
✓ Tests are included

============================================================
43. IMPLEMENTATION STRATEGY
============================================================

DO NOT generate the entire project blindly in one step.

Build in phases.

PHASE 1:
Project setup
Frontend + Backend
Database
Docker

PHASE 2:
Dashboard
Navigation
UI components

PHASE 3:
Dataset analyzer

PHASE 4:
Model analyzer

PHASE 5:
Inference provenance

PHASE 6:
Audit chain

PHASE 7:
Distribution shift

PHASE 8:
Attack simulator

PHASE 9:
Assurance/risk engine

PHASE 10:
Reports

PHASE 11:
Testing

PHASE 12:
Hackathon demo mode

After each phase:
- run the application
- test the implemented features
- fix errors
- do not proceed with broken functionality

============================================================
44. FINAL OUTPUT
============================================================

At the end provide:

1. Complete source code
2. Project structure
3. Setup commands
4. Docker commands
5. Database setup
6. Demo dataset
7. Demo models
8. Attack simulator
9. API documentation
10. README
11. Test suite
12. Sample assurance reports

The final system should look like a serious cybersecurity + AI assurance
platform that could realistically be demonstrated to a Ministry of Defence /
Indian Army technical evaluation panel.

Do not describe the project as merely:
"an AI image classifier."

The core identity is:

"An evidence-driven computer vision integrity assurance platform for
multi-contributor AI pipelines."

Start by creating the project architecture and Phase 1.
Then implement each phase sequentially, testing before moving to the next phase.

implement with working prototype with real world data