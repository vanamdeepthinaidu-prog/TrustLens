"""TrustLens Per-Image Forensic Analyzer

Extracts cryptographic and perceptual hashes, dimensions, statistical visual
metrics (brightness, contrast, blur score), and validates file integrity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional
import numpy as np
from PIL import Image, ImageOps
from scipy.signal import convolve2d
import imagehash

from app.core.hashing import hash_file
from app.schemas.cv import ImageAnalysisResult, PerceptualHashes


# Standard 3x3 discrete Laplacian kernel for sharpness/blur estimation
LAPLACIAN_KERNEL = np.array(
    [[0, 1, 0],
     [1, -4, 1],
     [0, 1, 0]],
    dtype=np.float32
)


def compute_blur_score(gray_array: np.ndarray) -> float:
    """Compute blur/sharpness score using the variance of the 2D Laplacian.
    
    A higher variance indicates sharp, high-frequency edge content.
    A low variance (near 0) indicates a blurry or uniform image.
    """
    if gray_array.size == 0 or gray_array.ndim != 2:
        return 0.0
    try:
        laplacian = convolve2d(gray_array, LAPLACIAN_KERNEL, mode="valid")
        return float(np.var(laplacian))
    except Exception:
        return 0.0


def compute_perceptual_hashes(img: Image.Image) -> PerceptualHashes:
    """Compute DCT pHash, difference dHash, average aHash, and wavelet whash."""
    # Convert image to RGB to handle palette or alpha modes cleanly for hashing
    rgb_img = img.convert("RGB")
    
    phash_val = str(imagehash.phash(rgb_img))
    dhash_val = str(imagehash.dhash(rgb_img))
    ahash_val = str(imagehash.average_hash(rgb_img))
    
    whash_val = None
    try:
        whash_val = str(imagehash.whash(rgb_img))
    except Exception:
        pass

    return PerceptualHashes(
        phash=phash_val,
        dhash=dhash_val,
        ahash=ahash_val,
        whash=whash_val,
    )


def analyze_image(file_path: Path | str) -> ImageAnalysisResult:
    """Perform comprehensive integrity and quality inspection on an image file.

    Args:
        file_path: Path to the target image file.

    Returns:
        ImageAnalysisResult containing hashes, dimensions, quality metrics,
        and integrity validation status.
    """
    path = Path(file_path)
    file_name = path.name

    if not path.is_file():
        return ImageAnalysisResult(
            file_path=str(path),
            file_name=file_name,
            sha256="",
            file_size_bytes=0,
            format="UNKNOWN",
            is_corrupted=True,
            corruption_reason=f"File does not exist: {path}",
        )

    file_size_bytes = path.stat().st_size
    if file_size_bytes == 0:
        return ImageAnalysisResult(
            file_path=str(path),
            file_name=file_name,
            sha256="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            file_size_bytes=0,
            format="EMPTY",
            is_corrupted=True,
            corruption_reason="Empty file (0 bytes)",
        )

    # Compute cryptographic SHA-256
    try:
        sha256_digest = hash_file(path)
    except Exception as e:
        return ImageAnalysisResult(
            file_path=str(path),
            file_name=file_name,
            sha256="",
            file_size_bytes=file_size_bytes,
            format="UNKNOWN",
            is_corrupted=True,
            corruption_reason=f"Error reading file for SHA-256: {e}",
        )

    # Decode and validate image structure
    try:
        with Image.open(path) as raw_img:
            # Check format integrity
            raw_img.verify()
        
        # Re-open after verify() to access pixels (PIL requirement)
        with Image.open(path) as img:
            img.load()
            fmt = img.format or path.suffix.lstrip(".").upper() or "UNKNOWN"
            width, height = img.size
            aspect_ratio = round(width / height, 4) if height > 0 else 0.0

            # Compute perceptual hashes
            perceptual_hashes = compute_perceptual_hashes(img)

            # Convert to grayscale float array for statistical metrics
            gray = ImageOps.grayscale(img)
            gray_arr = np.asarray(gray, dtype=np.float32)

            # Brightness: Mean luminance [0.0 - 255.0]
            brightness = float(np.mean(gray_arr)) if gray_arr.size > 0 else 0.0

            # Contrast: Standard deviation of pixel intensities (RMS contrast)
            contrast = float(np.std(gray_arr)) if gray_arr.size > 0 else 0.0

            # Blur score: Variance of Laplacian
            blur_score = compute_blur_score(gray_arr)

            return ImageAnalysisResult(
                file_path=str(path),
                file_name=file_name,
                sha256=sha256_digest,
                perceptual_hashes=perceptual_hashes,
                width=width,
                height=height,
                aspect_ratio=aspect_ratio,
                file_size_bytes=file_size_bytes,
                format=fmt,
                brightness=round(brightness, 2),
                contrast=round(contrast, 2),
                blur_score=round(blur_score, 2),
                is_corrupted=False,
                corruption_reason=None,
            )

    except Exception as e:
        return ImageAnalysisResult(
            file_path=str(path),
            file_name=file_name,
            sha256=sha256_digest,
            perceptual_hashes=None,
            width=0,
            height=0,
            aspect_ratio=0.0,
            file_size_bytes=file_size_bytes,
            format="CORRUPTED",
            brightness=0.0,
            contrast=0.0,
            blur_score=0.0,
            is_corrupted=True,
            corruption_reason=f"Corrupted or unsupported image file: {type(e).__name__}: {str(e)}",
        )
