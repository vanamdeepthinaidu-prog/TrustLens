"""Unit Tests for Per-Image Forensic Analyzer"""

from pathlib import Path
from PIL import Image, ImageFilter
from app.cv.image_analyzer import analyze_image


def test_analyze_valid_image(temp_workspace: Path):
    img = Image.new("RGB", (200, 100), color=(180, 180, 180))
    img_path = temp_workspace / "valid.jpg"
    img.save(img_path, "JPEG")

    result = analyze_image(img_path)

    assert result.is_corrupted is False
    assert result.file_name == "valid.jpg"
    assert result.width == 200
    assert result.height == 100
    assert result.aspect_ratio == 2.0
    assert len(result.sha256) == 64
    assert result.perceptual_hashes is not None
    assert result.perceptual_hashes.phash is not None
    assert result.perceptual_hashes.dhash is not None
    assert result.perceptual_hashes.ahash is not None
    assert result.brightness > 0.0
    assert result.format in ["JPEG", "MPO"]


def test_brightness_metrics(temp_workspace: Path):
    dark_img = Image.new("RGB", (100, 100), color=(20, 20, 20))
    dark_path = temp_workspace / "dark.png"
    dark_img.save(dark_path)

    bright_img = Image.new("RGB", (100, 100), color=(230, 230, 230))
    bright_path = temp_workspace / "bright.png"
    bright_img.save(bright_path)

    res_dark = analyze_image(dark_path)
    res_bright = analyze_image(bright_path)

    assert res_bright.brightness > res_dark.brightness
    assert res_bright.brightness > 200.0
    assert res_dark.brightness < 50.0


def test_sharpness_blur_metrics(temp_workspace: Path):
    # Sharp patterned image
    sharp_img = Image.new("RGB", (100, 100), color=(255, 255, 255))
    for x in range(0, 100, 10):
        for y in range(0, 100, 10):
            if (x + y) % 20 == 0:
                for dx in range(10):
                    for dy in range(10):
                        sharp_img.putpixel((x + dx, y + dy), (0, 0, 0))

    sharp_path = temp_workspace / "sharp.png"
    sharp_img.save(sharp_path)

    # Blur the same image
    blurred_img = sharp_img.filter(ImageFilter.GaussianBlur(radius=3.0))
    blurred_path = temp_workspace / "blurred.png"
    blurred_img.save(blurred_path)

    res_sharp = analyze_image(sharp_path)
    res_blurred = analyze_image(blurred_path)

    assert res_sharp.blur_score > res_blurred.blur_score


def test_corrupted_image_detection(temp_workspace: Path):
    corrupt_file = temp_workspace / "bad_image.jpg"
    corrupt_file.write_bytes(b"\xFF\xD8\xFF\xE0_TRUNCATED_CORRUPTED_HEADER_DATA")

    result = analyze_image(corrupt_file)

    assert result.is_corrupted is True
    assert result.corruption_reason is not None
    assert len(result.sha256) == 64  # SHA-256 is still computed for forensic logging


def test_empty_image_file(temp_workspace: Path):
    empty_file = temp_workspace / "empty.png"
    empty_file.touch()

    result = analyze_image(empty_file)

    assert result.is_corrupted is True
    assert result.file_size_bytes == 0
    assert "Empty" in (result.corruption_reason or "")
