"""TrustLens CV & Dataset Integrity Schemas

Defines Pydantic models for per-image analysis, duplicate clustering,
OOD anomaly scoring, and label consistency detection.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.evidence import SeverityEnum


class PerceptualHashes(BaseModel):
    """Collection of perceptual hashes for an image."""
    phash: str = Field(..., description="DCT-based perceptual hash (hex)")
    dhash: str = Field(..., description="Difference gradient hash (hex)")
    ahash: str = Field(..., description="Average luminance hash (hex)")
    whash: Optional[str] = Field(None, description="Wavelet decomposition hash (hex)")


class ImageAnalysisResult(BaseModel):
    """Complete forensic inspection record for a single image file."""
    file_path: str = Field(..., description="Path to the image file")
    file_name: str = Field(..., description="Filename with extension")
    sha256: str = Field(..., description="Cryptographic SHA-256 digest")
    perceptual_hashes: Optional[PerceptualHashes] = Field(
        None, description="Perceptual hashes (None if file is corrupted)"
    )
    width: int = Field(0, description="Pixel width")
    height: int = Field(0, description="Pixel height")
    aspect_ratio: float = Field(0.0, description="Width / Height aspect ratio")
    file_size_bytes: int = Field(..., description="File size on disk in bytes")
    format: str = Field(..., description="Image file format, e.g. JPEG, PNG, WEBP")
    brightness: float = Field(0.0, description="Mean luminance [0.0 - 255.0]")
    contrast: float = Field(0.0, description="RMS contrast / standard deviation of luminance")
    blur_score: float = Field(0.0, description="Laplacian variance sharpness metric")
    is_corrupted: bool = Field(False, description="True if image failed parsing or decode")
    corruption_reason: Optional[str] = Field(None, description="Diagnostic error details if corrupted")


class DuplicateTypeEnum(str, Enum):
    EXACT = "EXACT"
    NEAR_DUPLICATE = "NEAR_DUPLICATE"


class DuplicateItem(BaseModel):
    """Individual image member of a duplicate cluster."""
    file_path: str
    sha256: str
    similarity: float = Field(..., ge=0.0, le=100.0, description="Similarity percentage")
    duplicate_type: DuplicateTypeEnum
    hamming_distance: int = Field(..., ge=0, description="Perceptual Hamming distance from representative")


class DuplicateCluster(BaseModel):
    """Group of identical or near-identical image samples.
    
    Adheres strictly to the Section 9 specification:
    Always uses the phrase 'Potential duplicate flooding indicator'.
    """
    cluster_id: str = Field(..., description="Cluster identifier, e.g. DUP-CLUSTER-001")
    representative_image: str = Field(..., description="Canonical path of primary reference image")
    duplicates: List[DuplicateItem] = Field(default_factory=list, description="All images in the cluster")
    cluster_size: int = Field(..., description="Total items in this cluster including representative")
    indicator: str = Field(
        default="Potential duplicate flooding indicator",
        description="Mandatory non-adversarial indicator text"
    )


class DuplicateAnalysisResult(BaseModel):
    """Aggregate duplicate analysis outcome for a dataset."""
    clusters: List[DuplicateCluster] = Field(default_factory=list)
    total_duplicate_samples: int = 0
    exact_duplicate_count: int = 0
    near_duplicate_count: int = 0
    flooding_clusters_count: int = 0


class OODSampleScore(BaseModel):
    """Out-Of-Distribution anomaly evaluation for a single sample."""
    sample_id: str
    file_path: str
    ood_score: float = Field(..., ge=0.0, le=1.0, description="Normalized anomaly score [0.0 - 1.0]")
    distance_to_centroid: float = Field(..., description="Cosine/Euclidean distance from embedding centroid")
    isolation_score: float = Field(..., description="Raw Isolation Forest decision function output")
    severity: SeverityEnum
    is_outlier: bool = Field(..., description="True if sample exceeds outlier decision threshold")
    limitation_note: str = Field(
        default="Sample features deviate significantly from the baseline distribution. "
                "This indicates atypical visual features or potential out-of-distribution domain shift, "
                "but does not definitively prove malicious poisoning or corruption."
    )


class OODAnalysisResult(BaseModel):
    """Aggregate OOD and anomaly analysis report."""
    total_evaluated: int
    anomalies_detected: int
    contamination_rate: float
    samples: List[OODSampleScore] = Field(default_factory=list)
    summary_limitation: str = Field(
        default="OOD scores measure geometric feature deviation under the chosen embedding representation. "
                "Unusual visual lighting, novel backgrounds, or rare classes may elevate scores non-adversarially."
    )


class LabelInconsistencyFinding(BaseModel):
    """Sample flagged for disagreement between assigned label and neighborhood consensus.
    
    Adheres strictly to Section 11 specification:
    Mandatory finding description must say 'Potential label inconsistency'.
    """
    sample_id: str
    file_path: str
    current_label: str
    suggested_label: str
    consensus_ratio: float = Field(..., ge=0.0, le=1.0, description="Fraction of k-NN neighbors agreeing on suggested label")
    neighbor_count: int = Field(..., description="Value of k evaluated")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in the inconsistency finding")
    finding: str = Field(
        default="Potential label inconsistency",
        description="Mandatory Section 11 finding description"
    )
    details: Dict[str, Any] = Field(default_factory=dict)
