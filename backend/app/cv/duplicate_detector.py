"""TrustLens Duplicate Detection Engine

Detects exact cryptographic duplicates (SHA-256) and near-duplicates (perceptual hash
Hamming distance) with graph clustering and similarity percentage reporting.

Adheres strictly to the Section 9 specification:
Every cluster includes the phrase 'Potential duplicate flooding indicator'.
"""

from __future__ import annotations

from typing import Dict, List, Set
import imagehash
from app.schemas.cv import (
    DuplicateAnalysisResult,
    DuplicateCluster,
    DuplicateItem,
    DuplicateTypeEnum,
    ImageAnalysisResult,
)


class DisjointSetUnion:
    """Disjoint Set Union (DSU) / Union-Find for clustering connected duplicates."""

    def __init__(self, size: int) -> None:
        self.parent = list(range(size))
        self.rank = [0] * size

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> None:
        root_x = self.find(x)
        root_y = self.find(y)
        if root_x == root_y:
            return
        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1


def compute_phash_hamming_distance(hash1_hex: str, hash2_hex: str) -> int:
    """Compute Hamming distance between two hexadecimal hash strings."""
    try:
        h1 = imagehash.hex_to_hash(hash1_hex)
        h2 = imagehash.hex_to_hash(hash2_hex)
        return int(h1 - h2)
    except Exception:
        # Fallback manual bitwise XOR distance
        try:
            val1 = int(hash1_hex, 16)
            val2 = int(hash2_hex, 16)
            return bin(val1 ^ val2).count("1")
        except Exception:
            return 64


def detect_duplicates(
    images: List[ImageAnalysisResult],
    similarity_threshold: float = 0.90,
    hash_bit_length: int = 64,
) -> DuplicateAnalysisResult:
    """Analyze a collection of images for exact and near-duplicates.

    Args:
        images: List of analyzed image records.
        similarity_threshold: Minimum similarity fraction [0.5 - 1.0] for near duplicates.
            Default 0.90 corresponds to Hamming distance <= 6 out of 64 bits.
        hash_bit_length: Bit length of perceptual hash (default 64 for standard pHash).

    Returns:
        DuplicateAnalysisResult with clustered groups, metrics, and Section 9 indicator.
    """
    valid_images = [img for img in images if not img.is_corrupted and img.sha256]
    n = len(valid_images)
    if n <= 1:
        return DuplicateAnalysisResult(
            clusters=[],
            total_duplicate_samples=0,
            exact_duplicate_count=0,
            near_duplicate_count=0,
            flooding_clusters_count=0,
        )

    dsu = DisjointSetUnion(n)
    
    # Store pairwise relationship details: (i, j) -> (duplicate_type, similarity, hamming_distance)
    pair_relationships: Dict[tuple[int, int], tuple[DuplicateTypeEnum, float, int]] = {}

    max_hamming_dist = int(round((1.0 - similarity_threshold) * hash_bit_length))

    # 1. Exact Duplicate Pass via SHA-256 dictionary grouping
    sha_map: Dict[str, List[int]] = {}
    for idx, img in enumerate(valid_images):
        sha_map.setdefault(img.sha256, []).append(idx)

    for sha, indices in sha_map.items():
        if len(indices) > 1:
            first_idx = indices[0]
            for other_idx in indices[1:]:
                dsu.union(first_idx, other_idx)
                pair_relationships[(min(first_idx, other_idx), max(first_idx, other_idx))] = (
                    DuplicateTypeEnum.EXACT,
                    100.0,
                    0,
                )

    # 2. Near Duplicate Pass via Perceptual Hashes (pHash)
    for i in range(n):
        img_i = valid_images[i]
        if not img_i.perceptual_hashes or not img_i.perceptual_hashes.phash:
            continue
        phash_i = img_i.perceptual_hashes.phash

        for j in range(i + 1, n):
            # If already grouped as exact duplicate, skip near-duplicate calculation
            if (i, j) in pair_relationships:
                continue

            img_j = valid_images[j]
            if not img_j.perceptual_hashes or not img_j.perceptual_hashes.phash:
                continue
            phash_j = img_j.perceptual_hashes.phash

            dist = compute_phash_hamming_distance(phash_i, phash_j)
            # Guard against degenerate flat/solid color collisions (e.g. solid black vs solid white)
            brightness_diff = abs(img_i.brightness - img_j.brightness)
            if brightness_diff > 45.0:
                continue

            if dist <= max_hamming_dist:
                similarity_pct = round((1.0 - (dist / hash_bit_length)) * 100.0, 2)
                dsu.union(i, j)
                pair_relationships[(i, j)] = (
                    DuplicateTypeEnum.NEAR_DUPLICATE,
                    similarity_pct,
                    dist,
                )

    # 3. Form Clusters from DSU
    raw_clusters: Dict[int, List[int]] = {}
    for idx in range(n):
        root = dsu.find(idx)
        raw_clusters.setdefault(root, []).append(idx)

    clusters: List[DuplicateCluster] = []
    total_duplicate_samples = 0
    exact_count = 0
    near_count = 0
    cluster_counter = 1

    for root, member_indices in raw_clusters.items():
        if len(member_indices) < 2:
            continue  # Single isolated image, not a duplicate

        # Select canonical representative (highest blur score / sharpness, then earliest path)
        sorted_members = sorted(
            member_indices,
            key=lambda idx: (-valid_images[idx].blur_score, valid_images[idx].file_path)
        )
        rep_idx = sorted_members[0]
        rep_img = valid_images[rep_idx]

        duplicate_items: List[DuplicateItem] = []
        for idx in sorted_members:
            img = valid_images[idx]
            if idx == rep_idx:
                # Representative itself is 100% similar to itself
                duplicate_items.append(
                    DuplicateItem(
                        file_path=img.file_path,
                        sha256=img.sha256,
                        similarity=100.0,
                        duplicate_type=DuplicateTypeEnum.EXACT,
                        hamming_distance=0,
                    )
                )
            else:
                # Determine relationship with representative
                if img.sha256 == rep_img.sha256:
                    dup_type = DuplicateTypeEnum.EXACT
                    sim = 100.0
                    dist = 0
                    exact_count += 1
                else:
                    dup_type = DuplicateTypeEnum.NEAR_DUPLICATE
                    dist = 0
                    if img.perceptual_hashes and rep_img.perceptual_hashes:
                        dist = compute_phash_hamming_distance(
                            img.perceptual_hashes.phash, rep_img.perceptual_hashes.phash
                        )
                    sim = round((1.0 - (dist / hash_bit_length)) * 100.0, 2)
                    near_count += 1

                duplicate_items.append(
                    DuplicateItem(
                        file_path=img.file_path,
                        sha256=img.sha256,
                        similarity=sim,
                        duplicate_type=dup_type,
                        hamming_distance=dist,
                    )
                )

        cluster_id = f"DUP-CLUSTER-{cluster_counter:03d}"
        cluster_counter += 1
        total_duplicate_samples += (len(duplicate_items) - 1)

        clusters.append(
            DuplicateCluster(
                cluster_id=cluster_id,
                representative_image=rep_img.file_path,
                duplicates=duplicate_items,
                cluster_size=len(duplicate_items),
                indicator="Potential duplicate flooding indicator",
            )
        )

    return DuplicateAnalysisResult(
        clusters=clusters,
        total_duplicate_samples=total_duplicate_samples,
        exact_duplicate_count=exact_count,
        near_duplicate_count=near_count,
        flooding_clusters_count=len(clusters),
    )
