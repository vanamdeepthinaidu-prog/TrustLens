"""Unit Tests for Label Consistency Detection Engine"""

import numpy as np
from app.analytics.label_consistency import check_label_consistency
from app.schemas.dataset import DatasetSample


def test_label_consistency_detects_mislabeled_sample():
    np.random.seed(42)

    # 10 samples of Class A (centered at +2.0)
    class_a_embs = np.random.normal(loc=2.0, scale=0.1, size=(10, 512)).astype(np.float32)
    # 10 samples of Class B (centered at -2.0)
    class_b_embs = np.random.normal(loc=-2.0, scale=0.1, size=(10, 512)).astype(np.float32)

    all_embs = np.vstack([class_a_embs, class_b_embs])
    all_embs = all_embs / np.linalg.norm(all_embs, axis=1, keepdims=True)

    samples = []
    # Add Class A samples
    for i in range(10):
        samples.append(
            DatasetSample(sample_id=f"SA-{i}", file_path=f"path/to/a_{i}.jpg", label="ClassA")
        )

    # Add Class B samples, but intentionally mislabel the LAST one as 'ClassA'
    for i in range(10):
        assigned_label = "ClassA" if i == 9 else "ClassB"
        samples.append(
            DatasetSample(sample_id=f"SB-{i}", file_path=f"path/to/b_{i}.jpg", label=assigned_label)
        )

    findings = check_label_consistency(all_embs, samples, k=5, inconsistency_threshold=0.60)

    # Should detect the mislabeled sample (SB-9)
    assert len(findings) >= 1
    flagged = next((f for f in findings if f.sample_id == "SB-9"), None)
    assert flagged is not None
    assert flagged.current_label == "ClassA"
    assert flagged.suggested_label == "ClassB"
    assert flagged.consensus_ratio >= 0.80

    # Verify strict Section 11 reporting tone
    assert flagged.finding == "Potential label inconsistency"
    assert "poisoned" not in flagged.finding.lower()


def test_consistent_dataset_no_false_positives():
    np.random.seed(42)

    class_a = np.random.normal(loc=3.0, scale=0.1, size=(8, 512)).astype(np.float32)
    class_b = np.random.normal(loc=-3.0, scale=0.1, size=(8, 512)).astype(np.float32)

    embs = np.vstack([class_a, class_b])
    embs = embs / np.linalg.norm(embs, axis=1, keepdims=True)

    samples = [
        DatasetSample(sample_id=f"A-{i}", file_path=f"a_{i}.png", label="ClassA")
        for i in range(8)
    ] + [
        DatasetSample(sample_id=f"B-{i}", file_path=f"b_{i}.png", label="ClassB")
        for i in range(8)
    ]

    findings = check_label_consistency(embs, samples, k=3, inconsistency_threshold=0.60)
    assert len(findings) == 0
