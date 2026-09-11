"""
TrustLens - Pydantic Schemas for Model & Inference Security (Member 3)
Defines schemas for:
- Model fingerprinting
- Model substitution check
- Inference run & response
- Canonical cryptographic provenance records
- Tamper detection test
- Replay detection test
- Trigger-sensitivity demo
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# -------------------------------------------------------------
# 1. Model Fingerprinting Schemas (Section 12)
# -------------------------------------------------------------
class ModelFingerprintRecord(BaseModel):
    model_id: str
    sha256: str
    file_size_bytes: int
    framework: str
    architecture: str
    input_shape: List[int]
    output_shape: List[int]
    parameter_count: int
    created_at: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


# -------------------------------------------------------------
# 2. Model Substitution Check Schemas (Section 13)
# -------------------------------------------------------------
class ModelSubstitutionCheckRequest(BaseModel):
    model_id: str
    uploaded_model_hash: str
    reference_model_hash: Optional[str] = None


class ModelSubstitutionCheckResponse(BaseModel):
    model_id: str
    status: str  # "REFERENCE MATCH" or "MODEL BINARY DIFFERENCE"
    is_match: bool
    message: str
    expected_hash: str
    actual_hash: str


# -------------------------------------------------------------
# 3. Preprocessing & Provenance Binding Schemas (Section 14 & 15)
# -------------------------------------------------------------
class PreprocessingConfig(BaseModel):
    resize: List[int] = Field(default=[224, 224])
    normalize_mean: List[float] = Field(default=[0.485, 0.456, 0.406])
    normalize_std: List[float] = Field(default=[0.229, 0.224, 0.225])
    color_mode: str = Field(default="RGB")


class InferenceProvenanceRecord(BaseModel):
    sequence_number: int
    nonce: str
    timestamp: str
    operator_id: str
    model_id: str
    model_hash: str
    input_hash: str
    preprocessing_hash: str
    result_hash: str
    previous_record_hash: str
    record_hash: str


class InferenceRunRequest(BaseModel):
    model_id: str = "resnet18-demo-v1"
    operator_id: str = "OP-8492"
    preprocessing_config: Optional[Dict[str, Any]] = None
    image_base64: Optional[str] = None
    demo_image_name: Optional[str] = None
    is_demo: bool = True


class InferenceRunResponse(BaseModel):
    inference_id: str
    model_id: str
    model_hash: str
    input_hash: str
    preprocessing_hash: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    timestamp: str
    provenance_record: InferenceProvenanceRecord


# -------------------------------------------------------------
# 4. Tamper Detection Schemas (Section 16)
# -------------------------------------------------------------
class TamperFieldDiff(BaseModel):
    field: str
    original_value: Any
    modified_value: Any


class TamperTestRequest(BaseModel):
    record_hash: Optional[str] = None
    demo_record: Optional[Dict[str, Any]] = None
    modified_fields: Dict[str, Any]


class TamperTestResponse(BaseModel):
    tamper_detected: bool
    status: str
    original_hash: str
    current_hash: str
    modified_fields: List[TamperFieldDiff]
    explanation: str


# -------------------------------------------------------------
# 5. Replay Detection Schemas (Section 17)
# -------------------------------------------------------------
class ReplayTestRequest(BaseModel):
    provenance_record: Dict[str, Any]


class ReplayTestResponse(BaseModel):
    replay_detected: bool
    status: str
    violations: List[str]
    record_summary: Dict[str, Any]


# -------------------------------------------------------------
# 6. Trigger-Sensitivity Schemas (Section 18)
# -------------------------------------------------------------
class TriggerSensitivityRequest(BaseModel):
    model_id: str = "resnet18-demo-v1"
    patch_type: str = Field(default="square", description="square, corner_square, or stripe")
    patch_size: int = Field(default=32, ge=8, le=100)
    patch_color: List[int] = Field(default=[255, 0, 0])
    demo_image_name: Optional[str] = None
    image_base64: Optional[str] = None


class TriggerSensitivityResponse(BaseModel):
    status: str
    potential_trigger_sensitive: bool
    baseline_prediction: str
    baseline_confidence: float
    triggered_prediction: str
    triggered_confidence: float
    delta_confidence: float
    prediction_flipped: bool
    patch_type: str
    patch_coordinates: Dict[str, int]
    finding: str
    limitations: str
