"""
TrustLens Distribution Shift Analyzer
Conforms strictly to Section 19 of the TrustLens specification.

Compares reference vs current datasets on brightness stats, quality stats,
embeddings, cosine distance, and Wasserstein distance.
Generates output conforming to Section 19 string format and limitations.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Any, Optional, Union
import math
import numpy as np
from PIL import Image

from app.risk.schemas import EvidenceObject, Severity, Disposition


@dataclass
class DatasetStats:
    sample_count: int
    mean_brightness: float
    std_brightness: float
    contrast: float
    blur_score: float  # High = sharp, Low = blurred
    mean_embedding: List[float] = field(default_factory=list)
    raw_brightness_values: List[float] = field(default_factory=list)
    raw_contrast_values: List[float] = field(default_factory=list)


@dataclass
class DistributionShiftResult:
    reference_stats: DatasetStats
    current_stats: DatasetStats
    shift_score: float  # 0.00 to 1.00
    wasserstein_distance: float
    cosine_distance: float
    interpretation: str
    limitation: str
    section_19_formatted_text: str
    evidence_object: Optional[EvidenceObject] = None


class DistributionShiftAnalyzer:
    """
    Analyzes covariate and visual distribution shifts between a reference dataset
    and a newly observed / current dataset.
    """

    LIMITATION_DISCLAIMER = (
        "Statistical distribution shifts may reflect natural domain/lighting variations, "
        "sensor degradation, or operational shifts; they do not by themselves establish malicious intent."
    )

    @classmethod
    def _compute_wasserstein_1d(cls, u: List[float], v: List[float]) -> float:
        """Computes 1D Wasserstein distance between two scalar distributions."""
        if not u or not v:
            return 0.0
        try:
            from scipy.stats import wasserstein_distance
            return float(wasserstein_distance(u, v))
        except ImportError:
            # Fallback numpy CDF integration
            all_vals = np.sort(np.unique(np.concatenate([u, v])))
            u_cdf = np.searchsorted(np.sort(u), all_vals, side="right") / len(u)
            v_cdf = np.searchsorted(np.sort(v), all_vals, side="right") / len(v)
            diffs = np.diff(all_vals)
            return float(np.sum(np.abs(u_cdf[:-1] - v_cdf[:-1]) * diffs))

    @classmethod
    def _compute_cosine_distance(cls, vec_a: List[float], vec_b: List[float]) -> float:
        """Computes cosine distance (1.0 - cosine_similarity)."""
        if not vec_a or not vec_b or len(vec_a) != len(vec_b):
            return 0.0
        a = np.array(vec_a, dtype=float)
        b = np.array(vec_b, dtype=float)
        norm_a = np.linalg.norm(a)
        norm_b = np.linalg.norm(b)
        if norm_a == 0 or norm_b == 0:
            return 0.0
        cos_sim = np.dot(a, b) / (norm_a * norm_b)
        # Cosine distance bounded in [0.0, 2.0], typically [0.0, 1.0] for non-negative features
        cos_dist = 1.0 - max(-1.0, min(1.0, float(cos_sim)))
        return max(0.0, min(1.0, cos_dist))

    @classmethod
    def extract_image_features(cls, image_input: Union[str, Path, np.ndarray, Image.Image]) -> Dict[str, Any]:
        """
        Extracts statistical and visual characteristics from a single image.
        Supports file path, PIL Image, or numpy array.
        """
        if isinstance(image_input, (str, Path)):
            img = Image.open(image_input).convert("RGB")
            arr = np.array(img, dtype=float)
        elif isinstance(image_input, Image.Image):
            img = image_input.convert("RGB")
            arr = np.array(img, dtype=float)
        elif isinstance(image_input, np.ndarray):
            arr = image_input.astype(float)
            if arr.ndim == 2:
                arr = np.stack([arr] * 3, axis=-1)
        else:
            raise ValueError(f"Unsupported image input type: {type(image_input)}")

        # Grayscale representation for luminance & sharpness
        gray = 0.2989 * arr[:, :, 0] + 0.5870 * arr[:, :, 1] + 0.1140 * arr[:, :, 2]

        brightness = float(np.mean(gray))
        contrast = float(np.std(gray))

        # Discrete 2D Laplacian approximation for blur/sharpness score
        if gray.shape[0] >= 3 and gray.shape[1] >= 3:
            laplacian = (
                -4 * gray[1:-1, 1:-1]
                + gray[:-2, 1:-1]
                + gray[2:, 1:-1]
                + gray[1:-1, :-2]
                + gray[1:-1, 2:]
            )
            blur_score = float(np.var(laplacian))
        else:
            blur_score = 100.0

        # Feature embedding representation: 16-bin normalized color/spatial histogram
        r_hist, _ = np.histogram(arr[:, :, 0], bins=8, range=(0, 256), density=True)
        g_hist, _ = np.histogram(arr[:, :, 1], bins=8, range=(0, 256), density=True)
        b_hist, _ = np.histogram(arr[:, :, 2], bins=8, range=(0, 256), density=True)
        embedding = np.concatenate([r_hist, g_hist, b_hist]).tolist()

        return {
            "brightness": brightness,
            "contrast": contrast,
            "blur_score": blur_score,
            "embedding": embedding,
        }

    @classmethod
    def calculate_dataset_stats(cls, images_or_features: List[Union[str, Path, np.ndarray, Image.Image, Dict[str, Any]]]) -> DatasetStats:
        """Computes aggregate statistical distribution for an entire collection of images."""
        if not images_or_features:
            return DatasetStats(0, 0.0, 0.0, 0.0, 0.0, [], [], [])

        brightness_list: List[float] = []
        contrast_list: List[float] = []
        blur_list: List[float] = []
        embedding_matrix: List[List[float]] = []

        for item in images_or_features:
            if isinstance(item, dict) and "brightness" in item:
                feats = item
            else:
                feats = cls.extract_image_features(item)

            brightness_list.append(feats["brightness"])
            contrast_list.append(feats["contrast"])
            blur_list.append(feats["blur_score"])
            if feats.get("embedding"):
                embedding_matrix.append(feats["embedding"])

        mean_emb = (
            np.mean(embedding_matrix, axis=0).tolist()
            if embedding_matrix
            else []
        )

        return DatasetStats(
            sample_count=len(brightness_list),
            mean_brightness=float(np.mean(brightness_list)),
            std_brightness=float(np.std(brightness_list)),
            contrast=float(np.mean(contrast_list)),
            blur_score=float(np.mean(blur_list)),
            mean_embedding=mean_emb,
            raw_brightness_values=brightness_list,
            raw_contrast_values=contrast_list,
        )

    @classmethod
    def analyze_shift(
        cls,
        reference_data: Union[DatasetStats, List[Any]],
        current_data: Union[DatasetStats, List[Any]],
        dataset_name: str = "Dataset_Alpha",
    ) -> DistributionShiftResult:
        """
        Compares reference dataset vs current dataset.
        Returns full Section 19 structured output and evidence object.
        """
        ref_stats = reference_data if isinstance(reference_data, DatasetStats) else cls.calculate_dataset_stats(reference_data)
        cur_stats = current_data if isinstance(current_data, DatasetStats) else cls.calculate_dataset_stats(current_data)

        # 1. Wasserstein distance on brightness (normalized by max pixel range 255.0)
        raw_w_dist = cls._compute_wasserstein_1d(
            ref_stats.raw_brightness_values, cur_stats.raw_brightness_values
        )
        norm_w_dist = min(1.0, raw_w_dist / 255.0)

        # 2. Cosine distance on mean feature embeddings
        cos_dist = cls._compute_cosine_distance(
            ref_stats.mean_embedding, cur_stats.mean_embedding
        )

        # 3. Normalized blur and contrast divergence
        contrast_diff = abs(ref_stats.contrast - cur_stats.contrast) / max(1.0, ref_stats.contrast)
        contrast_penalty = min(1.0, contrast_diff)

        # Composite shift score in [0.0, 1.0]
        # 50% Wasserstein on luminance, 30% embedding Cosine distance, 20% contrast divergence
        composite_shift = round(
            (0.50 * norm_w_dist) + (0.30 * cos_dist) + (0.20 * contrast_penalty), 3
        )
        composite_shift = max(0.0, min(1.0, composite_shift))

        # Interpretation based on shift score magnitude
        if composite_shift < 0.15:
            interpretation = "Minimal distribution drift detected; current data is statistically consistent with reference distribution."
            severity = Severity.LOW
        elif composite_shift < 0.35:
            interpretation = "Low-to-moderate distribution shift observed across illumination and dynamic range metrics."
            severity = Severity.MEDIUM
        elif composite_shift < 0.60:
            interpretation = "Substantial distribution divergence observed in feature space and luminance statistics."
            severity = Severity.HIGH
        else:
            interpretation = "Severe distribution shift / anomalous domain deviation detected between datasets."
            severity = Severity.CRITICAL

        # Section 19 exact text output format
        formatted_text = (
            f"REFERENCE: mean_brightness={ref_stats.mean_brightness:.2f}, "
            f"std_brightness={ref_stats.std_brightness:.2f}, "
            f"contrast={ref_stats.contrast:.2f}, blur_score={ref_stats.blur_score:.2f}\n"
            f"CURRENT:   mean_brightness={cur_stats.mean_brightness:.2f}, "
            f"std_brightness={cur_stats.std_brightness:.2f}, "
            f"contrast={cur_stats.contrast:.2f}, blur_score={cur_stats.blur_score:.2f}\n"
            f"SHIFT SCORE: {composite_shift:.3f} (Wasserstein={norm_w_dist:.3f}, Cosine={cos_dist:.3f})\n"
            f"INTERPRETATION: {interpretation}\n"
            f"LIMITATION: {cls.LIMITATION_DISCLAIMER}"
        )

        # Evidence object generation
        evidence_obj: Optional[EvidenceObject] = None
        if composite_shift >= 0.15:
            evidence_obj = EvidenceObject(
                finding_type="Statistical distribution shift",
                what_happened=(
                    f"Current dataset diverged from baseline with composite shift score of {composite_shift:.3f} "
                    f"(Wasserstein: {norm_w_dist:.3f}, Cosine: {cos_dist:.3f})."
                ),
                why_flagged=(
                    f"The statistical distance between the baseline dataset distribution and current samples "
                    f"exceeds tolerance thresholds (contrast delta: {contrast_diff:.2%})."
                ),
                evidence=[
                    {
                        "metric": "Wasserstein_distance_normalized",
                        "value": round(norm_w_dist, 4),
                    },
                    {
                        "metric": "Cosine_distance_embeddings",
                        "value": round(cos_dist, 4),
                    },
                    {
                        "metric": "Reference_brightness_mean",
                        "value": round(ref_stats.mean_brightness, 2),
                    },
                    {
                        "metric": "Current_brightness_mean",
                        "value": round(cur_stats.mean_brightness, 2),
                    },
                ],
                severity=severity,
                confidence=min(0.95, round(0.50 + (composite_shift * 0.45), 2)),
                affected_asset=dataset_name,
                recommended_action=(
                    "Review environmental changes, camera calibration, or data collection shifts; "
                    "re-validate model accuracy on current distribution before deployment."
                ),
                limitations=cls.LIMITATION_DISCLAIMER,
                disposition=Disposition.REVIEW if severity in [Severity.MEDIUM, Severity.HIGH] else Disposition.QUARANTINE,
            )

        return DistributionShiftResult(
            reference_stats=ref_stats,
            current_stats=cur_stats,
            shift_score=composite_shift,
            wasserstein_distance=round(norm_w_dist, 4),
            cosine_distance=round(cos_dist, 4),
            interpretation=interpretation,
            limitation=cls.LIMITATION_DISCLAIMER,
            section_19_formatted_text=formatted_text,
            evidence_object=evidence_obj,
        )
