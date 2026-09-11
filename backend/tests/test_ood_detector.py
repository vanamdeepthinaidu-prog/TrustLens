"""Unit Tests for Out-Of-Distribution (OOD) Anomaly Detection Engine"""

import numpy as np
from app.analytics.ood_detector import detect_ood
from app.schemas.dataset import DatasetSample
from app.schemas.evidence import SeverityEnum


def test_ood_detects_distribution_outlier():
    np.random.seed(42)

    # 20 inlier points clustered around [1.0, 1.0, ...]
    inliers = np.random.normal(loc=1.0, scale=0.05, size=(20, 512)).astype(np.float32)
    # 1 severe outlier clustered around [-3.0, -3.0, ...]
    outlier = np.random.normal(loc=-3.0, scale=0.05, size=(1, 512)).astype(np.float32)

    embeddings = np.vstack([inliers, outlier])
    # L2-normalize
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

    samples = [
        DatasetSample(sample_id=f"S-{i:03d}", file_path=f"path/to/img_{i}.jpg", label="nominal")
        for i in range(21)
    ]

    result = detect_ood(embeddings, samples, contamination=0.05)

    assert result.total_evaluated == 21
    assert result.anomalies_detected >= 1

    outlier_res = result.samples[20]
    inlier_mean_score = np.mean([s.ood_score for s in result.samples[:20]])

    assert outlier_res.ood_score > inlier_mean_score
    assert outlier_res.severity in [SeverityEnum.CRITICAL, SeverityEnum.HIGH]


def test_ood_section_10_conservative_tone():
    embeddings = np.random.normal(loc=0.0, scale=1.0, size=(10, 512)).astype(np.float32)
    embeddings = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
    samples = [
        DatasetSample(sample_id=f"S-{i:03d}", file_path=f"path/to/img_{i}.jpg", label="test")
        for i in range(10)
    ]

    result = detect_ood(embeddings, samples)

    # Check tone requirements from Section 10
    for sample in result.samples:
        assert "Sample features deviate significantly from the baseline distribution." in sample.limitation_note
        assert "does not definitively prove malicious poisoning or corruption." in sample.limitation_note

    assert "OOD scores measure" in result.summary_limitation
