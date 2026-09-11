"""TrustLens Out-Of-Distribution (OOD) & Anomaly Detection Engine

Applies Isolation Forest ensemble and centroid geometric distance analysis
to feature embeddings, outputting normalized 0–1 anomaly scores with
Section 10 non-adversarial reporting language.
"""

from __future__ import annotations

from typing import List
import numpy as np
from sklearn.ensemble import IsolationForest

from app.schemas.cv import OODAnalysisResult, OODSampleScore
from app.schemas.dataset import DatasetSample
from app.schemas.evidence import SeverityEnum


SECTION_10_LIMITATION_NOTE = (
    "Sample features deviate significantly from the baseline distribution. "
    "This indicates atypical visual features or potential out-of-distribution domain shift, "
    "but does not definitively prove malicious poisoning or corruption."
)

SECTION_10_SUMMARY_LIMITATION = (
    "OOD scores measure statistical feature deviation within the embedding space. "
    "Unusual lighting, camera angles, rare visual objects, or legitimate edge cases "
    "may yield elevated anomaly scores without indicating adversarial tampering."
)


def score_to_severity(score: float) -> SeverityEnum:
    """Map normalized OOD score [0.0 - 1.0] to standard severity level."""
    if score >= 0.80:
        return SeverityEnum.CRITICAL
    if score >= 0.65:
        return SeverityEnum.HIGH
    if score >= 0.45:
        return SeverityEnum.MEDIUM
    return SeverityEnum.LOW


def detect_ood(
    embeddings: np.ndarray,
    samples: List[DatasetSample],
    contamination: float = 0.08,
    random_state: int = 42,
) -> OODAnalysisResult:
    """Analyze embedding distribution to detect out-of-distribution anomalies.

    Args:
        embeddings: 2D numpy array of shape (N, D) representing visual feature vectors.
        samples: Corresponding list of DatasetSample records.
        contamination: Anticipated fraction of outliers in the dataset [0.01 - 0.40].
        random_state: Deterministic random seed for reproducibility.

    Returns:
        OODAnalysisResult containing per-sample scores, severity, and Section 10 tone.
    """
    n_samples, n_features = embeddings.shape
    if n_samples == 0 or len(samples) != n_samples:
        return OODAnalysisResult(
            total_evaluated=0,
            anomalies_detected=0,
            contamination_rate=contamination,
            samples=[],
            summary_limitation=SECTION_10_SUMMARY_LIMITATION,
        )

    # Edge-case: Too few samples for Isolation Forest
    if n_samples < 4:
        sample_scores = [
            OODSampleScore(
                sample_id=s.sample_id,
                file_path=s.file_path,
                ood_score=0.10,
                distance_to_centroid=0.0,
                isolation_score=0.0,
                severity=SeverityEnum.LOW,
                is_outlier=False,
                limitation_note="Insufficient sample population for statistical OOD assessment.",
            )
            for s in samples
        ]
        return OODAnalysisResult(
            total_evaluated=n_samples,
            anomalies_detected=0,
            contamination_rate=contamination,
            samples=sample_scores,
            summary_limitation=SECTION_10_SUMMARY_LIMITATION,
        )

    # 1. Isolation Forest Scoring
    safe_contamination = max(0.01, min(0.35, contamination))
    clf = IsolationForest(
        contamination=safe_contamination,
        random_state=random_state,
        n_estimators=100,
    )
    clf.fit(embeddings)
    raw_decisions = clf.decision_function(embeddings)  # Lower values = more anomalous
    predictions = clf.predict(embeddings)              # -1 for outliers, 1 for inliers

    # Normalize Isolation Forest decision values to [0.0, 1.0] where 1.0 = most anomalous
    min_d, max_d = float(np.min(raw_decisions)), float(np.max(raw_decisions))
    range_d = max_d - min_d
    if range_d > 1e-7:
        iso_scores = (max_d - raw_decisions) / range_d
    else:
        iso_scores = np.zeros(n_samples, dtype=np.float32)

    # 2. Geometric Centroid Distance
    centroid = np.mean(embeddings, axis=0, keepdims=True)  # (1, D)
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    c_norm = np.linalg.norm(centroid)
    if c_norm > 1e-7:
        # Cosine distance to dataset center
        dot_products = np.sum(embeddings * centroid, axis=1) / (norms.squeeze() * c_norm + 1e-7)
        cosine_dists = np.clip(1.0 - dot_products, 0.0, 2.0)
    else:
        cosine_dists = np.zeros(n_samples, dtype=np.float32)

    min_cd, max_cd = float(np.min(cosine_dists)), float(np.max(cosine_dists))
    range_cd = max_cd - min_cd
    if range_cd > 1e-7:
        dist_scores = (cosine_dists - min_cd) / range_cd
    else:
        dist_scores = np.zeros(n_samples, dtype=np.float32)

    # 3. Weighted Blend: 60% Isolation Forest + 40% Centroid Distance
    blended_scores = 0.60 * iso_scores + 0.40 * dist_scores
    blended_scores = np.clip(blended_scores, 0.0, 1.0)

    sample_results: List[OODSampleScore] = []
    anomalies_count = 0

    for i in range(n_samples):
        final_score = float(blended_scores[i])
        is_outlier = bool(predictions[i] == -1 or final_score >= 0.70)
        if is_outlier:
            anomalies_count += 1

        sample_results.append(
            OODSampleScore(
                sample_id=samples[i].sample_id,
                file_path=samples[i].file_path,
                ood_score=round(final_score, 4),
                distance_to_centroid=round(float(cosine_dists[i]), 4),
                isolation_score=round(float(raw_decisions[i]), 4),
                severity=score_to_severity(final_score),
                is_outlier=is_outlier,
                limitation_note=SECTION_10_LIMITATION_NOTE,
            )
        )

    return OODAnalysisResult(
        total_evaluated=n_samples,
        anomalies_detected=anomalies_count,
        contamination_rate=safe_contamination,
        samples=sample_results,
        summary_limitation=SECTION_10_SUMMARY_LIMITATION,
    )
