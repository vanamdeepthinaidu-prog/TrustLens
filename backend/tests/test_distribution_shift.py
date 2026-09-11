"""
Unit Tests for DistributionShiftAnalyzer (Section 19)
"""

import numpy as np
from app.analytics.distribution_shift import (
    DistributionShiftAnalyzer,
    DatasetStats,
)


def test_distribution_shift_identical():
    # Same stats
    stats_a = DatasetStats(
        sample_count=50,
        mean_brightness=128.0,
        std_brightness=40.0,
        contrast=50.0,
        blur_score=150.0,
        mean_embedding=[0.2] * 24,
        raw_brightness_values=[128.0] * 50,
    )
    stats_b = DatasetStats(
        sample_count=50,
        mean_brightness=128.0,
        std_brightness=40.0,
        contrast=50.0,
        blur_score=150.0,
        mean_embedding=[0.2] * 24,
        raw_brightness_values=[128.0] * 50,
    )

    res = DistributionShiftAnalyzer.analyze_shift(stats_a, stats_b)
    assert res.shift_score == 0.0
    assert res.wasserstein_distance == 0.0
    assert res.cosine_distance == 0.0
    assert "Minimal distribution drift" in res.interpretation
    assert DistributionShiftAnalyzer.LIMITATION_DISCLAIMER in res.section_19_formatted_text
    assert "REFERENCE:" in res.section_19_formatted_text
    assert "CURRENT:" in res.section_19_formatted_text
    assert "SHIFT SCORE: 0.000" in res.section_19_formatted_text


def test_distribution_shift_divergent():
    # Drastically different brightness and contrast
    stats_ref = DatasetStats(
        sample_count=50,
        mean_brightness=180.0,
        std_brightness=40.0,
        contrast=60.0,
        blur_score=200.0,
        mean_embedding=[0.5] * 24,
        raw_brightness_values=[180.0] * 50,
    )
    stats_cur = DatasetStats(
        sample_count=50,
        mean_brightness=30.0,
        std_brightness=10.0,
        contrast=15.0,
        blur_score=40.0,
        mean_embedding=[0.05] * 24,
        raw_brightness_values=[30.0] * 50,
    )

    res = DistributionShiftAnalyzer.analyze_shift(stats_ref, stats_cur)
    assert res.shift_score > 0.30
    assert res.evidence_object is not None
    assert "Statistical distribution shift" in res.evidence_object.finding_type
    assert DistributionShiftAnalyzer.LIMITATION_DISCLAIMER in res.evidence_object.limitations


def test_feature_extraction_from_array():
    arr = np.ones((32, 32, 3), dtype=np.uint8) * 128
    feats = DistributionShiftAnalyzer.extract_image_features(arr)
    assert "brightness" in feats
    assert "contrast" in feats
    assert "blur_score" in feats
    assert "embedding" in feats
    assert abs(feats["brightness"] - 128.0) < 1.0
