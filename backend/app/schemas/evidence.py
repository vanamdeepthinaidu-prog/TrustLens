"""TrustLens Evidence Object Schema (Section 22 Specification)

Standardized evidence representation used across all detection engines
(Dataset Integrity, Model Security, Inference Verification, and Attack Simulation).
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field


class SeverityEnum(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class DispositionEnum(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REVIEW = "REVIEW"
    QUARANTINED = "QUARANTINED"
    DISMISSED = "DISMISSED"


class EvidenceItem(BaseModel):
    """Specific key-value or metric entry supporting an evidence finding."""
    key: str
    value: Any
    unit: Optional[str] = None
    threshold: Optional[Any] = None
    description: Optional[str] = None


class EvidenceObject(BaseModel):
    """Canonical Section 22 Evidence Object."""
    id: str = Field(..., description="Unique evidence ID, e.g. EVID-DS-2026-00042")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO-8601 UTC timestamp of detection"
    )
    finding_type: str = Field(
        ...,
        description="Category: DUPLICATE_FLOODING, OOD_ANOMALY, LABEL_INCONSISTENCY, CORRUPTED_FILE, etc."
    )
    what_happened: str = Field(
        ...,
        description="Factual, objective summary of the event or condition observed"
    )
    why_flagged: str = Field(
        ...,
        description="Technical criterion, statistical threshold, or heuristic triggered"
    )
    evidence: Union[List[EvidenceItem], Dict[str, Any]] = Field(
        ...,
        description="Structured supporting evidence metrics, hashes, and comparisons"
    )
    severity: SeverityEnum = Field(
        ...,
        description="Severity assessment: CRITICAL | HIGH | MEDIUM | LOW | INFO"
    )
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence score between 0.0 and 1.0"
    )
    affected_asset: str = Field(
        ...,
        description="Identifier or path of the affected file, sample, or dataset"
    )
    recommended_action: str = Field(
        ...,
        description="Concrete, actionable remediation advice for security analysts"
    )
    limitations: str = Field(
        ...,
        description="Objective boundary conditions, assumptions, or false-positive risks"
    )
    disposition: DispositionEnum = Field(
        default=DispositionEnum.PENDING,
        description="Analyst disposition status"
    )
