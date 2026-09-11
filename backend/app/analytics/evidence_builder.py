"""TrustLens Evidence Object Builder (Section 22 Implementation)

Transforms analytical findings from CV inspection, duplicate clustering,
OOD anomaly scoring, and label consistency checks into standardized,
canonical Section 22 Evidence Objects.
"""

from __future__ import annotations

from typing import List
from app.schemas.cv import (
    DuplicateAnalysisResult,
    ImageAnalysisResult,
    LabelInconsistencyFinding,
    OODAnalysisResult,
)
from app.schemas.evidence import EvidenceObject, SeverityEnum


class EvidenceBuilder:
    """Builds standardized Evidence Objects from CV and analytics results."""

    def __init__(self, dataset_prefix: str = "EVID-DS") -> None:
        self.prefix = dataset_prefix
        self._counter = 1

    def _next_id(self) -> str:
        eid = f"{self.prefix}-2026-{self._counter:05d}"
        self._counter += 1
        return eid

    def build_corruption_evidence(self, images: List[ImageAnalysisResult]) -> List[EvidenceObject]:
        """Convert corrupted file detections into Evidence Objects."""
        evidences: List[EvidenceObject] = []
        for img in images:
            if img.is_corrupted:
                evidences.append(
                    EvidenceObject(
                        id=self._next_id(),
                        finding_type="CORRUPTED_FILE_DETECTED",
                        what_happened=(
                            f"Image file '{img.file_name}' could not be decoded or failed format verification."
                        ),
                        why_flagged=f"Integrity check failed: {img.corruption_reason or 'Malformed image stream'}",
                        evidence={
                            "file_path": img.file_path,
                            "file_size_bytes": img.file_size_bytes,
                            "sha256": img.sha256,
                            "format": img.format,
                            "error_detail": img.corruption_reason,
                        },
                        severity=SeverityEnum.HIGH,
                        confidence=1.00,
                        affected_asset=img.file_path,
                        recommended_action=(
                            "Quarantine or re-ingest corrupted image file before training pipeline ingestion."
                        ),
                        limitations=(
                            "File corruption may result from incomplete network transfers, disk sector faults, "
                            "or invalid container headers rather than deliberate tampering."
                        ),
                    )
                )
        return evidences

    def build_duplicate_evidence(self, duplicate_result: DuplicateAnalysisResult) -> List[EvidenceObject]:
        """Convert duplicate flooding clusters into Evidence Objects."""
        evidences: List[EvidenceObject] = []
        for cluster in duplicate_result.clusters:
            # Determine maximum similarity among duplicates
            max_sim = max((d.similarity for d in cluster.duplicates if d.similarity < 99.999), default=100.0)
            has_exact = any(d.duplicate_type == "EXACT" and d.file_path != cluster.representative_image for d in cluster.duplicates)

            severity = SeverityEnum.HIGH if (cluster.cluster_size >= 4 or has_exact) else SeverityEnum.MEDIUM
            confidence = round(max_sim / 100.0, 4)

            evidences.append(
                EvidenceObject(
                    id=self._next_id(),
                    finding_type="DUPLICATE_FLOODING_CLUSTER",
                    what_happened=(
                        f"Detected duplicate cluster {cluster.cluster_id} comprising {cluster.cluster_size} "
                        f"identical or visually near-duplicate images."
                    ),
                    why_flagged=(
                        f"{cluster.indicator}: Cluster size of {cluster.cluster_size} exceeds nominal "
                        f"uniqueness threshold (similarity: {max_sim}%)."
                    ),
                    evidence={
                        "cluster_id": cluster.cluster_id,
                        "representative_image": cluster.representative_image,
                        "cluster_size": cluster.cluster_size,
                        "indicator": cluster.indicator,
                        "duplicate_samples": [d.model_dump() for d in cluster.duplicates],
                    },
                    severity=severity,
                    confidence=confidence,
                    affected_asset=cluster.representative_image,
                    recommended_action=(
                        "Review and deduplicate training batch to eliminate sample over-representation "
                        "and prevent model decision boundary distortion."
                    ),
                    limitations=(
                        "Sequential burst captures, dashcam sequences, or fixed-camera feeds may generate "
                        "high visual similarity clusters legitimately without malicious intent."
                    ),
                )
            )
        return evidences

    def build_ood_evidence(self, ood_result: OODAnalysisResult) -> List[EvidenceObject]:
        """Convert statistical OOD outliers into Evidence Objects."""
        evidences: List[EvidenceObject] = []
        for sample in ood_result.samples:
            if sample.is_outlier:
                evidences.append(
                    EvidenceObject(
                        id=self._next_id(),
                        finding_type="OUT_OF_DISTRIBUTION_ANOMALY",
                        what_happened=(
                            f"Sample visual features deviate markedly from the dataset distribution centroid "
                            f"(OOD anomaly score: {sample.ood_score})."
                        ),
                        why_flagged=(
                            f"Statistical outlier flagged by Isolation Forest decision function ({sample.isolation_score}) "
                            f"and centroid cosine distance ({sample.distance_to_centroid})."
                        ),
                        evidence={
                            "sample_id": sample.sample_id,
                            "file_path": sample.file_path,
                            "ood_score": sample.ood_score,
                            "isolation_score": sample.isolation_score,
                            "distance_to_centroid": sample.distance_to_centroid,
                            "contamination_rate": ood_result.contamination_rate,
                        },
                        severity=sample.severity,
                        confidence=sample.ood_score,
                        affected_asset=sample.file_path,
                        recommended_action=(
                            "Inspect sample for anomalous scene lighting, domain shift, synthetic artifacts, "
                            "or potential backdoor trigger patches."
                        ),
                        limitations=sample.limitation_note,
                    )
                )
        return evidences

    def build_label_inconsistency_evidence(
        self, label_findings: List[LabelInconsistencyFinding]
    ) -> List[EvidenceObject]:
        """Convert label inconsistency findings into Evidence Objects."""
        evidences: List[EvidenceObject] = []
        for finding in label_findings:
            severity = SeverityEnum.HIGH if finding.confidence >= 0.75 else SeverityEnum.MEDIUM
            evidences.append(
                EvidenceObject(
                    id=self._next_id(),
                    finding_type="LABEL_INCONSISTENCY_DETECTED",
                    what_happened=(
                        f"Sample assigned label '{finding.current_label}' contradicts "
                        f"{int(finding.consensus_ratio * 100)}% majority agreement among "
                        f"{finding.neighbor_count} nearest neighbors in feature space proposing '{finding.suggested_label}'."
                    ),
                    why_flagged=(
                        f"{finding.finding}: Feature neighborhood disagreement ratio "
                        f"({finding.consensus_ratio}) exceeds tolerance cutoff."
                    ),
                    evidence={
                        "sample_id": finding.sample_id,
                        "file_path": finding.file_path,
                        "current_label": finding.current_label,
                        "suggested_label": finding.suggested_label,
                        "consensus_ratio": finding.consensus_ratio,
                        "neighbor_count": finding.neighbor_count,
                        "breakdown": finding.details.get("neighbor_label_breakdown", {}),
                    },
                    severity=severity,
                    confidence=finding.confidence,
                    affected_asset=finding.file_path,
                    recommended_action=(
                        f"Route sample to human domain annotator to verify whether label should be updated "
                        f"from '{finding.current_label}' to '{finding.suggested_label}'."
                    ),
                    limitations=(
                        "Evaluated strictly on embedding distance consensus (NOT semantic understanding). "
                        "Unimodal clustering assumptions may not apply to multimodal or fine-grained classes."
                    ),
                )
            )
        return evidences
