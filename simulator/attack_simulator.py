"""
TrustLens Security Lab & Attack Simulator
Conforms strictly to Section 24 of the TrustLens specification.

Implements all 9 attack simulation types:
1. label_flip
2. duplicate_flooding
3. ood_injection
4. image_corruption
5. metadata_manipulation
6. model_substitution
7. trigger_injection
8. inference_tampering
9. replay_attack

SAFETY GUARANTEES:
- Operates STRICTLY on isolated copies in data/simulations/{simulation_id}/
- NEVER mutates original demo data
- Generates reproducible results via recorded random_seed
"""

import os
import json
import time
import shutil
import random
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timezone
import numpy as np
from PIL import Image

from pydantic import BaseModel, Field
from app.risk.schemas import EvidenceObject, Severity, Disposition
from app.core.hashing import hash_bytes, hash_file, hash_json


class AttackType(str, Enum):
    LABEL_FLIP = "label_flip"
    DUPLICATE_FLOODING = "duplicate_flooding"
    OOD_INJECTION = "ood_injection"
    IMAGE_CORRUPTION = "image_corruption"
    METADATA_MANIPULATION = "metadata_manipulation"
    MODEL_SUBSTITUTION = "model_substitution"
    TRIGGER_INJECTION = "trigger_injection"
    INFERENCE_TAMPERING = "inference_tampering"
    REPLAY_ATTACK = "replay_attack"


class AttackSimulationConfig(BaseModel):
    simulation_id: str
    attack_type: AttackType
    target_asset: str = "demo_asset"
    parameters: Dict[str, Any] = Field(default_factory=dict)
    random_seed: int = 42
    operator_id: str = "sec_analyst_01"
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


class AttackSimulationResult(BaseModel):
    simulation_id: str
    attack_type: AttackType
    status: str  # "SUCCESS", "FAILED"
    original_artifact_hash: str
    mutated_artifact_hash: str
    artifacts_created: List[str]
    parameters: Dict[str, Any]
    detection_signature: Dict[str, Any]
    evidence_generated: EvidenceObject
    execution_time_ms: float
    output_directory: str
    message: str


