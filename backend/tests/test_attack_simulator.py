"""
Unit Tests for Security Lab / Attack Simulator (Section 24)
Tests all 9 attack simulation types and safety invariants.
"""

import shutil
from pathlib import Path
from simulator.attack_simulator import AttackSimulator, AttackType


def test_all_nine_attacks(tmp_path):
    sim = AttackSimulator(base_sim_dir=str(tmp_path / "sims"))

    # 1. Label flip
    res1 = sim.run_simulation(AttackType.LABEL_FLIP, {"flip_rate": 0.20})
    assert res1.status == "SUCCESS"
    assert res1.attack_type == AttackType.LABEL_FLIP
    assert res1.simulation_id.startswith("SIM-2026-")
    assert "label inconsistency" in res1.evidence_generated.finding_type.lower()
    assert Path(res1.output_directory).exists()

    # 2. Duplicate flooding
    res2 = sim.run_simulation(AttackType.DUPLICATE_FLOODING, {"flood_count": 4})
    assert res2.status == "SUCCESS"
    assert res2.attack_type == AttackType.DUPLICATE_FLOODING
    assert "duplicate flooding" in res2.evidence_generated.finding_type.lower()
    assert len(res2.artifacts_created) >= 4

    # 3. OOD injection
    res3 = sim.run_simulation(AttackType.OOD_INJECTION, {"count": 2})
    assert res3.status == "SUCCESS"
    assert res3.attack_type == AttackType.OOD_INJECTION
    assert "out-of-distribution" in res3.evidence_generated.finding_type.lower()

    # 4. Image corruption
    res4 = sim.run_simulation(AttackType.IMAGE_CORRUPTION, {"corruption_type": "gaussian_noise"})
    assert res4.status == "SUCCESS"
    assert res4.attack_type == AttackType.IMAGE_CORRUPTION
    assert "corruption" in res4.evidence_generated.finding_type.lower()

    # 5. Metadata manipulation
    res5 = sim.run_simulation(AttackType.METADATA_MANIPULATION)
    assert res5.status == "SUCCESS"
    assert res5.attack_type == AttackType.METADATA_MANIPULATION
    assert "metadata" in res5.evidence_generated.finding_type.lower()

    # 6. Model substitution
    res6 = sim.run_simulation(AttackType.MODEL_SUBSTITUTION)
    assert res6.status == "SUCCESS"
    assert res6.attack_type == AttackType.MODEL_SUBSTITUTION
    assert res6.evidence_generated.finding_type == "MODEL BINARY DIFFERENCE"
    assert res6.original_artifact_hash != res6.mutated_artifact_hash

    # 7. Trigger injection
    res7 = sim.run_simulation(AttackType.TRIGGER_INJECTION, {"patch_type": "checkerboard_square"})
    assert res7.status == "SUCCESS"
    assert res7.attack_type == AttackType.TRIGGER_INJECTION
    assert "trigger-sensitive" in res7.evidence_generated.finding_type.lower()

    # 8. Inference tampering
    res8 = sim.run_simulation(AttackType.INFERENCE_TAMPERING)
    assert res8.status == "SUCCESS"
    assert res8.attack_type == AttackType.INFERENCE_TAMPERING
    assert "cryptographic" in res8.evidence_generated.finding_type.lower()
    assert res8.original_artifact_hash != res8.mutated_artifact_hash

    # 9. Replay attack
    res9 = sim.run_simulation(AttackType.REPLAY_ATTACK)
    assert res9.status == "SUCCESS"
    assert res9.attack_type == AttackType.REPLAY_ATTACK
    assert "replay" in res9.evidence_generated.finding_type.lower()


def test_safety_invariants_never_modify_source(tmp_path):
    # Ensure source file outside sandbox is not modified
    sim = AttackSimulator(base_sim_dir=str(tmp_path / "sims"))
    pristine_file = tmp_path / "original_pristine.png"
    # Create sample image
    from PIL import Image
    import numpy as np
    Image.fromarray((np.ones((32, 32, 3)) * 200).astype(np.uint8)).save(pristine_file)
    from app.core.hashing import hash_file
    pristine_hash_before = hash_file(pristine_file)

    # Run duplicate flooding and corruption pointing to pristine_file
    sim.run_simulation(AttackType.DUPLICATE_FLOODING, {"base_image_path": str(pristine_file)})
    sim.run_simulation(AttackType.IMAGE_CORRUPTION, {"base_image_path": str(pristine_file)})
    sim.run_simulation(AttackType.TRIGGER_INJECTION, {"base_image_path": str(pristine_file)})

    pristine_hash_after = hash_file(pristine_file)
    assert pristine_hash_before == pristine_hash_after, "Safety violation: Source file was mutated in-place!"
