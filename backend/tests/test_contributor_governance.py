"""
Unit Tests for Contributor Governance (Section 20)
"""

from app.governance.contributor import (
    ContributorGovernance,
    ContributorRole,
    ContributorRisk,
    ContributorStatus,
)


def test_contributor_roles():
    gov = ContributorGovernance()
    summary = gov.get_summary()
    assert summary["total_contributors"] >= 4
    # All 4 core roles represented
    for role in [ContributorRole.DATA_CONTRIBUTOR, ContributorRole.MODEL_TRAINER, ContributorRole.AUDITOR, ContributorRole.ADMIN]:
        assert role.value in summary["role_distribution"]


def test_submission_and_anomaly_escalation():
    gov = ContributorGovernance()
    c = gov.register_contributor(
        contributor_id="TEST-001",
        name="Test Ingress",
        role=ContributorRole.DATA_CONTRIBUTOR,
        organization="Sensor Lab",
    )
    assert c.risk_indicator == ContributorRisk.LOW
    assert c.status == ContributorStatus.ACTIVE

    # Record 10 submissions
    gov.record_submission("TEST-001", asset_count=10)
    assert c.assets_submitted == 10

    # Attribute 2 anomalies (ratio 2/10 = 0.20 -> MEDIUM risk)
    gov.attribute_anomaly("TEST-001", "EVD-01")
    gov.attribute_anomaly("TEST-001", "EVD-02")
    assert c.risk_indicator == ContributorRisk.MEDIUM

    # Attribute critical anomaly -> immediate CRITICAL and QUARANTINED
    gov.attribute_anomaly("TEST-001", "EVD-03", is_critical=True)
    assert c.risk_indicator == ContributorRisk.CRITICAL
    assert c.status == ContributorStatus.QUARANTINED
