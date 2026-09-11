"""
TrustLens Contributor Governance
Conforms strictly to Section 20 of the TrustLens specification.

Defines the 4 core contributor roles:
- DATA_CONTRIBUTOR
- MODEL_TRAINER
- AUDITOR
- ADMIN

Tracks contributor identity, assets submitted, anomalies attributed,
and risk indicators.
"""

from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime, timezone


class ContributorRole(str, Enum):
    DATA_CONTRIBUTOR = "DATA_CONTRIBUTOR"
    MODEL_TRAINER = "MODEL_TRAINER"
    AUDITOR = "AUDITOR"
    ADMIN = "ADMIN"


class ContributorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    FLAGGED = "FLAGGED"
    SUSPENDED = "SUSPENDED"
    QUARANTINED = "QUARANTINED"


class ContributorRisk(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ContributorRecord(BaseModel):
    contributor_id: str
    name: str
    role: ContributorRole
    organization: str
    assets_submitted: int = 0
    anomalies_flagged: int = 0
    risk_indicator: ContributorRisk = ContributorRisk.LOW
    status: ContributorStatus = ContributorStatus.ACTIVE
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    last_active: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    attributed_evidence_ids: List[str] = Field(default_factory=list)

    @property
    def anomaly_ratio(self) -> float:
        if self.assets_submitted == 0:
            return 0.0
        return round(self.anomalies_flagged / self.assets_submitted, 4)


class ContributorGovernance:
    """
    Manages contributor directory, tracks submission metrics,
    and updates dynamic risk ratings based on forensic evidence.
    """

    def __init__(self) -> None:
        self._contributors: Dict[str, ContributorRecord] = {}
        self._seed_default_contributors()

    def _seed_default_contributors(self) -> None:
        defaults = [
            ContributorRecord(
                contributor_id="CONTRIB-001",
                name="Dr. Aris Thorne",
                role=ContributorRole.ADMIN,
                organization="Security Operations Center",
                assets_submitted=15,
                anomalies_flagged=0,
                risk_indicator=ContributorRisk.LOW,
                status=ContributorStatus.ACTIVE,
            ),
            ContributorRecord(
                contributor_id="CONTRIB-002",
                name="Elena Rostova",
                role=ContributorRole.MODEL_TRAINER,
                organization="Vision Research Group",
                assets_submitted=42,
                anomalies_flagged=1,
                risk_indicator=ContributorRisk.LOW,
                status=ContributorStatus.ACTIVE,
            ),
            ContributorRecord(
                contributor_id="CONTRIB-003",
                name="Marcus Vance",
                role=ContributorRole.DATA_CONTRIBUTOR,
                organization="Field Fleet Sensors",
                assets_submitted=85,
                anomalies_flagged=4,
                risk_indicator=ContributorRisk.LOW,
                status=ContributorStatus.ACTIVE,
            ),
            ContributorRecord(
                contributor_id="CONTRIB-004",
                name="Sarah Jenkins",
                role=ContributorRole.AUDITOR,
                organization="Independent Compliance Org",
                assets_submitted=8,
                anomalies_flagged=0,
                risk_indicator=ContributorRisk.LOW,
                status=ContributorStatus.ACTIVE,
            ),
            ContributorRecord(
                contributor_id="CONTRIB-005",
                name="Untrusted External Ingress",
                role=ContributorRole.DATA_CONTRIBUTOR,
                organization="Public Ingestion Endpoint",
                assets_submitted=30,
                anomalies_flagged=18,
                risk_indicator=ContributorRisk.CRITICAL,
                status=ContributorStatus.QUARANTINED,
            ),
        ]
        for c in defaults:
            self._contributors[c.contributor_id] = c

    def register_contributor(
        self,
        contributor_id: str,
        name: str,
        role: ContributorRole,
        organization: str,
    ) -> ContributorRecord:
        record = ContributorRecord(
            contributor_id=contributor_id,
            name=name,
            role=role,
            organization=organization,
        )
        self._contributors[contributor_id] = record
        return record

    def record_submission(self, contributor_id: str, asset_count: int = 1) -> Optional[ContributorRecord]:
        contributor = self._contributors.get(contributor_id)
        if not contributor:
            return None
        contributor.assets_submitted += asset_count
        contributor.last_active = datetime.now(timezone.utc).isoformat()
        self._recalculate_risk(contributor)
        return contributor

    def attribute_anomaly(
        self,
        contributor_id: str,
        evidence_id: str,
        is_critical: bool = False,
    ) -> Optional[ContributorRecord]:
        contributor = self._contributors.get(contributor_id)
        if not contributor:
            return None
        contributor.anomalies_flagged += 1
        if evidence_id not in contributor.attributed_evidence_ids:
            contributor.attributed_evidence_ids.append(evidence_id)
        contributor.last_active = datetime.now(timezone.utc).isoformat()
        self._recalculate_risk(contributor, is_critical=is_critical)
        return contributor

    def _recalculate_risk(self, contributor: ContributorRecord, is_critical: bool = False) -> None:
        ratio = contributor.anomaly_ratio
        if is_critical or ratio >= 0.40 or contributor.anomalies_flagged >= 10:
            contributor.risk_indicator = ContributorRisk.CRITICAL
            contributor.status = ContributorStatus.QUARANTINED
        elif ratio >= 0.25 or contributor.anomalies_flagged >= 5:
            contributor.risk_indicator = ContributorRisk.HIGH
            contributor.status = ContributorStatus.FLAGGED
        elif ratio >= 0.10:
            contributor.risk_indicator = ContributorRisk.MEDIUM
            contributor.status = ContributorStatus.ACTIVE
        else:
            contributor.risk_indicator = ContributorRisk.LOW
            if contributor.status == ContributorStatus.FLAGGED:
                contributor.status = ContributorStatus.ACTIVE

    def get_contributor(self, contributor_id: str) -> Optional[ContributorRecord]:
        return self._contributors.get(contributor_id)

    def list_contributors(
        self,
        role: Optional[ContributorRole] = None,
        risk: Optional[ContributorRisk] = None,
    ) -> List[ContributorRecord]:
        results = list(self._contributors.values())
        if role:
            results = [c for c in results if c.role == role]
        if risk:
            results = [c for c in results if c.risk_indicator == risk]
        return results

    def get_summary(self) -> Dict[str, Any]:
        records = list(self._contributors.values())
        total = len(records)
        active = sum(1 for c in records if c.status == ContributorStatus.ACTIVE)
        quarantined = sum(1 for c in records if c.status == ContributorStatus.QUARANTINED)
        high_critical = sum(1 for c in records if c.risk_indicator in [ContributorRisk.HIGH, ContributorRisk.CRITICAL])
        return {
            "total_contributors": total,
            "active_contributors": active,
            "quarantined_contributors": quarantined,
            "elevated_risk_contributors": high_critical,
            "role_distribution": {
                role.value: sum(1 for c in records if c.role == role)
                for role in ContributorRole
            },
        }
