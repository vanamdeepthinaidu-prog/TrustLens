"""
TrustLens Transparent Trust Scoring Engine
Conforms strictly to Section 21 of the TrustLens specification.

Weights:
- Dataset Integrity: 30% (0.30)
- Model Integrity: 30% (0.30)
- Inference Integrity: 25% (0.25)
- Distribution Stability: 15% (0.15)

Score Bands:
- 86 - 100: TRUSTED (Green)
- 71 - 85:  LOW (Cyan)
- 51 - 70:  MEDIUM (Amber)
- 31 - 50:  HIGH (Orange)
- 0  - 30:  CRITICAL (Red)
"""

from typing import List, Optional, Dict, Any
from app.risk.schemas import (
    RiskBand,
    TrustScoreResult,
    ComponentScores,
    ScorePenalty,
    EvidenceObject,
    Severity,
)


class TrustEngine:
    """
    Transparent, verifiable risk engine computing overall trust score
    and itemized penalty deductions with complete mathematical auditability.
    """

    WEIGHTS = {
        "dataset_integrity": 0.30,
        "model_integrity": 0.30,
        "inference_integrity": 0.25,
        "distribution_stability": 0.15,
    }

    @classmethod
    def evaluate_risk_band(cls, score: float) -> tuple[RiskBand, str, str]:
        """Maps numerical score to RiskBand, label, and UI display color."""
        clamped = max(0.0, min(100.0, score))
        if clamped >= 86.0:
            return RiskBand.TRUSTED, "TRUSTED", "#10B981"  # Emerald Green
        elif clamped >= 71.0:
            return RiskBand.LOW, "LOW RISK", "#06B6D4"     # Cyan
        elif clamped >= 51.0:
            return RiskBand.MEDIUM, "MEDIUM RISK", "#F59E0B" # Amber
        elif clamped >= 31.0:
            return RiskBand.HIGH, "HIGH RISK", "#F97316"   # Orange
        else:
            return RiskBand.CRITICAL, "CRITICAL RISK", "#EF4444" # Red

    @classmethod
    def calculate(
        cls,
        evidence_list: Optional[List[EvidenceObject]] = None,
        distribution_shift_score: Optional[float] = None,
        custom_component_scores: Optional[Dict[str, float]] = None,
    ) -> TrustScoreResult:
        """
        Calculates composite trust score based on evidence objects and distribution shift.
        If custom_component_scores are provided, they override the baseline deductions.
        """
        evidence_list = evidence_list or []
        deductions: List[ScorePenalty] = []

        # Start from clean baselines (100.0 each)
        s_data = 100.0
        s_model = 100.0
        s_infer = 100.0
        s_dist = 100.0

        if distribution_shift_score is not None:
            # Shift score is between 0.0 (no shift) and 1.0 (extreme shift)
            clamped_shift = max(0.0, min(1.0, float(distribution_shift_score)))
            s_dist = max(0.0, 100.0 * (1.0 - clamped_shift))
            if clamped_shift > 0.15:
                deductions.append(
                    ScorePenalty(
                        component="distribution",
                        penalty_points=round(100.0 * clamped_shift, 2),
                        reason=f"Distribution shift score detected at {clamped_shift:.3f}",
                    )
                )

        # Process evidence items
        for ev in evidence_list:
            ev_type = (ev.finding_type or "").lower()
            sev = ev.severity
            conf = max(0.1, min(1.0, ev.confidence))

            # Base penalty multiplier by severity
            sev_multiplier = {
                Severity.LOW: 5.0,
                Severity.MEDIUM: 15.0,
                Severity.HIGH: 30.0,
                Severity.CRITICAL: 50.0,
            }.get(sev, 10.0)

            penalty_amount = round(sev_multiplier * conf, 2)

            # 1. Dataset Integrity Findings
            if any(k in ev_type for k in ["duplicate", "label", "corrupt", "dataset", "ood_sample"]):
                if "duplicate" in ev_type:
                    p = min(35.0, penalty_amount)
                    s_data -= p
                    deductions.append(ScorePenalty(component="dataset", penalty_points=p, reason=f"Duplicate flooding: {ev.what_happened}", evidence_id=ev.evidence_id))
                elif "label" in ev_type:
                    p = min(40.0, penalty_amount * 1.2)
                    s_data -= p
                    deductions.append(ScorePenalty(component="dataset", penalty_points=p, reason=f"Label inconsistency: {ev.what_happened}", evidence_id=ev.evidence_id))
                elif "corrupt" in ev_type:
                    p = min(30.0, penalty_amount)
                    s_data -= p
                    deductions.append(ScorePenalty(component="dataset", penalty_points=p, reason=f"Image corruption: {ev.what_happened}", evidence_id=ev.evidence_id))
                elif "ood" in ev_type:
                    p = min(25.0, penalty_amount)
                    s_data -= p
                    deductions.append(ScorePenalty(component="dataset", penalty_points=p, reason=f"OOD injection: {ev.what_happened}", evidence_id=ev.evidence_id))
                else:
                    s_data -= penalty_amount
                    deductions.append(ScorePenalty(component="dataset", penalty_points=penalty_amount, reason=ev.what_happened, evidence_id=ev.evidence_id))

            # 2. Model Integrity Findings
            elif any(k in ev_type for k in ["model", "binary", "trigger", "architecture", "fingerprint"]):
                if "binary difference" in ev_type or "substitution" in ev_type or "mismatch" in ev_type:
                    # Model substitution drops model integrity completely
                    p = 100.0
                    s_model = 0.0
                    deductions.append(ScorePenalty(component="model", penalty_points=p, reason="MODEL BINARY DIFFERENCE: Unverified model binary substitution", evidence_id=ev.evidence_id))
                elif "trigger" in ev_type:
                    p = min(40.0, penalty_amount * 1.3)
                    s_model -= p
                    deductions.append(ScorePenalty(component="model", penalty_points=p, reason=f"Trigger sensitivity: {ev.what_happened}", evidence_id=ev.evidence_id))
                else:
                    s_model -= penalty_amount
                    deductions.append(ScorePenalty(component="model", penalty_points=penalty_amount, reason=ev.what_happened, evidence_id=ev.evidence_id))

            # 3. Inference Integrity Findings
            elif any(k in ev_type for k in ["inference", "tamper", "replay", "nonce", "sequence", "hash"]):
                if "tamper" in ev_type or "cryptographic" in ev_type:
                    p = 100.0
                    s_infer = 0.0
                    deductions.append(ScorePenalty(component="inference", penalty_points=p, reason="Inference record cryptographic violation: hash mismatch", evidence_id=ev.evidence_id))
                elif "replay" in ev_type or "nonce" in ev_type or "sequence" in ev_type:
                    p = min(60.0, penalty_amount * 1.5)
                    s_infer -= p
                    deductions.append(ScorePenalty(component="inference", penalty_points=p, reason=f"Replay attack / sequence violation: {ev.what_happened}", evidence_id=ev.evidence_id))
                else:
                    s_infer -= penalty_amount
                    deductions.append(ScorePenalty(component="inference", penalty_points=penalty_amount, reason=ev.what_happened, evidence_id=ev.evidence_id))

            # 4. Distribution Shift Findings
            elif "distribution" in ev_type or "shift" in ev_type:
                p = min(50.0, penalty_amount)
                s_dist -= p
                deductions.append(ScorePenalty(component="distribution", penalty_points=p, reason=f"Distribution shift: {ev.what_happened}", evidence_id=ev.evidence_id))

        # Clamp component scores to [0.0, 100.0]
        s_data = max(0.0, min(100.0, s_data))
        s_model = max(0.0, min(100.0, s_model))
        s_infer = max(0.0, min(100.0, s_infer))
        s_dist = max(0.0, min(100.0, s_dist))

        # Allow explicit override if requested
        if custom_component_scores:
            if "dataset_integrity" in custom_component_scores:
                s_data = max(0.0, min(100.0, custom_component_scores["dataset_integrity"]))
            if "model_integrity" in custom_component_scores:
                s_model = max(0.0, min(100.0, custom_component_scores["model_integrity"]))
            if "inference_integrity" in custom_component_scores:
                s_infer = max(0.0, min(100.0, custom_component_scores["inference_integrity"]))
            if "distribution_stability" in custom_component_scores:
                s_dist = max(0.0, min(100.0, custom_component_scores["distribution_stability"]))

        # Weighted calculation
        w_data = cls.WEIGHTS["dataset_integrity"]
        w_model = cls.WEIGHTS["model_integrity"]
        w_infer = cls.WEIGHTS["inference_integrity"]
        w_dist = cls.WEIGHTS["distribution_stability"]

        overall = (w_data * s_data) + (w_model * s_model) + (w_infer * s_infer) + (w_dist * s_dist)
        overall = round(max(0.0, min(100.0, overall)), 2)

        risk_band, status_label, status_color = cls.evaluate_risk_band(overall)

        formula_breakdown = (
            f"Trust Score = ({w_data:.2f} * {s_data:.1f}) + ({w_model:.2f} * {s_model:.1f}) + "
            f"({w_infer:.2f} * {s_infer:.1f}) + ({w_dist:.2f} * {s_dist:.1f}) = {overall:.2f} [{status_label}]"
        )

        summary = (
            f"Composite Trust Score: {overall:.2f}/100 ({status_label}). "
            f"Component breakdown: Dataset={s_data:.1f}, Model={s_model:.1f}, "
            f"Inference={s_infer:.1f}, Distribution={s_dist:.1f}."
        )

        return TrustScoreResult(
            overall_score=overall,
            risk_band=risk_band,
            status_label=status_label,
            status_color=status_color,
            component_scores=ComponentScores(
                dataset_integrity=round(s_data, 2),
                model_integrity=round(s_model, 2),
                inference_integrity=round(s_infer, 2),
                distribution_stability=round(s_dist, 2),
            ),
            weights=cls.WEIGHTS,
            deductions=deductions,
            formula_breakdown=formula_breakdown,
            summary=summary,
        )
