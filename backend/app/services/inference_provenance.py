"""
TrustLens - Inference Provenance & Security Verification Service (Member 3)
Implements:
- Section 14: POST /api/inference/run execution
- Section 15: Cryptographic Inference Provenance Record Binding
- Section 16: Tamper Detection Test (Controlled field modification & hash cascade)
- Section 17: Replay Detection Test (Sequence, nonce, timestamp, chain checks)
"""

import base64
from datetime import datetime, timezone, timedelta
import io
import secrets
from typing import Any, Dict, List, Optional, Tuple
from PIL import Image

from app.core.hashing import canonicalize_json, hash_bytes, hash_json
from app.provenance.ledger import ledger_instance
from app.services.cv_engine import model_manager, LocalCVModel


class ProvenanceTracker:
    """
    In-memory and ledger-backed registry tracking live inference provenance streams
    per operator to enforce sequence monotonicity, nonce uniqueness, and hash chaining.
    """

    def __init__(self):
        # operator_id -> list of records
        self.operator_records: Dict[str, List[Dict[str, Any]]] = {}
        # Set of seen nonces across all operators
        self.seen_nonces: set = set()
        # Set of seen record hashes across all operators
        self.seen_record_hashes: set = set()
        # Storage of demo records for tamper testing
        self.demo_records: Dict[str, Dict[str, Any]] = {}

    def get_latest_record(self, operator_id: str) -> Optional[Dict[str, Any]]:
        records = self.operator_records.get(operator_id, [])
        return records[-1] if records else None

    def get_next_sequence_number(self, operator_id: str) -> int:
        records = self.operator_records.get(operator_id, [])
        return len(records) + 1

    def record_inference(self, record: Dict[str, Any], is_demo: bool = True):
        op_id = record["operator_id"]
        if op_id not in self.operator_records:
            self.operator_records[op_id] = []

        self.operator_records[op_id].append(record)
        self.seen_nonces.add(record["nonce"])
        self.seen_record_hashes.add(record["record_hash"])

        if is_demo:
            self.demo_records[record["record_hash"]] = record

        # Also append to tamper-evident ledger
        ledger_instance.append_block(
            artifact_type="INFERENCE_RECORD",
            artifact_hash=record["record_hash"],
            metadata={
                "operator_id": op_id,
                "sequence_number": record["sequence_number"],
                "model_id": record["model_id"],
                "input_hash": record["input_hash"],
            },
        )


tracker = ProvenanceTracker()


def compute_canonical_record_hash(record_dict: Dict[str, Any]) -> str:
    """
    Computes the SHA-256 hash of the canonical JSON representation of the
    10 bound fields (excluding record_hash itself).
    """
    bound_fields = {
        "sequence_number": record_dict["sequence_number"],
        "nonce": record_dict["nonce"],
        "timestamp": record_dict["timestamp"],
        "operator_id": record_dict["operator_id"],
        "model_id": record_dict["model_id"],
        "model_hash": record_dict["model_hash"],
        "input_hash": record_dict["input_hash"],
        "preprocessing_hash": record_dict["preprocessing_hash"],
        "result_hash": record_dict["result_hash"],
        "previous_record_hash": record_dict["previous_record_hash"],
    }
    return hash_json(bound_fields)


def create_provenance_record(
    input_hash: str,
    model_id: str,
    model_hash: str,
    preprocessing_hash: str,
    result_hash: str,
    operator_id: str = "OP-8492",
    custom_timestamp: Optional[str] = None,
    custom_sequence: Optional[int] = None,
    custom_nonce: Optional[str] = None,
    custom_previous_hash: Optional[str] = None,
    commit_to_tracker: bool = True,
    is_demo: bool = True,
) -> Dict[str, Any]:
    """
    Cryptographically binds the 10 inference provenance fields into a chained record.
    """
    timestamp = custom_timestamp or datetime.now(timezone.utc).isoformat()
    sequence_number = custom_sequence or tracker.get_next_sequence_number(operator_id)
    nonce = custom_nonce or secrets.token_hex(8)

    if custom_previous_hash is not None:
        previous_record_hash = custom_previous_hash
    else:
        latest = tracker.get_latest_record(operator_id)
        previous_record_hash = latest["record_hash"] if latest else ("0" * 64)

    record = {
        "sequence_number": sequence_number,
        "nonce": nonce,
        "timestamp": timestamp,
        "operator_id": operator_id,
        "model_id": model_id,
        "model_hash": model_hash,
        "input_hash": input_hash,
        "preprocessing_hash": preprocessing_hash,
        "result_hash": result_hash,
        "previous_record_hash": previous_record_hash,
    }

    record["record_hash"] = compute_canonical_record_hash(record)

    if commit_to_tracker:
        tracker.record_inference(record, is_demo=is_demo)

    return record


