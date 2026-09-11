"""
TrustLens - Unit Tests for Model & Inference Security (Member 3 - Section 41)
Tests:
1. test_model_fingerprint: Validates SHA-256 computation, parameter count, and structural inspection.
2. test_model_substitution: Validates matching baseline and verifies EXACT Section 13 language for mismatches.
3. test_inference_run_and_provenance: Validates inference output schema and canonical 10-field provenance record binding.
4. test_tamper_detection: Tests controlled mutation (prediction / confidence / timestamp) and avalanche detection.
5. test_replay_detection: Tests duplicate sequence numbers, reused nonces, repeated record hashes, and stale timestamps.
6. test_trigger_sensitivity: Tests synthetic patches (square, corner_square, stripe) and Section 18 wording.
7. test_ledger_linkage: Validates that all events are committed to the tamper-evident ledger.
"""

from datetime import datetime, timezone, timedelta
import json
import secrets
import pytest
from PIL import Image

from app.core.hashing import hash_bytes, hash_file, hash_json, canonicalize_json
from app.provenance.ledger import ledger_instance, TamperEvidentLedger
from app.services.cv_engine import model_manager, LocalCVModel
from app.services.model_security import (
    safe_inspect_model,
    register_model_fingerprint,
    verify_model_substitution,
)
from app.services.inference_provenance import (
    create_provenance_record,
    compute_canonical_record_hash,
    run_inference,
    run_tamper_test,
    run_replay_test,
    tracker,
)
from app.services.trigger_sensitivity import (
    apply_synthetic_patch,
    evaluate_trigger_sensitivity,
)


# -------------------------------------------------------------
# Test 1: Model Fingerprinting (Section 12 & 41)
# -------------------------------------------------------------
def test_model_fingerprint():
    model = model_manager.get_model("resnet18-demo-v1")
    fp = model.get_fingerprint()

    assert fp["model_id"] == "resnet18-demo-v1"
    assert len(fp["sha256"]) == 64  # Valid SHA-256 hex string
    assert fp["parameter_count"] > 0
    assert fp["input_shape"] == [1, 3, 224, 224]
    assert fp["output_shape"] == [1, 10]
    assert "military_truck" in fp["classes"]

    # Test safe inspection of arbitrary binary without code execution
    dummy_model_bytes = b"MOCK_MODEL_WEIGHTS_VERSION_2_SECURE"
    inspection = safe_inspect_model(dummy_model_bytes, filename="custom_cnn.bin")
    assert inspection["sha256"] == hash_bytes(dummy_model_bytes)
    assert inspection["file_size_bytes"] == len(dummy_model_bytes)
    assert inspection["parameter_count"] > 0


# -------------------------------------------------------------
# Test 2: Model Substitution Check (Section 13 & 41)
# -------------------------------------------------------------
def test_model_substitution_exact_language():
    model = model_manager.get_model("resnet18-demo-v1")
    valid_hash = model.model_hash

    # Case A: REFERENCE MATCH
    match_result = verify_model_substitution(
        model_id="resnet18-demo-v1",
        uploaded_model_hash=valid_hash,
        reference_model_hash=valid_hash,
    )
    assert match_result["is_match"] is True
    assert match_result["status"] == "REFERENCE MATCH"
    assert match_result["message"] == "Model binary matches registered baseline hash. Integrity verified."

    # Case B: MODEL BINARY DIFFERENCE
    tampered_hash = "f" * 64
    mismatch_result = verify_model_substitution(
        model_id="resnet18-demo-v1",
        uploaded_model_hash=tampered_hash,
        reference_model_hash=valid_hash,
    )
    assert mismatch_result["is_match"] is False
    assert mismatch_result["status"] == "MODEL BINARY DIFFERENCE"
    # Verify exact required wording
    assert f"Expected: {valid_hash}, Received: {tampered_hash}" in mismatch_result["message"]
    assert "Discrepancy may indicate unauthorized model substitution, silent update, or retraining." in mismatch_result["message"]
    # Verify non-accusatory rule: Must NOT say "malicious attack" or "backdoored"
    assert "malicious" not in mismatch_result["message"].lower()


# -------------------------------------------------------------
# Test 3: Inference Run & Provenance Binding (Section 14, 15, 41)
# -------------------------------------------------------------
def test_inference_run_and_provenance_binding():
    operator = "OP-TEST-01"
    response = run_inference(
        demo_image_name="military_truck.png",
        operator_id=operator,
        is_demo=True,
    )

    assert response["inference_id"].startswith("INF-2026-")
    assert response["prediction"] in model_manager.get_model("resnet18-demo-v1").classes
    assert 0.0 <= response["confidence"] <= 1.0
    assert len(response["input_hash"]) == 64
    assert len(response["model_hash"]) == 64
    assert len(response["preprocessing_hash"]) == 64

    # Verify cryptographic binding of the 10 fields in provenance record
    prov = response["provenance_record"]
    assert prov["operator_id"] == operator
    assert prov["sequence_number"] >= 1
    assert len(prov["nonce"]) == 16  # 8 bytes in hex = 16 characters
    assert len(prov["previous_record_hash"]) == 64
    assert len(prov["record_hash"]) == 64

    # Validate that canonical re-hash produces exact record_hash
    recomputed = compute_canonical_record_hash(prov)
    assert recomputed == prov["record_hash"]


