"""
Unit Tests for TrustEngine (Section 21)
"""

import pytest
from app.risk.trust_engine import TrustEngine
from app.risk.schemas import RiskBand, Severity, EvidenceObject, Disposition


def test_clean_baseline_score():
    result = TrustEngine.calculate(evidence_list=[], distribution_shift_score=0.0)
    assert result.overall_score == 100.0
    assert result.risk_band == RiskBand.TRUSTED
    assert result.status_label == "TRUSTED"
    assert result.component_scores.dataset_integrity == 100.0
    assert result.component_scores.model_integrity == 100.0
    assert result.component_scores.inference_integrity == 100.0
    assert result.component_scores.distribution_stability == 100.0
    assert len(result.deductions) == 0
    assert "Trust Score = (0.30 * 100.0) + (0.30 * 100.0) + (0.25 * 100.0) + (0.15 * 100.0)" in result.formula_breakdown


def test_model_binary_substitution_penalty():
    ev = EvidenceObject(
        finding_type="MODEL BINARY DIFFERENCE",
        what_happened="Model substitution detected: deployment binary hash does not match registered reference.",
        why_flagged="Current binary SHA-256 diverges from verified baseline register.",
        severity=Severity.CRITICAL,
        confidence=1.0,
        affected_asset="resnet18_weights.onnx",
        recommended_action="Roll back model weights.",
        limitations="Assumes registered hash was authentic.",
    )
    result = TrustEngine.calculate(evidence_list=[ev], distribution_shift_score=0.0)
    # Model integrity drops to 0
    assert result.component_scores.model_integrity == 0.0
    # Overall score: 0.30*100 + 0.30*0 + 0.25*100 + 0.15*100 = 30 + 0 + 25 + 15 = 70.0
    assert result.overall_score == 70.0
    assert result.risk_band == RiskBand.MEDIUM
    assert any("MODEL BINARY DIFFERENCE" in d.reason for d in result.deductions)


def test_inference_tampering_penalty():
    ev = EvidenceObject(
        finding_type="Inference record cryptographic violation",
        what_happened="Record hash mismatch detected.",
        why_flagged="Cryptographic payload binding failed.",
        severity=Severity.CRITICAL,
        confidence=1.0,
        affected_asset="INF-001",
        recommended_action="Drop record.",
        limitations="Cryptographic check on record.",
    )
    result = TrustEngine.calculate(evidence_list=[ev], distribution_shift_score=0.0)
    assert result.component_scores.inference_integrity == 0.0
    # Overall score: 0.30*100 + 0.30*100 + 0.25*0 + 0.15*100 = 30 + 30 + 0 + 15 = 75.0
    assert result.overall_score == 75.0
    assert result.risk_band == RiskBand.LOW


def test_compound_penalties_reach_critical():
    ev1 = EvidenceObject(
        finding_type="MODEL BINARY DIFFERENCE",
        what_happened="Model substituted",
        why_flagged="Binary mismatch",
        severity=Severity.CRITICAL,
        confidence=1.0,
        affected_asset="model",
        recommended_action="Rollback",
        limitations="None",
    )
    ev2 = EvidenceObject(
        finding_type="Inference record cryptographic violation",
        what_happened="Inference tampered",
        why_flagged="Signature fail",
        severity=Severity.CRITICAL,
        confidence=1.0,
        affected_asset="inference",
        recommended_action="Drop",
        limitations="None",
    )
    # Both model (0) and inference (0) compromised
    # Dataset 100, Dist 100 -> 0.30*100 + 0.30*0 + 0.25*0 + 0.15*100 = 45.0
    result = TrustEngine.calculate(evidence_list=[ev1, ev2], distribution_shift_score=0.0)
    assert result.overall_score == 45.0
    assert result.risk_band == RiskBand.HIGH

    # If distribution shift also severe (0.90 -> dist score = 10)
    result_crit = TrustEngine.calculate(evidence_list=[ev1, ev2], distribution_shift_score=0.90)
    # 0.30*100 + 0.30*0 + 0.25*0 + 0.15*10 = 30 + 0 + 0 + 1.5 = 31.5 -> HIGH, let's drop data too
    ev3 = EvidenceObject(
        finding_type="Potential duplicate flooding indicator",
        what_happened="Duplicate flood",
        why_flagged="50% duplicates",
        severity=Severity.CRITICAL,
        confidence=1.0,
        affected_asset="dataset",
        recommended_action="Purge",
        limitations="None",
    )
    result_crit = TrustEngine.calculate(evidence_list=[ev1, ev2, ev3], distribution_shift_score=0.90)
    assert result_crit.overall_score <= 30.0
    assert result_crit.risk_band == RiskBand.CRITICAL


def test_custom_component_override():
    custom = {
        "dataset_integrity": 80.0,
        "model_integrity": 90.0,
        "inference_integrity": 85.0,
        "distribution_stability": 95.0,
    }
    # 0.30*80 + 0.30*90 + 0.25*85 + 0.15*95 = 24 + 27 + 21.25 + 14.25 = 86.5
    result = TrustEngine.calculate(custom_component_scores=custom)
    assert result.overall_score == 86.5
    assert result.risk_band == RiskBand.TRUSTED