def run_inference(
    image_bytes: Optional[bytes] = None,
    demo_image_name: Optional[str] = None,
    image_base64: Optional[str] = None,
    model_id: str = "resnet18-demo-v1",
    operator_id: str = "OP-8492",
    preprocessing_config: Optional[Dict[str, Any]] = None,
    is_demo: bool = True,
) -> Dict[str, Any]:
    """
    Executes Section 14 Local CV inference and automatically binds Section 15 Provenance Record.
    """
    # 1. Resolve image bytes
    if image_bytes is None:
        if image_base64:
            image_bytes = base64.b64decode(image_base64)
        elif demo_image_name:
            image_bytes = model_manager.get_demo_image(demo_image_name)
        else:
            image_bytes = model_manager.get_demo_image("military_truck.png")

    input_hash = hash_bytes(image_bytes)

    # 2. Preprocessing
    model = model_manager.get_model(model_id)
    pil_img = Image.open(io.BytesIO(image_bytes))
    tensor, canonical_prep_config = model.preprocess_image(pil_img, preprocessing_config)
    preprocessing_hash = hash_json(canonical_prep_config)

    # 3. Model Prediction
    prediction, confidence, probabilities = model.predict(tensor, pil_img)

    # Result hash binds prediction and confidence
    result_payload = {"prediction": prediction, "confidence": confidence}
    result_hash = hash_json(result_payload)

    # 4. Generate Provenance Record
    provenance_rec = create_provenance_record(
        input_hash=input_hash,
        model_id=model.model_id,
        model_hash=model.model_hash,
        preprocessing_hash=preprocessing_hash,
        result_hash=result_hash,
        operator_id=operator_id,
        commit_to_tracker=True,
        is_demo=is_demo,
    )

    inference_id = f"INF-2026-{secrets.token_hex(4).upper()}"
    timestamp = provenance_rec["timestamp"]

    return {
        "inference_id": inference_id,
        "model_id": model.model_id,
        "model_hash": model.model_hash,
        "input_hash": input_hash,
        "preprocessing_hash": preprocessing_hash,
        "prediction": prediction,
        "confidence": confidence,
        "probabilities": probabilities,
        "timestamp": timestamp,
        "provenance_record": provenance_rec,
    }


