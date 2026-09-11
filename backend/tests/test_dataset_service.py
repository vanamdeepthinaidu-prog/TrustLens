"""Integration Tests for Dataset Forensic Service & Multi-Format Ingestion"""

from pathlib import Path
from app.schemas.dataset import DatasetAnalysisRequest, DatasetFormatEnum
from app.services.dataset_service import DatasetService


def test_service_analyzes_folder_dataset(synthetic_folder_dataset: Path):
    service = DatasetService()
    req = DatasetAnalysisRequest(
        dataset_path=str(synthetic_folder_dataset),
        format_hint=DatasetFormatEnum.FOLDER,
        similarity_threshold=0.85,
        enable_embeddings=True,
    )

    response = service.analyze_dataset(req)

    # 1. Manifest verification
    assert response.dataset_manifest.total_samples == 7
    assert response.dataset_manifest.detected_format == DatasetFormatEnum.FOLDER

    # 2. Quality overview
    assert response.quality_overview.corrupted_images >= 1
    assert response.quality_overview.valid_images >= 4
    assert response.quality_overview.duplicate_clusters_count >= 1

    # 3. Duplicate clusters
    dup_res = response.duplicate_analysis
    assert len(dup_res.clusters) >= 1
    for cluster in dup_res.clusters:
        assert cluster.indicator == "Potential duplicate flooding indicator"

    # 4. Section 22 Evidence Objects verification
    evidences = response.evidence_objects
    assert len(evidences) >= 2  # At least 1 corruption + 1 duplicate cluster

    for ev in evidences:
        assert ev.id.startswith("EVID-DS-")
        assert ev.finding_type in [
            "CORRUPTED_FILE_DETECTED",
            "DUPLICATE_FLOODING_CLUSTER",
            "OUT_OF_DISTRIBUTION_ANOMALY",
            "LABEL_INCONSISTENCY_DETECTED",
        ]
        assert len(ev.what_happened) > 10
        assert len(ev.why_flagged) > 10
        assert ev.severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
        assert 0.0 <= ev.confidence <= 1.0
        assert len(ev.affected_asset) > 0
        assert len(ev.recommended_action) > 10
        assert len(ev.limitations) > 10


def test_service_analyzes_csv_dataset(synthetic_csv_dataset: Path):
    service = DatasetService()
    req = DatasetAnalysisRequest(
        dataset_path=str(synthetic_csv_dataset),
        format_hint=DatasetFormatEnum.CSV,
        enable_embeddings=True,
        knn_k=3,
    )

    response = service.analyze_dataset(req)

    assert response.dataset_manifest.detected_format == DatasetFormatEnum.CSV
    assert response.dataset_manifest.total_samples == 10
    assert "red_circle" in response.dataset_manifest.classes
    assert "blue_square" in response.dataset_manifest.classes

    # Label consistency findings
    assert len(response.label_analysis) >= 1
    inconsistent = response.label_analysis[0]
    assert inconsistent.finding == "Potential label inconsistency"

    # Evidence Objects
    label_evs = [ev for ev in response.evidence_objects if ev.finding_type == "LABEL_INCONSISTENCY_DETECTED"]
    assert len(label_evs) >= 1


def test_service_analyzes_yolo_dataset(synthetic_yolo_dataset: Path):
    service = DatasetService()
    req = DatasetAnalysisRequest(
        dataset_path=str(synthetic_yolo_dataset),
        format_hint=DatasetFormatEnum.YOLO,
        enable_embeddings=True,
    )

    response = service.analyze_dataset(req)

    assert response.dataset_manifest.detected_format == DatasetFormatEnum.YOLO
    assert response.dataset_manifest.total_samples == 2
    assert "drone" in response.dataset_manifest.classes
    assert "vehicle" in response.dataset_manifest.classes

    # Sample bounding boxes preserved in metadata
    sample1 = response.dataset_manifest.samples[0]
    assert "yolo_boxes" in sample1.metadata
    assert len(sample1.metadata["yolo_boxes"]) == 1
