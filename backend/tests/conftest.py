"""TrustLens PyTest Configuration and Synthetic Fixtures

Generates controlled synthetic test sets for image analysis, duplicate flooding,
OOD anomaly detection, label consistency, and multi-format loaders.
"""

from __future__ import annotations

import csv
import shutil
import tempfile
from pathlib import Path
import pytest
import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def make_test_image(
    color: tuple[int, int, int] = (128, 128, 128),
    shape: str = "rect",
    size: tuple[int, int] = (100, 100),
) -> Image.Image:
    """Create a synthetic test image with a specific shape and color."""
    img = Image.new("RGB", size, color=(240, 240, 240))
    draw = ImageDraw.Draw(img)
    if shape == "rect":
        draw.rectangle([20, 20, 80, 80], fill=color, outline=(0, 0, 0))
    elif shape == "circle":
        draw.ellipse([20, 20, 80, 80], fill=color, outline=(0, 0, 0))
    elif shape == "triangle":
        draw.polygon([(50, 15), (20, 85), (80, 85)], fill=color, outline=(0, 0, 0))
    elif shape == "cross":
        draw.rectangle([40, 10, 60, 90], fill=color)
        draw.rectangle([10, 40, 90, 60], fill=color)
    return img


@pytest.fixture
def temp_workspace():
    """Temporary directory for test artifacts cleaned up automatically."""
    tmp_dir = Path(tempfile.mkdtemp(prefix="trustlens_test_"))
    yield tmp_dir
    shutil.rmtree(tmp_dir, ignore_errors=True)


@pytest.fixture
def synthetic_folder_dataset(temp_workspace: Path) -> Path:
    """Creates a folder dataset containing:
    - 3 unique clean images
    - 1 exact duplicate (identical copy)
    - 1 near-duplicate (blurred/compressed copy)
    - 1 corrupted non-image file
    - 1 empty 0-byte file
    """
    dataset_dir = temp_workspace / "sample_folder_dataset"
    dataset_dir.mkdir(parents=True, exist_ok=True)

    # Base images
    img1 = make_test_image(color=(220, 30, 30), shape="circle")
    img1_path = dataset_dir / "img_01.jpg"
    img1.save(img1_path, "JPEG", quality=95)

    img2 = make_test_image(color=(30, 220, 30), shape="rect")
    img2_path = dataset_dir / "img_02.jpg"
    img2.save(img2_path, "JPEG", quality=95)

    img3 = make_test_image(color=(30, 30, 220), shape="triangle")
    img3_path = dataset_dir / "img_03.jpg"
    img3.save(img3_path, "JPEG", quality=95)

    # Exact duplicate of img1
    exact_dup_path = dataset_dir / "img_01_exact_copy.jpg"
    shutil.copyfile(img1_path, exact_dup_path)

    # Near-duplicate of img1 (slightly blurred version)
    near_dup = img1.filter(ImageFilter.GaussianBlur(radius=1.5))
    near_dup_path = dataset_dir / "img_01_near_dup.jpg"
    near_dup.save(near_dup_path, "JPEG", quality=85)

    # Corrupted file
    corrupt_path = dataset_dir / "corrupted.jpg"
    corrupt_path.write_bytes(b"NOT_A_JPEG_FILE_HEADER_GARBAGE_BYTES_12345")

    # Empty file
    empty_path = dataset_dir / "empty.jpg"
    empty_path.touch()

    return dataset_dir


@pytest.fixture
def synthetic_csv_dataset(temp_workspace: Path) -> Path:
    """Creates a dataset with metadata.csv containing 10 samples across 2 classes,
    with 1 sample intentionally mislabeled (Class B visual features, but labeled Class A).
    """
    csv_dir = temp_workspace / "sample_csv_dataset"
    csv_dir.mkdir(parents=True, exist_ok=True)
    images_dir = csv_dir / "images"
    images_dir.mkdir()

    rows = []

    # Class 'red_circle' (5 samples)
    for i in range(5):
        img = make_test_image(color=(240, 20 + i * 5, 20), shape="circle")
        filename = f"red_{i:02d}.png"
        img.save(images_dir / filename)
        rows.append({"image": f"images/{filename}", "label": "red_circle"})

    # Class 'blue_square' (5 samples)
    for i in range(5):
        img = make_test_image(color=(20, 20, 240 - i * 5), shape="rect")
        filename = f"blue_{i:02d}.png"
        img.save(images_dir / filename)
        # Sample 4 is INTENTIONALLY mislabeled as 'red_circle' to test label consistency
        assigned_label = "red_circle" if i == 4 else "blue_square"
        rows.append({"image": f"images/{filename}", "label": assigned_label})

    # Write metadata.csv
    csv_file = csv_dir / "metadata.csv"
    with csv_file.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["image", "label"])
        writer.writeheader()
        writer.writerows(rows)

    return csv_dir


@pytest.fixture
def synthetic_yolo_dataset(temp_workspace: Path) -> Path:
    """Creates a simple YOLO-style dataset with images/ and labels/ directories."""
    yolo_dir = temp_workspace / "sample_yolo_dataset"
    yolo_dir.mkdir(parents=True, exist_ok=True)
    images_dir = yolo_dir / "images"
    labels_dir = yolo_dir / "labels"
    images_dir.mkdir()
    labels_dir.mkdir()

    # Write classes.txt
    classes_file = yolo_dir / "classes.txt"
    classes_file.write_text("drone\nvehicle\npedestrian\n", encoding="utf-8")

    # Sample 1: drone
    img1 = make_test_image(color=(100, 100, 255), shape="cross")
    img1.save(images_dir / "sample_01.jpg")
    (labels_dir / "sample_01.txt").write_text("0 0.5 0.5 0.6 0.6\n", encoding="utf-8")

    # Sample 2: vehicle
    img2 = make_test_image(color=(255, 100, 100), shape="rect")
    img2.save(images_dir / "sample_02.jpg")
    (labels_dir / "sample_02.txt").write_text("1 0.4 0.4 0.5 0.5\n", encoding="utf-8")

    return yolo_dir
