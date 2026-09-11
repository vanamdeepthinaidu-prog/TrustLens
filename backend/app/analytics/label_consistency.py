"""TrustLens Label Consistency Forensic Engine

Identifies potential label noise or mislabeling using feature-space k-nearest
neighbor consensus and cluster agreement.

Adheres strictly to the Section 11 specification:
Uses statistical feature agreement (NOT semantic understanding) and outputs
the exact phrase 'Potential label inconsistency', never 'confirmed poisoned sample'.
"""

from __future__ import annotations

from collections import Counter
from typing import Dict, List, Optional
import numpy as np
from sklearn.neighbors import NearestNeighbors

from app.schemas.cv import LabelInconsistencyFinding
from app.schemas.dataset import DatasetSample


def check_label_consistency(
    embeddings: np.ndarray,
    samples: List[DatasetSample],
    k: int = 5,
    inconsistency_threshold: float = 0.60,
) -> List[LabelInconsistencyFinding]:
    """Inspect dataset labels for inconsistency against feature neighborhood agreement.

    Args:
        embeddings: 2D feature matrix of shape (N, D).
        samples: List of DatasetSample objects.
        k: Number of nearest neighbors to evaluate (default 5).
        inconsistency_threshold: Minimum fraction of neighbors [0.5 - 1.0] that must
            disagree with the sample's assigned label to trigger a finding.

    Returns:
        List of LabelInconsistencyFinding records.
    """
    if len(samples) != len(embeddings) or len(samples) < 3:
        return []

    # 1. Extract labeled indices
    labeled_indices: List[int] = []
    labels: List[str] = []
    for idx, s in enumerate(samples):
        if s.label is not None and str(s.label).strip():
            labeled_indices.append(idx)
            labels.append(str(s.label).strip())

    if len(labeled_indices) < 3:
        return []

    unique_classes = set(labels)
    if len(unique_classes) < 2:
        return []  # Need at least two distinct classes to detect inconsistency

    # Constrain k to available samples
    effective_k = min(k, len(labeled_indices) - 1)
    if effective_k < 1:
        return []

    sub_embeddings = embeddings[labeled_indices]

    # Fit k-NN using cosine metric (or euclidean on normalized features)
    nn = NearestNeighbors(n_neighbors=effective_k + 1, metric="cosine")
    nn.fit(sub_embeddings)
    distances, indices = nn.kneighbors(sub_embeddings)

    findings: List[LabelInconsistencyFinding] = []

    for row_idx, sample_idx in enumerate(labeled_indices):
        current_sample = samples[sample_idx]
        current_label = labels[row_idx]

        # Neighbor indices excluding the query sample itself (index 0 is self)
        neighbor_row_indices = indices[row_idx, 1:]
        neighbor_labels = [labels[n_idx] for n_idx in neighbor_row_indices]

        # Tally vote of neighborhood
        counts = Counter(neighbor_labels)
        most_common_label, most_common_count = counts.most_common(1)[0]
        consensus_ratio = float(most_common_count / effective_k)

        # Flag if majority of neighbors belong to a different class
        if most_common_label != current_label and consensus_ratio >= inconsistency_threshold:
            # Confidence is scaled by consensus ratio and distance contrast
            own_label_count = counts.get(current_label, 0)
            confidence = round(float(consensus_ratio * (1.0 - (own_label_count / effective_k))), 4)
            confidence = max(0.50, min(0.99, confidence))

            finding = LabelInconsistencyFinding(
                sample_id=current_sample.sample_id,
                file_path=current_sample.file_path,
                current_label=current_label,
                suggested_label=most_common_label,
                consensus_ratio=round(consensus_ratio, 4),
                neighbor_count=effective_k,
                confidence=confidence,
                finding="Potential label inconsistency",
                details={
                    "neighbor_label_breakdown": dict(counts),
                    "own_label_agreement_count": own_label_count,
                    "methodology": "k-Nearest Neighbor Cosine Feature Consensus",
                    "disclaimer": "Evaluated on visual feature space similarity; does not assert deliberate manipulation.",
                },
            )
            findings.append(finding)

    return findings
