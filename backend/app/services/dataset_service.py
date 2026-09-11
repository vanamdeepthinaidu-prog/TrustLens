"""TrustLens Dataset Forensic Service

Coordinates the complete dataset audit pipeline:
1. Ingests dataset (Folders, CSV metadata, YOLO format)
2. Runs per-image forensic analysis (SHA-256, pHash, blur, brightness, contrast, corruption)
3. Detects exact and near-duplicate clusters with flooding indicators
4. Extracts 512-dim visual embeddings (local TorchVision / deterministic offline)
5. Detects Out-Of-Distribution anomalies via Isolation Forest & centroid distance
6. Evaluates label consistency using k-NN neighborhood consensus
7. Generates canonical Section 22 Evidence Objects
"""

from __future__ import annotations

from pathlib import Path
from typing import List, Optional
import numpy as np

from app.analytics.evidence_builder import EvidenceBuilder
from app.analytics.label_consistency import check_label_consistency
from app.analytics.ood_detector import detect_ood
from app.cv.dataset_loader import load_dataset
from app.cv.duplicate_detector import detect_duplicates
from app.cv.embedding_extractor import get_embedding_extractor
from app.cv.image_analyzer import analyze_image
from app.schemas.cv import (
    DuplicateAnalysisResult,
    ImageAnalysisResult,
    LabelInconsistencyFinding,
    OODAnalysisResult,
)
from app.schemas.dataset import (
    DatasetAnalysisRequest,
    DatasetAnalysisResponse,
    DatasetManifest,
    DatasetQualityOverview,
)
from app.schemas.evidence import EvidenceObject


class DatasetService:
    """Service providing end-to-end dataset integrity evaluation."""

    def __init__(self) -> None:
        self.embedding_extractor = get_embedding_extractor()

    def analyze_dataset(
        self,
        request: DatasetAnalysisRequest,
    ) -> DatasetAnalysisResponse:
        """Execute full dataset integrity and security inspection pipeline."""
        dataset_path = Path(request.dataset_path).resolve()
        manifest: DatasetManifest = load_dataset(dataset_path, format_hint=request.format_hint)

        # 1. Per-Image Forensic Analysis
        image_results: List[ImageAnalysisResult] = []
        valid_paths: List[str] = []
        valid_sample_indices: List[int] = []

        for idx, sample in enumerate(manifest.samples):
            analysis = analyze_image(sample.file_path)
            image_results.append(analysis)
            if not analysis.is_corrupted:
                valid_paths.append(sample.file_path)
                valid_sample_indices.append(idx)

        # 2. Duplicate Detection (Exact & Near-Duplicate Clustering)
        duplicate_results: DuplicateAnalysisResult = detect_duplicates(
            image_results,
            similarity_threshold=request.similarity_threshold,
        )

        # 3. Embedding Extraction & Advanced Analytics (OOD & Label Consistency)
        ood_results: Optional[OODAnalysisResult] = None
        label_findings: List[LabelInconsistencyFinding] = []

        if request.enable_embeddings and valid_paths:
            valid_samples = [manifest.samples[i] for i in valid_sample_indices]
            embeddings = self.embedding_extractor.extract_batch(valid_paths)

            if len(embeddings) > 0:
                # OOD Anomaly Detection
                ood_results = detect_ood(
                    embeddings,
                    valid_samples,
                    contamination=request.ood_contamination,
                )

                # Label Consistency Inspection (only if dataset contains labels)
                if manifest.classes or any(s.label for s in valid_samples):
                    label_findings = check_label_consistency(
                        embeddings,
                        valid_samples,
                        k=request.knn_k,
                    )

        # 4. Synthesize Section 22 Evidence Objects
        evidence_builder = EvidenceBuilder(dataset_prefix="EVID-DS")
        evidence_objects: List[EvidenceObject] = []

        # A. Corrupted image evidence
        evidence_objects.extend(evidence_builder.build_corruption_evidence(image_results))

        # B. Duplicate flooding evidence
        evidence_objects.extend(evidence_builder.build_duplicate_evidence(duplicate_results))

        # C. OOD anomaly evidence
        if ood_results:
            evidence_objects.extend(evidence_builder.build_ood_evidence(ood_results))

        # D. Label inconsistency evidence
        if label_findings:
            evidence_objects.extend(
                evidence_builder.build_label_inconsistency_evidence(label_findings)
            )

        # 5. Quality Overview Metrics
        valid_count = sum(1 for img in image_results if not img.is_corrupted)
        corrupted_count = sum(1 for img in image_results if img.is_corrupted)
        
        valid_images = [img for img in image_results if not img.is_corrupted]
        mean_brightness = (
            round(float(np.mean([img.brightness for img in valid_images])), 2)
            if valid_images else 0.0
        )
        mean_contrast = (
            round(float(np.mean([img.contrast for img in valid_images])), 2)
            if valid_images else 0.0
        )
        mean_blur = (
            round(float(np.mean([img.blur_score for img in valid_images])), 2)
            if valid_images else 0.0
        )

        ood_anomalies_count = ood_results.anomalies_detected if ood_results else 0
        label_inconsistencies_count = len(label_findings)

        # Overall integrity status
        if corrupted_count > 0 or duplicate_results.flooding_clusters_count >= 3 or ood_anomalies_count >= 5:
            integrity_status = "CRITICAL_ANOMALIES"
        elif duplicate_results.total_duplicate_samples > 0 or ood_anomalies_count > 0 or label_inconsistencies_count > 0:
            integrity_status = "FLAGGED"
        else:
            integrity_status = "PASSED"

        quality_overview = DatasetQualityOverview(
            total_samples=len(manifest.samples),
            valid_images=valid_count,
            corrupted_images=corrupted_count,
            mean_brightness=mean_brightness,
            mean_contrast=mean_contrast,
            mean_blur_score=mean_blur,
            duplicate_clusters_count=duplicate_results.flooding_clusters_count,
            duplicate_samples_count=duplicate_results.total_duplicate_samples,
            ood_anomalies_count=ood_anomalies_count,
            label_inconsistencies_count=label_inconsistencies_count,
            integrity_status=integrity_status,
        )

        return DatasetAnalysisResponse(
            dataset_manifest=manifest,
            quality_overview=quality_overview,
            image_results=image_results,
            duplicate_analysis=duplicate_results,
            ood_analysis=ood_results,
            label_analysis=label_findings,
            evidence_objects=evidence_objects,
        )


# Global service instance
_DEFAULT_SERVICE: Optional[DatasetService] = None


def get_dataset_service() -> DatasetService:
    """Retrieve or initialize singleton DatasetService."""
    global _DEFAULT_SERVICE
    if _DEFAULT_SERVICE is None:
        _DEFAULT_SERVICE = DatasetService()
    return _DEFAULT_SERVICE
