"""TrustLens Dataset Manifest and Analysis Request/Response Schemas

Supports multi-format datasets (folders, CSV metadata, YOLO formats)
and provides response payload structures for API integration.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from app.schemas.cv import (
    ImageAnalysisResult,
    DuplicateAnalysisResult,
    OODAnalysisResult,
    LabelInconsistencyFinding,
)
from app.schemas.evidence import EvidenceObject


class DatasetFormatEnum(str, Enum):
    FOLDER = "FOLDER"
    CSV = "CSV"
    YOLO = "YOLO"
    AUTO = "AUTO"


class DatasetSample(BaseModel):
    """Normalized representation of a single dataset sample regardless of raw format."""
    sample_id: str = Field(..., description="Unique sample ID within dataset")
    file_path: str = Field(..., description="Absolute or relative path to image file")
    label: Optional[str] = Field(None, description="Ground-truth label if provided")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Format-specific metadata (e.g. YOLO boxes, CSV columns)")


class DatasetManifest(BaseModel):
    """Manifest describing an ingested dataset."""
    dataset_id: str
    dataset_name: str
    detected_format: DatasetFormatEnum
    root_path: str
    total_samples: int
    samples: List[DatasetSample] = Field(default_factory=list)
    classes: List[str] = Field(default_factory=list)
    manifest_hash: Optional[str] = None


class DatasetAnalysisRequest(BaseModel):
    """Request payload for dataset forensic analysis."""
    dataset_path: str = Field(..., description="Path to folder, CSV file, or YOLO directory")
    format_hint: DatasetFormatEnum = Field(default=DatasetFormatEnum.AUTO)
    similarity_threshold: float = Field(default=0.90, ge=0.50, le=1.00, description="Perceptual similarity cutoff")
    ood_contamination: float = Field(default=0.08, ge=0.01, le=0.50, description="Estimated outlier contamination rate")
    knn_k: int = Field(default=5, ge=1, le=50, description="k-nearest neighbors for label consistency")
    enable_embeddings: bool = Field(default=True, description="Whether to extract deep embeddings for OOD and label checks")


class DatasetQualityOverview(BaseModel):
    """High-level summary metrics of dataset health."""
    total_samples: int
    valid_images: int
    corrupted_images: int
    mean_brightness: float
    mean_contrast: float
    mean_blur_score: float
    duplicate_clusters_count: int
    duplicate_samples_count: int
    ood_anomalies_count: int
    label_inconsistencies_count: int
    integrity_status: str = Field(..., description="PASSED | FLAGGED | CRITICAL_ANOMALIES")


class DatasetAnalysisResponse(BaseModel):
    """Complete forensic inspection response for POST /api/datasets/analyze."""
    dataset_manifest: DatasetManifest
    quality_overview: DatasetQualityOverview
    image_results: List[ImageAnalysisResult] = Field(default_factory=list)
    duplicate_analysis: DuplicateAnalysisResult
    ood_analysis: Optional[OODAnalysisResult] = None
    label_analysis: List[LabelInconsistencyFinding] = Field(default_factory=list)
    evidence_objects: List[EvidenceObject] = Field(
        default_factory=list,
        description="Section 22 Evidence Objects for downstream risk engines and UI"
    )
