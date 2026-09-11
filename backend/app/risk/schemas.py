"""
TrustLens Risk & Evidence Schemas
Conforms strictly to Section 21 & Section 22 Evidence Object contracts.
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class Severity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Disposition(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REVIEW = "REVIEW"
    QUARANTINE = "QUARANTINE"


class RiskBand(str, Enum):
    CRITICAL = "CRITICAL"   # 0 - 30
    HIGH = "HIGH"           # 31 - 50
    MEDIUM = "MEDIUM"       # 51 - 70
    LOW = "LOW"             # 71 - 85
    TRUSTED = "TRUSTED"     # 86 - 100


class EvidenceObject(BaseModel):
    """
    Section 22 Evidence Object contract.
    Must maintain non-accusatory, empirical tone across all findings.
    """
    evidence_id: str = Field(default_factory=lambda: f"EVD-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')[:17]}")
    finding_type: str
    what_happened: str
    why_flagged: str
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    severity: Severity
    confidence: float = Field(ge=0.0, le=1.0)
    affected_asset: str
    recommended_action: str
    limitations: str
    disposition: Disposition = Disposition.PENDING
    contributor_id: Optional[str] = None
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class ComponentScores(BaseModel):
    dataset_integrity: float = Field(ge=0.0, le=100.0)
    model_integrity: float = Field(ge=0.0, le=100.0)
    inference_integrity: float = Field(ge=0.0, le=100.0)
    distribution_stability: float = Field(ge=0.0, le=100.0)


class ScorePenalty(BaseModel):
    component: str  # "dataset", "model", "inference", "distribution"
    penalty_points: float
    reason: str
    evidence_id: Optional[str] = None


class TrustScoreResult(BaseModel):
    """
    Section 21 Trust Scoring Result.
    Fully transparent, mathematical breakdown with no hidden state.
    """
    overall_score: float = Field(ge=0.0, le=100.0)
    risk_band: RiskBand
    status_label: str
    status_color: str  # "green", "cyan", "amber", "orange", "red"
    component_scores: ComponentScores
    weights: Dict[str, float] = {
        "dataset_integrity": 0.30,
        "model_integrity": 0.30,
        "inference_integrity": 0.25,
        "distribution_stability": 0.15,
    }
    deductions: List[ScorePenalty] = Field(default_factory=list)
    formula_breakdown: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    summary: str
