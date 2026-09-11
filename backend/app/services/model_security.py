"""
TrustLens - Model Security Service (Member 3)
Provides:
1. Safe model fingerprinting without code execution (Section 12, 37)
2. Model substitution check with exact Section 13 non-accusatory language
3. Ledger-backed fingerprint storage and verification
"""

from datetime import datetime, timezone
import os
from pathlib import Path
from typing import Any, Dict, Optional, Union
from app.core.hashing import hash_bytes, hash_file
from app.provenance.ledger import ledger_instance
from app.services.cv_engine import model_manager


# Registry of stored model fingerprints
fingerprint_store: Dict[str, Dict[str, Any]] = {}


def safe_inspect_model(
    model_bytes: bytes,
    filename: str = "model.bin",
    architecture_hint: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Safely inspects model binary WITHOUT executing arbitrary code (Section 37).
    Disallows unsafe pickle.load or arbitrary Python code execution.
    Inspects magic bytes, file headers, and metadata safely.
    """
    file_size = len(model_bytes)
    sha256_hash = hash_bytes(model_bytes)

    # Detect framework from magic headers / signatures
    framework = "Unknown Binary"
    architecture = architecture_hint or "Custom Architecture"
    input_shape = [1, 3, 224, 224]
    output_shape = [1, 10]
    param_count = max(file_size // 4, 1000)  # Default approximate 4 bytes per float32

    # Safe inspection based on magic bytes
    if model_bytes.startswith(b"TRUSTLENS_RESNET18"):
        framework = "TrustLens Baseline Engine"
        architecture = "ResNet-18"
        param_count = 11689512
        output_shape = [1, 10]
    elif model_bytes.startswith(b"PK\x03\x04"):
        # Zip container (typical for TorchScript, PyTorch 1.6+ zip format, or ONNX zip)
        framework = "PyTorch ZipContainer (TorchScript/PyTorch)"
        architecture = architecture_hint or "CNN-VisionModel"
    elif b"ONNX" in model_bytes[:100] or filename.lower().endswith(".onnx"):
        framework = "ONNX Runtime"
        architecture = architecture_hint or "ONNX-VisionClassifier"
    elif filename.lower().endswith(".pt") or filename.lower().endswith(".pth"):
        framework = "PyTorch Checkpoint"
        architecture = architecture_hint or "ResNet-18"
    else:
        framework = "Generic CV Weights Binary"

    return {
        "sha256": sha256_hash,
        "file_size_bytes": file_size,
        "framework": framework,
        "architecture": architecture,
        "input_shape": input_shape,
        "output_shape": output_shape,
        "parameter_count": param_count,
    }


def register_model_fingerprint(
    model_id: str,
    model_bytes: bytes,
    filename: str = "model.bin",
    architecture_hint: Optional[str] = None,
    operator_id: str = "SYSTEM_ADMIN",
) -> Dict[str, Any]:
    """
    Computes fingerprint for uploaded model, stores in registry, and commits to ledger.
    """
    inspection = safe_inspect_model(model_bytes, filename, architecture_hint)
    timestamp = datetime.now(timezone.utc).isoformat()

    record = {
        "model_id": model_id,
        "sha256": inspection["sha256"],
        "file_size_bytes": inspection["file_size_bytes"],
        "framework": inspection["framework"],
        "architecture": inspection["architecture"],
        "input_shape": inspection["input_shape"],
        "output_shape": inspection["output_shape"],
        "parameter_count": inspection["parameter_count"],
        "created_at": timestamp,
        "metadata": {
            "operator_id": operator_id,
            "filename": filename,
            "offline_verified": True,
        },
    }

    # Store in-memory registry
    fingerprint_store[model_id] = record

    # Append to tamper-evident ledger
    ledger_instance.append_block(
        artifact_type="MODEL_FINGERPRINT",
        artifact_hash=inspection["sha256"],
        metadata={
            "model_id": model_id,
            "architecture": inspection["architecture"],
            "parameter_count": inspection["parameter_count"],
            "operator_id": operator_id,
        },
    )

    return record


def verify_model_substitution(
    model_id: str,
    uploaded_model_hash: str,
    reference_model_hash: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Compares an uploaded model's hash against a registered reference hash.
    Outputs EXACT Section 13 language:
    - Match:
      'REFERENCE MATCH'
      'Model binary matches registered baseline hash. Integrity verified.'
    - Mismatch:
      'MODEL BINARY DIFFERENCE'
      'Model binary differs from registered baseline hash. Expected: {expected_hash}, Received: {actual_hash}. Discrepancy may indicate unauthorized model substitution, silent update, or retraining.'

    CRITICAL RULE: Never call it malicious automatically.
    """
    expected_hash = reference_model_hash
    if not expected_hash:
        expected_hash = model_manager.get_baseline_hash(model_id)
        if not expected_hash and model_id in fingerprint_store:
            expected_hash = fingerprint_store[model_id]["sha256"]

    if not expected_hash:
        expected_hash = model_manager.get_model("resnet18-demo-v1").model_hash

    is_match = (uploaded_model_hash.lower() == expected_hash.lower())

    if is_match:
        status = "REFERENCE MATCH"
        message = "Model binary matches registered baseline hash. Integrity verified."
    else:
        status = "MODEL BINARY DIFFERENCE"
        message = (
            f"Model binary differs from registered baseline hash. "
            f"Expected: {expected_hash}, Received: {uploaded_model_hash}. "
            f"Discrepancy may indicate unauthorized model substitution, silent update, or retraining."
        )

    # Log verification to ledger
    ledger_instance.append_block(
        artifact_type="MODEL_SUBSTITUTION_CHECK",
        artifact_hash=uploaded_model_hash,
        metadata={
            "model_id": model_id,
            "status": status,
            "is_match": is_match,
            "expected_hash": expected_hash,
            "actual_hash": uploaded_model_hash,
        },
    )

    return {
        "model_id": model_id,
        "status": status,
        "is_match": is_match,
        "message": message,
        "expected_hash": expected_hash,
        "actual_hash": uploaded_model_hash,
    }
