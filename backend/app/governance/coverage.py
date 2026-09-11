"""
TrustLens Honest Detection Coverage Specification
Conforms strictly to Section 32 of the TrustLens specification.

Maintains strict scientific and operational honesty:
- Never asserts intent
- Clear delineation of Supported, Partially Supported, and Unsupported boundaries
- Prevents security overclaiming
"""

from enum import Enum
from typing import List, Dict, Any
from pydantic import BaseModel


class CoverageCategory(str, Enum):
    SUPPORTED = "SUPPORTED"
    PARTIALLY_SUPPORTED = "PARTIALLY_SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"


class DetectionCapability(BaseModel):
    capability_id: str
    name: str
    category: CoverageCategory
    detection_method: str
    guarantee_level: str
    limitations: str
    example_scenario: str


class DetectionCoverageMatrix:
    """
    Section 32 Detection Coverage Matrix.
    Provides verifiable, transparent declarations of detection guarantees.
    """

    CAPABILITIES: List[DetectionCapability] = [
        # SUPPORTED
        DetectionCapability(
            capability_id="CAP-SUP-01",
            name="Exact Duplicate Flooding",
            category=CoverageCategory.SUPPORTED,
            detection_method="SHA-256 cryptographic byte-hash indexing",
            guarantee_level="Deterministic (100% mathematical guarantee)",
            limitations="Fails if a single pixel value or metadata bit is altered.",
            example_scenario="Attacker attempts to flood the training queue with identical image files.",
        ),
        DetectionCapability(
            capability_id="CAP-SUP-02",
            name="Near-Duplicate Visual Clustering",
            category=CoverageCategory.SUPPORTED,
            detection_method="Perceptual hashing (pHash) with Hamming distance clustering",
            guarantee_level="High heuristic confidence (>95%)",
            limitations="May flag legitimate multi-frame burst camera captures as clusters.",
            example_scenario="Repeated submissions of the same frame with slight JPEG compression artifacts.",
        ),
        DetectionCapability(
            capability_id="CAP-SUP-03",
            name="Corrupted / Malformed Image Ingress",
            category=CoverageCategory.SUPPORTED,
            detection_method="Strict byte header validation & parser decompression checks",
            guarantee_level="Deterministic (100%)",
            limitations="Does not inspect semantic validity of successfully decoded pixels.",
            example_scenario="Truncated or malformed PNG/JPEG files causing buffer crashes.",
        ),
        DetectionCapability(
            capability_id="CAP-SUP-04",
            name="Model Binary Substitution",
            category=CoverageCategory.SUPPORTED,
            detection_method="Cryptographic SHA-256 comparison against immutable ledger register",
            guarantee_level="Deterministic (100% cryptographic guarantee)",
            limitations="Assumes initial reference hash was registered legitimately by authorized authority.",
            example_scenario="Trojan or modified model weights substituted in deployment folder.",
        ),
        DetectionCapability(
            capability_id="CAP-SUP-05",
            name="Inference Record Cryptographic Tampering",
            category=CoverageCategory.SUPPORTED,
            detection_method="Canonical JSON payload SHA-256 hash binding",
            guarantee_level="Deterministic (100% cryptographic guarantee)",
            limitations="Protects record integrity post-generation; does not detect model calculation bugs.",
            example_scenario="Post-inference alteration of classification confidence or output label.",
        ),
        DetectionCapability(
            capability_id="CAP-SUP-06",
            name="Inference Replay & Sequence Desynchronization",
            category=CoverageCategory.SUPPORTED,
            detection_method="Nonce tracking, monotonic sequence validation & timestamp window checks",
            guarantee_level="Deterministic within monitored session context",
            limitations="Requires continuous state synchronization across inference nodes.",
            example_scenario="Interception and replay of previously valid inference authorization tokens.",
        ),
        DetectionCapability(
            capability_id="CAP-SUP-07",
            name="Covariate Luminance & Dynamic Range Drift",
            category=CoverageCategory.SUPPORTED,
            detection_method="1D Wasserstein distance on luminance and Laplacian sharpness variance",
            guarantee_level="Statistical significance metric",
            limitations="Cannot determine whether drift is environmental (weather) or deliberate manipulation.",
            example_scenario="Sensor degradation causing systematic underexposure across dataset ingress.",
        ),

        # PARTIALLY SUPPORTED
        DetectionCapability(
            capability_id="CAP-PART-01",
            name="Dataset Label Inconsistency / Flipping",
            category=CoverageCategory.PARTIALLY_SUPPORTED,
            detection_method="Nearest-neighbor feature distance agreement in embedding space",
            guarantee_level="Empirical heuristic (Medium confidence)",
            limitations="Identifies statistical cluster outliers; cannot verify true ground-truth semantic intent.",
            example_scenario="Subtle mislabeling of stop signs as speed limits in visual datasets.",
        ),
        DetectionCapability(
            capability_id="CAP-PART-02",
            name="Out-of-Distribution (OOD) Sample Ingress",
            category=CoverageCategory.PARTIALLY_SUPPORTED,
            detection_method="Penultimate feature embedding extraction & distance from training centroid",
            guarantee_level="Empirical confidence based on embedding representation",
            limitations="Susceptible to false positives on rare legitimate long-tail edge cases.",
            example_scenario="Irrelevant images (e.g. medical X-rays) submitted to autonomous vehicle dataset.",
        ),
        DetectionCapability(
            capability_id="CAP-PART-03",
            name="Backdoor Trigger Sensitivity",
            category=CoverageCategory.PARTIALLY_SUPPORTED,
            detection_method="Empirical output sensitivity check under synthetic visual perturbation patches",
            guarantee_level="Empirical heuristic for tested patch topologies",
            limitations="Only tests known synthetic patterns; cannot guarantee discovery of complex latent triggers.",
            example_scenario="Model exhibiting anomalous classification flips when corner patch is applied.",
        ),
        DetectionCapability(
            capability_id="CAP-PART-04",
            name="Metadata Provenance Manipulation",
            category=CoverageCategory.PARTIALLY_SUPPORTED,
            detection_method="Cross-validation against signed ledger manifests and contributor rosters",
            guarantee_level="High if ledger record exists; Low for unanchored external files",
            limitations="Cannot prevent falsified camera clock stamps before initial cryptographic ingestion.",
            example_scenario="Altering GPS coordinates or acquisition timestamps on ingested surveillance frames.",
        ),

        # UNSUPPORTED
        DetectionCapability(
            capability_id="CAP-UNSUP-01",
            name="Imperceptible Adversarial Gradient Perturbations",
            category=CoverageCategory.UNSUPPORTED,
            detection_method="None (out of scope for lightweight offline hash/feature pipeline)",
            guarantee_level="Unsupported",
            limitations="Low-magnitude gradient attacks (e.g. FGSM/PGD with epsilon < 2/255) bypass statistical detectors.",
            example_scenario="Carefully optimized continuous adversarial noise targeting neural network activations.",
        ),
        DetectionCapability(
            capability_id="CAP-UNSUP-02",
            name="Stealthy Zero-Day Architecture Backdoors",
            category=CoverageCategory.UNSUPPORTED,
            detection_method="None (requires full neural network weight decompilation / formal verification)",
            guarantee_level="Unsupported",
            limitations="Complex backdoors triggered by natural rare feature combinations cannot be detected statically.",
            example_scenario="Backdoors activated only when specific rare multi-object configurations appear.",
        ),
        DetectionCapability(
            capability_id="CAP-UNSUP-03",
            name="Pre-Sensor Physical World Spoofing",
            category=CoverageCategory.UNSUPPORTED,
            detection_method="None (requires hardware multi-spectral tamper sensors)",
            guarantee_level="Unsupported",
            limitations="Physical camouflage, lens laser dazzling, and painted road triggers operate prior to digital capture.",
            example_scenario="Physical adversarial stickers placed on roadside infrastructure.",
        ),
        DetectionCapability(
            capability_id="CAP-UNSUP-04",
            name="Legitimate Key Insider Compromise",
            category=CoverageCategory.UNSUPPORTED,
            detection_method="None (cryptographic signatures remain mathematically valid)",
            guarantee_level="Unsupported",
            limitations="Cryptographic ledgers record authentic signatures; they cannot prevent authorized actors from submitting malicious content.",
            example_scenario="Authorized administrator credentials used to sign an altered model checkpoint.",
        ),
    ]

    @classmethod
    def get_capabilities_by_category(cls, category: CoverageCategory) -> List[DetectionCapability]:
        return [c for c in cls.CAPABILITIES if c.category == category]

    @classmethod
    def get_coverage_summary(cls) -> Dict[str, Any]:
        return {
            "total_capabilities_evaluated": len(cls.CAPABILITIES),
            "supported_count": sum(1 for c in cls.CAPABILITIES if c.category == CoverageCategory.SUPPORTED),
            "partially_supported_count": sum(1 for c in cls.CAPABILITIES if c.category == CoverageCategory.PARTIALLY_SUPPORTED),
            "unsupported_count": sum(1 for c in cls.CAPABILITIES if c.category == CoverageCategory.UNSUPPORTED),
            "guarantee_statement": (
                "TrustLens provides deterministic cryptographic guarantees for artifact integrity, "
                "ledger immutability, and replay protection. Visual dataset and model behavior detections "
                "are statistical heuristics subject to scientific limitations clearly stated in Section 32."
            ),
        }