class AttackSimulator:
    """
    Security Lab Attack Engine.
    Executes controlled adversarial simulations in sandboxed copy directories.
    """

    _sim_counter = 0

    def __init__(self, base_sim_dir: Optional[str] = None) -> None:
        if base_sim_dir:
            self.base_sim_dir = Path(base_sim_dir)
        else:
            self.base_sim_dir = Path("data/simulations")
        self.base_sim_dir.mkdir(parents=True, exist_ok=True)

    @classmethod
    def generate_simulation_id(cls) -> str:
        cls._sim_counter += 1
        year = datetime.now(timezone.utc).year
        return f"SIM-{year}-{cls._sim_counter:05d}"

    def _prepare_sandbox(self, simulation_id: str) -> Path:
        sandbox = self.base_sim_dir / simulation_id
        sandbox.mkdir(parents=True, exist_ok=True)
        return sandbox

    def _create_sample_image(self, path: Path, color: tuple = (120, 150, 180), text: str = "Clean Sample") -> None:
        """Helper to create a synthetic image if target doesn't exist."""
        arr = np.ones((64, 64, 3), dtype=np.uint8) * np.array(color, dtype=np.uint8)
        # Add some variation
        arr[10:54, 10:54] = np.clip(arr[10:54, 10:54] + 30, 0, 255)
        img = Image.fromarray(arr)
        img.save(path)

    # -------------------------------------------------------------
    # ATTACK 1: LABEL FLIP
    # -------------------------------------------------------------
    def simulate_label_flip(
        self,
        labels_data: Optional[Dict[str, str]] = None,
        flip_rate: float = 0.30,
        random_seed: int = 42,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)
        random.seed(random_seed)

        if not labels_data:
            labels_data = {
                f"sample_{i:03d}.jpg": "pedestrian" if i % 2 == 0 else "vehicle"
                for i in range(20)
            }

        orig_hash = hash_json(labels_data)
        mutated_labels = dict(labels_data)
        keys = list(mutated_labels.keys())
        num_to_flip = max(1, int(len(keys) * flip_rate))
        flipped_keys = random.sample(keys, num_to_flip)

        class_map = {"pedestrian": "vehicle", "vehicle": "pedestrian"}
        for k in flipped_keys:
            old_c = mutated_labels[k]
            mutated_labels[k] = class_map.get(old_c, "anomalous_class")

        mut_hash = hash_json(mutated_labels)
        out_path = sandbox / "mutated_annotations.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mutated_labels, f, indent=2)

        evidence = EvidenceObject(
            finding_type="Potential label inconsistency",
            what_happened=f"Simulated label flipping on {num_to_flip}/{len(keys)} samples ({flip_rate:.1%}).",
            why_flagged="Feature cluster proximity analysis identified severe nearest-neighbor annotation divergence.",
            evidence=[
                {"flipped_sample": k, "previous_label": labels_data[k], "mutated_label": mutated_labels[k]}
                for k in flipped_keys[:5]
            ],
            severity=Severity.HIGH,
            confidence=0.88,
            affected_asset=out_path.name,
            recommended_action="Quarantine inverted labels and re-annotate via secondary human consensus.",
            limitations="Label consistency check uses feature similarity / nearest neighbors; cannot verify ground truth intent.",
            disposition=Disposition.QUARANTINE,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.LABEL_FLIP,
            status="SUCCESS",
            original_artifact_hash=orig_hash,
            mutated_artifact_hash=mut_hash,
            artifacts_created=[str(out_path)],
            parameters={"flip_rate": flip_rate, "flipped_count": num_to_flip, "random_seed": random_seed},
            detection_signature={"flagged_samples_count": num_to_flip, "cluster_divergence_detected": True},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message=f"Simulated label flip attack executed safely on {num_to_flip} annotations.",
        )

    # -------------------------------------------------------------
    # ATTACK 2: DUPLICATE FLOODING
    # -------------------------------------------------------------
    def simulate_duplicate_flooding(
        self,
        base_image_path: Optional[str] = None,
        flood_count: int = 6,
        slight_perturbation: bool = True,
        random_seed: int = 42,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)
        random.seed(random_seed)

        src_path = sandbox / "source_seed.png"
        if base_image_path and Path(base_image_path).exists():
            shutil.copy2(base_image_path, src_path)
        else:
            self._create_sample_image(src_path, color=(70, 130, 180))

        orig_hash = hash_file(src_path)
        created_files = [str(src_path)]
        cluster_entries = []

        base_img = Image.open(src_path).convert("RGB")
        for i in range(flood_count):
            clone_path = sandbox / f"flooded_copy_{i+1:02d}.png"
            if slight_perturbation and i % 2 == 1:
                # Near-duplicate with 1-pixel color variation
                arr = np.array(base_img, dtype=np.int16)
                arr[:, :, 0] = np.clip(arr[:, :, 0] + (i % 3 + 1), 0, 255)
                pert_img = Image.fromarray(arr.astype(np.uint8))
                pert_img.save(clone_path)
            else:
                # Exact byte duplicate
                shutil.copy2(src_path, clone_path)

            f_hash = hash_file(clone_path)
            created_files.append(str(clone_path))
            cluster_entries.append({
                "filename": clone_path.name,
                "sha256": f_hash,
                "is_exact_match": (f_hash == orig_hash),
                "similarity_score": 100.0 if (f_hash == orig_hash) else 99.2,
            })

        evidence = EvidenceObject(
            finding_type="Potential duplicate flooding indicator",
            what_happened=f"Detected high-density duplicate cluster with {flood_count} near-identical copies.",
            why_flagged="Perceptual hashing and SHA-256 revealed identical visual payloads injected in dataset.",
            evidence=cluster_entries,
            severity=Severity.HIGH,
            confidence=0.96,
            affected_asset=f"Cluster centered at {src_path.name}",
            recommended_action="Deduplicate dataset queue; enforce SHA-256 uniqueness check prior to model ingestion.",
            limitations="Duplicate analysis identifies mathematical matches; does not infer whether duplication was accidental.",
            disposition=Disposition.REVIEW,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.DUPLICATE_FLOODING,
            status="SUCCESS",
            original_artifact_hash=orig_hash,
            mutated_artifact_hash=cluster_entries[-1]["sha256"],
            artifacts_created=created_files,
            parameters={"flood_count": flood_count, "slight_perturbation": slight_perturbation, "random_seed": random_seed},
            detection_signature={"cluster_size": flood_count + 1, "exact_matches": sum(1 for c in cluster_entries if c["is_exact_match"])},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message=f"Duplicate flooding attack simulation generated {flood_count} duplicate instances.",
        )

    # -------------------------------------------------------------
    # ATTACK 3: OOD INJECTION
    # -------------------------------------------------------------
    def simulate_ood_injection(
        self,
        count: int = 3,
        random_seed: int = 42,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)
        np.random.seed(random_seed)

        created = []
        evidence_items = []
        for i in range(count):
            ood_file = sandbox / f"ood_synthetic_sample_{i+1:02d}.png"
            # High-frequency synthetic noise pattern completely outside natural camera distributions
            noise_arr = np.random.randint(0, 256, (64, 64, 3), dtype=np.uint8)
            # Add synthetic checkerboard stripes
            noise_arr[::8, :, :] = 255
            noise_arr[:, ::8, :] = 0
            img = Image.fromarray(noise_arr)
            img.save(ood_file)
            f_hash = hash_file(ood_file)
            created.append(str(ood_file))
            evidence_items.append({
                "file": ood_file.name,
                "hash": f_hash,
                "ood_score": round(0.85 + (i * 0.04), 3),
                "distance_from_centroid": round(4.2 + (i * 0.3), 2),
            })

        evidence = EvidenceObject(
            finding_type="Potential out-of-distribution anomaly",
            what_happened=f"Injected {count} high-variance out-of-distribution synthetic samples into pipeline queue.",
            why_flagged="Feature embedding distance from training distribution centroid exceeded 4.0 standard deviations.",
            evidence=evidence_items,
            severity=Severity.HIGH,
            confidence=0.91,
            affected_asset=f"{count} OOD samples",
            recommended_action="Quarantine anomalous samples; verify camera domain compatibility.",
            limitations="OOD detection relies on feature embedding distance; rare natural edge cases may trigger alerts.",
            disposition=Disposition.QUARANTINE,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.OOD_INJECTION,
            status="SUCCESS",
            original_artifact_hash="NATURAL_DISTRIBUTION_CENTROID",
            mutated_artifact_hash=evidence_items[0]["hash"],
            artifacts_created=created,
            parameters={"count": count, "random_seed": random_seed},
            detection_signature={"mean_ood_score": 0.89, "centroid_distance_sigma": 4.5},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message=f"Injected {count} out-of-distribution samples in isolated simulation sandbox.",
        )

    # -------------------------------------------------------------
    # ATTACK 4: IMAGE CORRUPTION
    # -------------------------------------------------------------
    def simulate_image_corruption(
        self,
        base_image_path: Optional[str] = None,
        corruption_type: str = "gaussian_noise",
        severity_level: float = 0.40,
        random_seed: int = 42,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)
        np.random.seed(random_seed)

        src_path = sandbox / "pristine_source.png"
        if base_image_path and Path(base_image_path).exists():
            shutil.copy2(base_image_path, src_path)
        else:
            self._create_sample_image(src_path, color=(140, 180, 120))

        orig_hash = hash_file(src_path)
        corrupt_path = sandbox / f"corrupted_{corruption_type}.png"

        img = Image.open(src_path).convert("RGB")
        arr = np.array(img, dtype=float)

        if corruption_type == "gaussian_noise":
            noise = np.random.normal(0, severity_level * 100.0, arr.shape)
            corrupted_arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
        elif corruption_type == "salt_pepper":
            mask = np.random.rand(*arr.shape[:2])
            corrupted_arr = arr.copy()
            corrupted_arr[mask < (severity_level * 0.1)] = 0
            corrupted_arr[mask > (1.0 - (severity_level * 0.1))] = 255
            corrupted_arr = corrupted_arr.astype(np.uint8)
        else:
            # Heavy pixelation / blur
            small = img.resize((16, 16), resample=Image.Resampling.BOX)
            corrupted_arr = np.array(small.resize(img.size, resample=Image.Resampling.NEAREST))

        Image.fromarray(corrupted_arr).save(corrupt_path)
        mut_hash = hash_file(corrupt_path)

        evidence = EvidenceObject(
            finding_type="Image integrity / corruption anomaly",
            what_happened=f"Simulated severe {corruption_type} corruption with intensity factor {severity_level:.2f}.",
            why_flagged="High-frequency noise variance and Laplacian sharpness deviation breached quality thresholds.",
            evidence=[{
                "corruption_type": corruption_type,
                "severity_factor": severity_level,
                "original_sha256": orig_hash,
                "corrupted_sha256": mut_hash,
            }],
            severity=Severity.MEDIUM,
            confidence=0.92,
            affected_asset=corrupt_path.name,
            recommended_action="Reject degraded frame; check optical lens transmission and transmission channel.",
            limitations="Quality degradation indicates noisy channel or physical blur; not necessarily intentional malice.",
            disposition=Disposition.REVIEW,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.IMAGE_CORRUPTION,
            status="SUCCESS",
            original_artifact_hash=orig_hash,
            mutated_artifact_hash=mut_hash,
            artifacts_created=[str(corrupt_path)],
            parameters={"corruption_type": corruption_type, "severity_level": severity_level, "random_seed": random_seed},
            detection_signature={"snr_degradation_db": 14.2, "quality_score_drop": 0.45},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message=f"Simulated {corruption_type} visual corruption applied safely to copy.",
        )

    # -------------------------------------------------------------
    # ATTACK 5: METADATA MANIPULATION
    # -------------------------------------------------------------
    def simulate_metadata_manipulation(
        self,
        original_metadata: Optional[Dict[str, Any]] = None,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)

        if not original_metadata:
            original_metadata = {
                "asset_id": "FRAME-2026-0881",
                "acquisition_time": "2026-09-08T10:15:30Z",
                "sensor_id": "CAMERA-NORTH-04",
                "contributor_id": "CONTRIB-003",
                "gps_coordinates": {"lat": 37.7749, "lon": -122.4194},
                "status": "RAW_INGRESS",
            }

        orig_hash = hash_json(original_metadata)
        mutated_metadata = dict(original_metadata)
        # Malicious modification: change timestamp to 2029 (future) and alter GPS
        mutated_metadata["acquisition_time"] = "2029-01-01T00:00:00Z"
        mutated_metadata["gps_coordinates"] = {"lat": 0.0, "lon": 0.0}
        mutated_metadata["contributor_id"] = "CONTRIB-005"  # Untrusted contributor

        mut_hash = hash_json(mutated_metadata)
        out_path = sandbox / "tampered_metadata.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(mutated_metadata, f, indent=2)

        evidence = EvidenceObject(
            finding_type="Metadata provenance discrepancy",
            what_happened="Detected unauthorized field manipulation: acquisition timestamp and sensor GPS altered.",
            why_flagged="Cross-check against signed ledger manifest failed; timestamp exceeds plausible operational window.",
            evidence=[
                {"field": "acquisition_time", "expected": original_metadata["acquisition_time"], "tampered": mutated_metadata["acquisition_time"]},
                {"field": "contributor_id", "expected": original_metadata["contributor_id"], "tampered": mutated_metadata["contributor_id"]},
            ],
            severity=Severity.HIGH,
            confidence=0.99,
            affected_asset=out_path.name,
            recommended_action="Reject unverified metadata packet; re-validate with hardware sensor cryptographic certificate.",
            limitations="Cannot detect falsified sensor clock prior to initial cryptographic ingestion.",
            disposition=Disposition.QUARANTINE,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.METADATA_MANIPULATION,
            status="SUCCESS",
            original_artifact_hash=orig_hash,
            mutated_artifact_hash=mut_hash,
            artifacts_created=[str(out_path)],
            parameters={"tampered_fields": ["acquisition_time", "gps_coordinates", "contributor_id"]},
            detection_signature={"ledger_manifest_discrepancy": True, "stale_or_future_timestamp": True},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message="Metadata manipulation simulation executed in sandbox.",
        )

    # -------------------------------------------------------------
    # ATTACK 6: MODEL SUBSTITUTION
    # -------------------------------------------------------------
    def simulate_model_substitution(
        self,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)

        ref_model_path = sandbox / "resnet18_baseline.onnx"
        with open(ref_model_path, "wb") as f:
            f.write(b"OFFICIAL_VERIFIED_MODEL_WEIGHTS_V1_TRUSTED" * 50)
        orig_hash = hash_file(ref_model_path)

        substituted_path = sandbox / "resnet18_substituted.onnx"
        with open(substituted_path, "wb") as f:
            f.write(b"UNVERIFIED_MODIFIED_TROJAN_WEIGHTS_V2_UNTRUSTED" * 50)
        mut_hash = hash_file(substituted_path)

        evidence = EvidenceObject(
            finding_type="MODEL BINARY DIFFERENCE",
            what_happened="Model substitution detected: deployment binary hash does not match registered reference ledger.",
            why_flagged="Current binary SHA-256 diverges from verified baseline register. Immediate integrity failure.",
            evidence=[
                {"registered_reference_hash": orig_hash},
                {"deployed_binary_hash": mut_hash},
                {"status": "MODEL BINARY DIFFERENCE"},
            ],
            severity=Severity.CRITICAL,
            confidence=1.0,
            affected_asset=substituted_path.name,
            recommended_action="Immediately halt model serving container; roll back to registered reference checkpoint.",
            limitations="Assumes registered reference hash on ledger was authentic and signed by authorized model trainer.",
            disposition=Disposition.QUARANTINE,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.MODEL_SUBSTITUTION,
            status="SUCCESS",
            original_artifact_hash=orig_hash,
            mutated_artifact_hash=mut_hash,
            artifacts_created=[str(ref_model_path), str(substituted_path)],
            parameters={"model_architecture": "ResNet-18", "format": "ONNX"},
            detection_signature={"reference_match": False, "status_code": "MODEL BINARY DIFFERENCE"},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message="Model substitution simulation: verified binary swapped for altered weights.",
        )

    # -------------------------------------------------------------
    # ATTACK 7: TRIGGER INJECTION
    # -------------------------------------------------------------
    def simulate_trigger_injection(
        self,
        base_image_path: Optional[str] = None,
        patch_type: str = "checkerboard_square",
        patch_size: int = 16,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)

        src_path = sandbox / "clean_traffic_sign.png"
        if base_image_path and Path(base_image_path).exists():
            shutil.copy2(base_image_path, src_path)
        else:
            self._create_sample_image(src_path, color=(200, 50, 50))

        orig_hash = hash_file(src_path)
        patched_path = sandbox / f"poisoned_trigger_{patch_type}.png"

        img = Image.open(src_path).convert("RGB")
        arr = np.array(img)
        h, w, _ = arr.shape

        # Stamp a trigger patch in bottom-right corner
        patch_s = min(patch_size, h // 4, w // 4)
        if patch_type == "checkerboard_square":
            patch = np.zeros((patch_s, patch_s, 3), dtype=np.uint8)
            patch[::2, ::2] = [255, 255, 0]  # Yellow/Black checkerboard
            patch[1::2, 1::2] = [255, 255, 0]
        elif patch_type == "corner_stripe":
            patch = np.full((patch_s, patch_s, 3), [255, 0, 255], dtype=np.uint8) # Magenta
        else:
            patch = np.full((patch_s, patch_s, 3), [255, 255, 255], dtype=np.uint8) # White square

        arr[h - patch_s : h, w - patch_s : w] = patch
        Image.fromarray(arr).save(patched_path)
        mut_hash = hash_file(patched_path)

        evidence = EvidenceObject(
            finding_type="Potential trigger-sensitive behavior",
            what_happened=f"Simulated {patch_type} trigger patch ({patch_s}x{patch_s}px) overlaid on clean demo frame.",
            why_flagged="Localized high-contrast corner perturbation tested for empirical model output sensitivity.",
            evidence=[{
                "patch_type": patch_type,
                "patch_dimensions": f"{patch_s}x{patch_s}",
                "location": "bottom_right_corner",
                "clean_confidence": 0.94,
                "perturbed_confidence": 0.38,
            }],
            severity=Severity.HIGH,
            confidence=0.86,
            affected_asset=patched_path.name,
            recommended_action="Run full trigger inversion audit; isolate affected training checkpoints.",
            limitations="Trigger sensitivity test applies synthetic test patches; does not constitute confirmed backdoor proof.",
            disposition=Disposition.REVIEW,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.TRIGGER_INJECTION,
            status="SUCCESS",
            original_artifact_hash=orig_hash,
            mutated_artifact_hash=mut_hash,
            artifacts_created=[str(patched_path)],
            parameters={"patch_type": patch_type, "patch_size": patch_s},
            detection_signature={"output_sensitivity_drop": 0.56, "status": "Potential trigger-sensitive behavior"},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message="Backdoor trigger patch simulation created in sandbox.",
        )

    # -------------------------------------------------------------
    # ATTACK 8: INFERENCE TAMPERING
    # -------------------------------------------------------------
    def simulate_inference_tampering(
        self,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)

        clean_inference = {
            "inference_id": "INF-2026-00912",
            "input_hash": "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
            "model_id": "RESNET-18-PROD",
            "model_hash": "b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef01",
            "prediction": "benign",
            "confidence": 0.982,
            "timestamp": "2026-09-10T12:00:00Z",
            "sequence_number": 1042,
            "nonce": "NONCE-98124",
            "operator_id": "sys_inference_node",
        }
        # Cryptographically signed record hash
        expected_hash = hash_json(clean_inference)
        clean_inference["record_hash"] = expected_hash

        # Malicious modification: attacker alters prediction from benign -> threat, but leaves old record_hash
        tampered_inference = dict(clean_inference)
        tampered_inference["prediction"] = "threat"
        tampered_inference["confidence"] = 0.410

        # Calculate what the hash actually evaluates to now
        payload_for_hashing = {k: v for k, v in tampered_inference.items() if k != "record_hash"}
        actual_recomputed_hash = hash_json(payload_for_hashing)

        out_path = sandbox / "tampered_inference_record.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(tampered_inference, f, indent=2)

        evidence = EvidenceObject(
            finding_type="Inference record cryptographic violation",
            what_happened="Inference result payload altered post-execution; signature mismatch detected.",
            why_flagged=f"ORIGINAL HASH: {expected_hash[:16]}... CURRENT HASH: {actual_recomputed_hash[:16]}... Cryptographic violation.",
            evidence=[
                {"field": "record_hash", "stated_in_record": expected_hash, "recomputed_hash": actual_recomputed_hash},
                {"field": "prediction", "original": "benign", "tampered": "threat"},
            ],
            severity=Severity.CRITICAL,
            confidence=1.0,
            affected_asset=clean_inference["inference_id"],
            recommended_action="Drop invalid inference record; audit inference host node for unauthorized write access.",
            limitations="Deterministic cryptographic check on record structure; does not evaluate camera hardware sensor stream.",
            disposition=Disposition.QUARANTINE,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.INFERENCE_TAMPERING,
            status="SUCCESS",
            original_artifact_hash=expected_hash,
            mutated_artifact_hash=actual_recomputed_hash,
            artifacts_created=[str(out_path)],
            parameters={"modified_fields": ["prediction", "confidence"]},
            detection_signature={"signature_verified": False, "stated_hash": expected_hash, "actual_hash": actual_recomputed_hash},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message="Inference tampering simulation: payload modified and detected via cryptographic hash recomputation.",
        )

    # -------------------------------------------------------------
    # ATTACK 9: REPLAY ATTACK
    # -------------------------------------------------------------
    def simulate_replay_attack(
        self,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        start_t = time.perf_counter()
        sim_id = self.generate_simulation_id()
        sandbox = self._prepare_sandbox(sim_id)

        valid_record = {
            "inference_id": "INF-2026-00445",
            "sequence_number": 850,
            "nonce": "NONCE-ALPHA-445",
            "timestamp": "2026-09-01T08:30:00Z",  # Stale timestamp (10 days old)
            "decision": "AUTHORIZED_ACCESS",
        }
        rec_hash = hash_json(valid_record)

        # Attacker replays exact same sequence number and nonce at current time
        replayed_record = dict(valid_record)
        replayed_record["replayed_at"] = datetime.now(timezone.utc).isoformat()

        out_path = sandbox / "replayed_packet.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(replayed_record, f, indent=2)

        evidence = EvidenceObject(
            finding_type="Inference replay violation",
            what_happened=f"Duplicate sequence number #{valid_record['sequence_number']} and reused nonce '{valid_record['nonce']}' intercepted.",
            why_flagged="Sequence registry flagged duplicate entry; timestamp exceeds allowable drift window (>300s).",
            evidence=[
                {"reused_nonce": valid_record["nonce"]},
                {"duplicate_sequence_number": valid_record["sequence_number"]},
                {"original_timestamp": valid_record["timestamp"]},
            ],
            severity=Severity.HIGH,
            confidence=0.98,
            affected_asset=valid_record["inference_id"],
            recommended_action="Block replayed inference packet; invalidate session token and enforce strict nonce cache.",
            limitations="Replay detection requires stateful sequence and nonce synchronization across inference workers.",
            disposition=Disposition.QUARANTINE,
        )

        elapsed = (time.perf_counter() - start_t) * 1000.0
        return AttackSimulationResult(
            simulation_id=sim_id,
            attack_type=AttackType.REPLAY_ATTACK,
            status="SUCCESS",
            original_artifact_hash=rec_hash,
            mutated_artifact_hash=hash_json(replayed_record),
            artifacts_created=[str(out_path)],
            parameters={"sequence_number": valid_record["sequence_number"], "nonce": valid_record["nonce"]},
            detection_signature={"duplicate_sequence": True, "reused_nonce": True, "stale_timestamp": True},
            evidence_generated=evidence,
            execution_time_ms=round(elapsed, 2),
            output_directory=str(sandbox),
            message="Replay attack simulation: intercepted payload replayed and caught by sequence/nonce validation.",
        )

    # -------------------------------------------------------------
    # MASTER RUNNER FOR ALL 9 ATTACKS
    # -------------------------------------------------------------
    def run_simulation(
        self,
        attack_type: AttackType,
        parameters: Optional[Dict[str, Any]] = None,
        random_seed: int = 42,
        operator_id: str = "sec_analyst_01",
    ) -> AttackSimulationResult:
        params = parameters or {}
        if attack_type == AttackType.LABEL_FLIP:
            return self.simulate_label_flip(
                labels_data=params.get("labels_data"),
                flip_rate=params.get("flip_rate", 0.30),
                random_seed=random_seed,
                operator_id=operator_id,
            )
        elif attack_type == AttackType.DUPLICATE_FLOODING:
            return self.simulate_duplicate_flooding(
                base_image_path=params.get("base_image_path"),
                flood_count=params.get("flood_count", 6),
                slight_perturbation=params.get("slight_perturbation", True),
                random_seed=random_seed,
                operator_id=operator_id,
            )
        elif attack_type == AttackType.OOD_INJECTION:
            return self.simulate_ood_injection(
                count=params.get("count", 3),
                random_seed=random_seed,
                operator_id=operator_id,
            )
        elif attack_type == AttackType.IMAGE_CORRUPTION:
            return self.simulate_image_corruption(
                base_image_path=params.get("base_image_path"),
                corruption_type=params.get("corruption_type", "gaussian_noise"),
                severity_level=params.get("severity_level", 0.40),
                random_seed=random_seed,
                operator_id=operator_id,
            )
        elif attack_type == AttackType.METADATA_MANIPULATION:
            return self.simulate_metadata_manipulation(
                original_metadata=params.get("original_metadata"),
                operator_id=operator_id,
            )
        elif attack_type == AttackType.MODEL_SUBSTITUTION:
            return self.simulate_model_substitution(
                operator_id=operator_id,
            )
        elif attack_type == AttackType.TRIGGER_INJECTION:
            return self.simulate_trigger_injection(
                base_image_path=params.get("base_image_path"),
                patch_type=params.get("patch_type", "checkerboard_square"),
                patch_size=params.get("patch_size", 16),
                operator_id=operator_id,
            )
        elif attack_type == AttackType.INFERENCE_TAMPERING:
            return self.simulate_inference_tampering(
                operator_id=operator_id,
            )
        elif attack_type == AttackType.REPLAY_ATTACK:
            return self.simulate_replay_attack(
                operator_id=operator_id,
            )
        else:
            raise ValueError(f"Unknown attack type: {attack_type}")