def run_tamper_test(
    record_hash: Optional[str] = None,
    demo_record: Optional[Dict[str, Any]] = None,
    modified_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Section 16: Tamper Detection Endpoint logic.
    Operates ONLY on demo/test records.
    Allows controlled field modification, recomputes canonical hash, and reports
    ORIGINAL HASH vs CURRENT HASH demonstrating cryptographic avalanche effect.
    """
    modified_fields = modified_fields or {}

    # Target record selection
    target_rec: Optional[Dict[str, Any]] = None
    if demo_record:
        target_rec = dict(demo_record)
    elif record_hash and record_hash in tracker.demo_records:
        target_rec = dict(tracker.demo_records[record_hash])
    elif tracker.demo_records:
        target_rec = dict(next(reversed(tracker.demo_records.values())))
    else:
        # Create a fresh demo record if none exists
        fresh_run = run_inference(demo_image_name="military_truck.png", is_demo=True)
        target_rec = dict(fresh_run["provenance_record"])

    original_hash = target_rec.get("record_hash", "")
    mutated_rec = dict(target_rec)
    diffs = []

    # Apply controlled modifications
    for field_name, new_val in modified_fields.items():
        old_val = target_rec.get(field_name, None)

        # If modifying high-level semantic fields like 'prediction' or 'confidence',
        # cascadingly recompute result_hash
        if field_name in ["prediction", "confidence"]:
            base_pred = new_val if field_name == "prediction" else "civilian_vehicle"
            base_conf = new_val if field_name == "confidence" else 0.95
            mutated_result_hash = hash_json({"prediction": base_pred, "confidence": base_conf})
            diffs.append({
                "field": f"{field_name} -> result_hash",
                "original_value": target_rec.get("result_hash"),
                "modified_value": mutated_result_hash,
            })
            mutated_rec["result_hash"] = mutated_result_hash
        else:
            diffs.append({
                "field": field_name,
                "original_value": old_val,
                "modified_value": new_val,
            })
            mutated_rec[field_name] = new_val

    # Recompute canonical record hash on the modified fields
    current_hash = compute_canonical_record_hash(mutated_rec)
    tamper_detected = (current_hash != original_hash)

    if tamper_detected:
        status = "TAMPER DETECTED: RECORD HASH MISMATCH"
        explanation = (
            f"Cryptographic binding broken: modification of {len(diffs)} field(s) "
            f"altered the canonical serialized JSON, resulting in a completely divergent "
            f"SHA-256 digest due to the cryptographic avalanche effect. "
            f"Expected: {original_hash}, Recomputed: {current_hash}."
        )
    else:
        status = "VERIFIED: RECORD INTACT"
        explanation = "No modifications detected. Recomputed SHA-256 matches the recorded digest."

    # Log tamper test to ledger
    ledger_instance.append_block(
        artifact_type="TAMPER_VERIFICATION_TEST",
        artifact_hash=current_hash,
        metadata={
            "original_hash": original_hash,
            "current_hash": current_hash,
            "tamper_detected": tamper_detected,
            "modified_fields_count": len(diffs),
        },
    )

    return {
        "tamper_detected": tamper_detected,
        "status": status,
        "original_hash": original_hash,
        "current_hash": current_hash,
        "modified_fields": diffs,
        "explanation": explanation,
    }


def run_replay_test(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Section 17: Replay Detection Endpoint logic.
    Detects:
    1. Duplicate sequence numbers
    2. Reused nonces
    3. Repeated record hashes
    4. Stale timestamps (outside allowed window)
    5. Invalid ordering
    6. Broken hash chain
    """
    violations: List[str] = []
    op_id = record.get("operator_id", "UNKNOWN")
    seq_num = record.get("sequence_number")
    nonce = record.get("nonce")
    rec_hash = record.get("record_hash")
    ts_str = record.get("timestamp")
    prev_hash = record.get("previous_record_hash")

    # 1. Nonce check
    if nonce in tracker.seen_nonces:
        violations.append(f"Reused nonce detected: '{nonce}' was already used in a previous record.")

    # 2. Record hash check
    if rec_hash in tracker.seen_record_hashes:
        violations.append(f"Duplicate record hash detected: '{rec_hash}' already exists in ledger.")

    # 3. Sequence number & ordering checks
    existing_records = tracker.operator_records.get(op_id, [])
    if existing_records:
        highest_seq = existing_records[-1]["sequence_number"]
        last_rec_hash = existing_records[-1]["record_hash"]

        if seq_num is not None and seq_num <= highest_seq:
            violations.append(
                f"Duplicate or regressive sequence number: received seq {seq_num}, "
                f"but operator '{op_id}' has already reached sequence {highest_seq}."
            )
        elif seq_num is not None and seq_num > highest_seq + 1:
            violations.append(
                f"Invalid ordering / sequence gap: received seq {seq_num}, "
                f"expected next sequence was {highest_seq + 1}."
            )

        # 4. Broken chain check
        if prev_hash and prev_hash != last_rec_hash:
            violations.append(
                f"Broken hash chain link: previous_record_hash '{prev_hash}' "
                f"does not match trailing record hash '{last_rec_hash}'."
            )
    else:
        # First record for this operator: should have genesis previous_hash "0"*64 and seq 1
        if seq_num is not None and seq_num != 1:
            violations.append(f"Invalid initial sequence number {seq_num}; expected 1 for initial record.")

    # 5. Stale timestamp check (allowed window +/- 300 seconds)
    if ts_str:
        try:
            record_time = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
            current_time = datetime.now(timezone.utc)
            drift = abs((current_time - record_time).total_seconds())
            if drift > 300:
                violations.append(
                    f"Stale or future timestamp: record timestamp '{ts_str}' deviates "
                    f"from current time by {drift:.1f}s (max tolerance: 300s)."
                )
        except Exception as e:
            violations.append(f"Malformed ISO-8601 timestamp: '{ts_str}'.")

    replay_detected = len(violations) > 0

    if replay_detected:
        status = f"REPLAY DETECTED: {len(violations)} VIOLATION(S)"
    else:
        status = "RECORD ACCEPTED: VALID PROVENANCE"

    # Log replay test event to ledger
    ledger_instance.append_block(
        artifact_type="REPLAY_DETECTION_TEST",
        artifact_hash=rec_hash or "UNKNOWN_HASH",
        metadata={
            "operator_id": op_id,
            "sequence_number": seq_num,
            "replay_detected": replay_detected,
            "violations_count": len(violations),
        },
    )

    return {
        "replay_detected": replay_detected,
        "status": status,
        "violations": violations,
        "record_summary": {
            "operator_id": op_id,
            "sequence_number": seq_num,
            "nonce": nonce,
            "record_hash": rec_hash,
            "timestamp": ts_str,
        },
    }
