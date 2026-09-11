from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.orm_models import AnalystAction, Anomaly
from app.schemas.pydantic_schemas import (
    DispositionRequest, DispositionResponse, EvidenceItem
)
from app.provenance.ledger import append_block

router = APIRouter(prefix="", tags=["Asset Governance & Evidence Explorer (M4 Integration)"])

@router.post("/assets/{asset_id}/disposition", response_model=DispositionResponse)
def record_disposition(asset_id: str, req: DispositionRequest, db: Session = Depends(get_db)):
    """
    Record an official human analyst disposition: ACCEPT, REVIEW, or QUARANTINE.
    Immediately commits the decision, analyst ID, and justification to the audit ledger.
    """
    now_str = datetime.now(timezone.utc).isoformat()
    action = AnalystAction(
        asset_id=asset_id,
        asset_type="DATASET" if "DS" in asset_id else "MODEL",
        analyst_name=req.analyst_name or "Lead Security Analyst",
        disposition=req.disposition,
        justification=req.justification,
        timestamp=now_str
    )
    db.add(action)
    db.commit()

    block = append_block(
        event_type="DISPOSITION_RECORDED",
        entity_type="ASSET",
        entity_id=asset_id,
        payload={
            "disposition": req.disposition,
            "analyst": req.analyst_name,
            "justification": req.justification
        },
        operator_id=req.analyst_name or "ANALYST"
    )

    return DispositionResponse(
        asset_id=asset_id,
        disposition=req.disposition,
        analyst_name=req.analyst_name or "Lead Security Analyst",
        recorded_at=now_str,
        ledger_block_index=block.block_index
    )

@router.get("/evidence", response_model=List[EvidenceItem])
def query_evidence(
    severity: Optional[str] = Query(None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"),
    asset: Optional[str] = Query(None, description="Filter by asset name or ID")
):
    """
    Evidence Explorer filterable query endpoint returning structured findings
    with WHAT / WHY / EVIDENCE / CONFIDENCE / LIMITATION / RECOMMENDED ACTION.
    """
    sample_evidence = [
        EvidenceItem(
            finding_id="FINDING-2026-001",
            finding_type="DUPLICATE_FLOODING",
            what_happened="12 highly correlated image samples detected with identical perceptual hash structures.",
            why_flagged="Artificially skews training weights toward a specific combat vehicle angle.",
            severity="HIGH",
            confidence=0.94,
            affected_asset="DS-2026-DEMO01",
            recommended_action="Quarantine duplicate cluster; deduplicate dataset before model retraining.",
            limitations="Perceptual hashing measures visual similarity; cannot ascertain submitter intent.",
            disposition="REVIEW",
            timestamp="2026-09-10T08:15:00Z"
        ),
        EvidenceItem(
            finding_id="FINDING-2026-002",
            finding_type="OOD_ANOMALY",
            what_happened="Feature embedding distance exceeds 3 standard deviations from reference centroid.",
            why_flagged="Civilian commercial vehicle injected into armored defense reconnaissance dataset.",
            severity="MEDIUM",
            confidence=0.87,
            affected_asset="DS-2026-DEMO01",
            recommended_action="Inspect sample manually and filter non-military assets.",
            limitations="Isolation Forest distance heuristic based on ImageNet representations.",
            disposition="PENDING",
            timestamp="2026-09-10T08:20:00Z"
        ),
        EvidenceItem(
            finding_id="FINDING-2026-003",
            finding_type="MODEL_BINARY_DIFFERENCE",
            what_happened="Computed SHA-256 does not match certified model registry reference hash.",
            why_flagged="Potential unauthorized weight substitution or corrupted deployment artifact.",
            severity="CRITICAL",
            confidence=1.0,
            affected_asset="MOD-2026-RESNET18",
            recommended_action="Halt deployment pipeline; revert model weights from secure offline air-gapped vault.",
            limitations="Cryptographic hash discrepancy indicates byte change; does not determine adversarial intent.",
            disposition="QUARANTINE",
            timestamp="2026-09-10T08:25:00Z"
        )
    ]

    results = sample_evidence
    if severity:
        results = [e for e in results if e.severity.upper() == severity.upper()]
    if asset:
        results = [e for e in results if asset.lower() in e.affected_asset.lower()]

    return results