# -------------------------------------------------------------
# Test 4: Tamper Detection (Section 16 & 41)
# -------------------------------------------------------------
def test_tamper_detection_endpoint_logic():
    # 1. Run inference to generate a clean baseline record
    run = run_inference(demo_image_name="civilian_car.png", operator_id="OP-TAMPER-TEST", is_demo=True)
    clean_record = run["provenance_record"]

    # 2. Test unmodified record (should verify as intact)
    intact_result = run_tamper_test(demo_record=clean_record, modified_fields={})
    assert intact_result["tamper_detected"] is False
    assert intact_result["status"] == "VERIFIED: RECORD INTACT"
    assert intact_result["original_hash"] == intact_result["current_hash"]

    # 3. Modify 'prediction' field (e.g. from detected class to 'military_truck')
    tampered_pred = run_tamper_test(
        demo_record=clean_record,
        modified_fields={"prediction": "military_truck", "confidence": 0.999},
    )
    assert tampered_pred["tamper_detected"] is True
    assert tampered_pred["status"] == "TAMPER DETECTED: RECORD HASH MISMATCH"
    assert tampered_pred["original_hash"] != tampered_pred["current_hash"]
    assert len(tampered_pred["modified_fields"]) > 0
    assert "avalanche effect" in tampered_pred["explanation"].lower()

    # 4. Modify timestamp field
    tampered_ts = run_tamper_test(
        demo_record=clean_record,
        modified_fields={"timestamp": "2025-01-01T00:00:00Z"},
    )
    assert tampered_ts["tamper_detected"] is True
    assert tampered_ts["status"] == "TAMPER DETECTED: RECORD HASH MISMATCH"
    assert tampered_ts["original_hash"] != tampered_ts["current_hash"]


# -------------------------------------------------------------
# Test 5: Replay Detection (Section 17 & 41)
# -------------------------------------------------------------
def test_replay_detection():
    op = "OP-REPLAY-AGENT"

    # Step 1: Create a genuine initial record
    rec1 = run_inference(demo_image_name="surveillance_drone.png", operator_id=op)["provenance_record"]

    # Attempt to replay the exact same record
    replay_same = run_replay_test(rec1)
    assert replay_same["replay_detected"] is True
    assert "Duplicate record hash detected" in " ".join(replay_same["violations"])
    assert "Reused nonce detected" in " ".join(replay_same["violations"])

    # Step 2: Fabricate record with duplicate sequence number
    dup_seq_record = dict(rec1)
    dup_seq_record["nonce"] = secrets.token_hex(8)  # New nonce
    dup_seq_record["record_hash"] = secrets.token_hex(32)  # New hash
    dup_seq_test = run_replay_test(dup_seq_record)
    assert dup_seq_test["replay_detected"] is True
    assert "Duplicate or regressive sequence number" in " ".join(dup_seq_test["violations"])

    # Step 3: Stale timestamp check
    stale_record = dict(rec1)
    stale_record["nonce"] = secrets.token_hex(8)
    stale_record["record_hash"] = secrets.token_hex(32)
    stale_record["sequence_number"] = tracker.get_next_sequence_number(op)
    # Set timestamp 2 days ago
    stale_record["timestamp"] = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
    stale_test = run_replay_test(stale_record)
    assert stale_test["replay_detected"] is True
    assert "Stale or future timestamp" in " ".join(stale_test["violations"])


# -------------------------------------------------------------
# Test 6: Trigger Sensitivity Demo (Section 18 & 41)
# -------------------------------------------------------------
def test_trigger_sensitivity():
    # Test all three required synthetic patch types: square, corner_square, stripe
    for patch in ["square", "corner_square", "stripe"]:
        result = evaluate_trigger_sensitivity(
            model_id="resnet18-demo-v1",
            patch_type=patch,
            patch_size=32,
            demo_image_name="military_truck.png",
        )

        assert "patch_type" in result
        assert result["patch_type"] == patch
        assert "baseline_prediction" in result
        assert "triggered_prediction" in result
        assert "delta_confidence" in result
        assert "patch_coordinates" in result

        # Strict wording validation
        if result["potential_trigger_sensitive"]:
            assert "Potential trigger-sensitive behavior" in result["finding"]
        else:
            assert "No significant trigger sensitivity detected" in result["finding"]

        # NEVER claim "confirmed backdoor"
        assert "confirmed backdoor" not in result["finding"].lower()
        assert "confirmed backdoor" not in result["limitations"].lower()
        assert "Limitation Note:" in result["limitations"]


# -------------------------------------------------------------
# Test 7: Tamper-Evident Ledger Integrity
# -------------------------------------------------------------
def test_tamper_evident_ledger_verification():
    verification = ledger_instance.verify_chain()
    assert verification["is_valid"] is True
    assert verification["status"] == "CHAIN INTACT: ALL BLOCKS CRYPTOGRAPHICALLY VERIFIED"

    # Save original block 1 state to restore after test
    orig_b = ledger_instance.get_block(1)

    try:
        # Simulate tampering with a block in the ledger
        ledger_tamper = ledger_instance.simulate_tampering(
            block_index=1,
            modified_fields={"artifact_hash": "e" * 64},
        )
        tampered_verification = ledger_tamper["verification_result"]
        assert tampered_verification["is_valid"] is False
        assert tampered_verification["broken_index"] >= 1
    finally:
        if orig_b:
            with ledger_instance.db_factory() as db:
                from app.models.orm_models import AuditLog
                rec = db.query(AuditLog).filter(AuditLog.block_index == 1).first()
                if rec:
                    rec.entity_id = orig_b.entity_id
                    rec.block_hash = orig_b.block_hash
                    rec.payload_hash = orig_b.payload_hash
                    rec.payload_json = json.dumps(orig_b.payload, sort_keys=True)
                    rec.previous_hash = orig_b.previous_hash
                    db.commit()
