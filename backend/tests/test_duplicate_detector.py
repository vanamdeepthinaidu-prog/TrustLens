"""Unit Tests for Duplicate Detection and Flooding Cluster Grouping"""

from pathlib import Path
from PIL import Image, ImageFilter
from app.cv.image_analyzer import analyze_image
from app.cv.duplicate_detector import detect_duplicates
from app.schemas.cv import DuplicateTypeEnum


def test_exact_duplicate_detection(temp_workspace: Path):
    img = Image.new("RGB", (100, 100), color=(100, 150, 200))
    p1 = temp_workspace / "original.png"
    p2 = temp_workspace / "exact_copy.png"
    img.save(p1)
    img.save(p2)

    res1 = analyze_image(p1)
    res2 = analyze_image(p2)

    dup_results = detect_duplicates([res1, res2], similarity_threshold=0.90)

    assert len(dup_results.clusters) == 1
    cluster = dup_results.clusters[0]
    assert cluster.cluster_size == 2
    assert cluster.indicator == "Potential duplicate flooding indicator"

    types = [d.duplicate_type for d in cluster.duplicates]
    assert DuplicateTypeEnum.EXACT in types
    assert dup_results.exact_duplicate_count >= 1


def test_near_duplicate_detection(temp_workspace: Path):
    img = Image.new("RGB", (120, 120), color=(200, 50, 80))
    p_orig = temp_workspace / "clean.jpg"
    img.save(p_orig, "JPEG", quality=95)

    # Make slightly compressed/blurred variant
    variant = img.filter(ImageFilter.GaussianBlur(radius=0.8))
    p_variant = temp_workspace / "compressed.jpg"
    variant.save(p_variant, "JPEG", quality=75)

    res1 = analyze_image(p_orig)
    res2 = analyze_image(p_variant)

    dup_results = detect_duplicates([res1, res2], similarity_threshold=0.85)

    assert len(dup_results.clusters) == 1
    cluster = dup_results.clusters[0]
    assert cluster.indicator == "Potential duplicate flooding indicator"
    assert any(d.duplicate_type == DuplicateTypeEnum.NEAR_DUPLICATE for d in cluster.duplicates)


def test_distinct_images_no_false_clustering(temp_workspace: Path):
    # Distinct structured shapes
    from tests.conftest import make_test_image
    img1 = make_test_image(color=(220, 30, 30), shape="circle")
    img2 = make_test_image(color=(30, 30, 220), shape="triangle")
    p1 = temp_workspace / "circle.png"
    p2 = temp_workspace / "triangle.png"
    img1.save(p1)
    img2.save(p2)

    res1 = analyze_image(p1)
    res2 = analyze_image(p2)

    dup_results = detect_duplicates([res1, res2], similarity_threshold=0.90)
    assert len(dup_results.clusters) == 0
    assert dup_results.total_duplicate_samples == 0

    # Also test high luminance contrast images (solid black vs solid white)
    black = Image.new("RGB", (100, 100), color=(0, 0, 0))
    white = Image.new("RGB", (100, 100), color=(255, 255, 255))
    pb = temp_workspace / "black.png"
    pw = temp_workspace / "white.png"
    black.save(pb)
    white.save(pw)

    res_b = analyze_image(pb)
    res_w = analyze_image(pw)
    dup_contrast = detect_duplicates([res_b, res_w], similarity_threshold=0.90)
    assert len(dup_contrast.clusters) == 0
