from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

# ---------------------------------------------------------------------------
# Auth & User Schemas
# ---------------------------------------------------------------------------

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "DATA_CONTRIBUTOR"
    organization: Optional[str] = None
    name: Optional[str] = None

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    username: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    created_at: Optional[datetime] = None

class ContributorCreate(BaseModel):
    contributor_id: str
    name: str
    role: str
    organization: Optional[str] = None

class ContributorResponse(BaseModel):
    id: int
    contributor_id: str
    name: str
    role: str
    organization: Optional[str] = None
    trust_score: float
    total_contributions: int
    flagged_contributions: int
    risk_indicator: str

# ---------------------------------------------------------------------------
# Dataset Schemas (M2 Integration)
# ---------------------------------------------------------------------------

class DatasetUploadResponse(BaseModel):
    dataset_id: str
    name: str
    file_hash: str
    sample_count: int
    status: str
    message: str

class DatasetAnalyzeRequest(BaseModel):
    dataset_id: str
    run_ood: bool = True
    run_duplicates: bool = True
    run_label_consistency: bool = True

class DuplicateCluster(BaseModel):
    cluster_id: str
    similarity_percentage: float
    finding_text: str = "Potential duplicate flooding indicator"
    file_hashes: List[str]

class OODFinding(BaseModel):
    sample_id: str
    ood_score: float
    severity: str
    limitation_note: str

class DatasetAnalyzeResponse(BaseModel):
    dataset_id: str
    total_samples: int
    corrupted_count: int
    exact_duplicates_count: int
    near_duplicates_count: int
    duplicate_clusters: List[DuplicateCluster]
    ood_flagged_count: int
    label_inconsistencies_count: int
    dataset_integrity_score: float
    status: str

class DatasetDetailResponse(BaseModel):
    id: int
    dataset_id: str
    name: str
    file_hash: str
    sample_count: int
    status: str
    contributor_name: Optional[str] = None
    created_at: Optional[datetime] = None

# ---------------------------------------------------------------------------
# Model Schemas (M3 Integration)
# ---------------------------------------------------------------------------

class ModelUploadResponse(BaseModel):
    model_id: str
    name: str
    file_hash: str
    framework: str
    status: str
    message: str

class ModelFingerprintResponse(BaseModel):
    model_id: str
    sha256: str
    file_size_bytes: int
    framework: str
    architecture: Optional[str] = None
    input_shape: Optional[str] = None
    output_shape: Optional[str] = None
    parameter_count: Optional[int] = None

class ModelAnalyzeRequest(BaseModel):
    model_id: str
    reference_hash: Optional[str] = None

class ModelAnalyzeResponse(BaseModel):
    model_id: str
    uploaded_hash: str
    reference_hash: str
    status_label: str  # "REFERENCE MATCH" or "MODEL BINARY DIFFERENCE"
    is_match: bool
    details: str
    limitation: str = "Hash discrepancy indicates file variation; does not automatically assert malicious intent."

class TriggerAnalysisRequest(BaseModel):
    model_id: str
    demo_image_id: Optional[str] = "demo_tank_01.jpg"
    trigger_type: str = "corner_square"  # square, corner_square, stripe

class TriggerAnalysisResponse(BaseModel):
    model_id: str
    trigger_type: str
    clean_prediction: str
    clean_confidence: float
    patched_prediction: str
    patched_confidence: float
    behavior_flag: str = "Potential trigger-sensitive behavior"
    limitation: str = "Evaluated on synthetic demo patches; does not constitute confirmed backdoor proof."

# ---------------------------------------------------------------------------
# Inference & Provenance Schemas (M3 Integration)
# ---------------------------------------------------------------------------

class PreprocessingConfig(BaseModel):
    resize: List[int] = [224, 224]
    normalize_mean: List[float] = [0.485, 0.456, 0.406]
    normalize_std: List[float] = [0.229, 0.224, 0.225]

class InferenceRunRequest(BaseModel):
    image_name: str
    model_id: str
    preprocessing: Optional[PreprocessingConfig] = None
    operator_id: Optional[str] = "OPERATOR-ALPHA"

class InferenceRunResponse(BaseModel):
    inference_id: str
    prediction: str
    confidence: float
    input_hash: str
    model_id: str
    model_hash: str
    preprocessing_hash: str
    result_hash: str
    timestamp: str
    sequence_number: int
    nonce: str
    previous_record_hash: str
    record_hash: str

class InferenceVerifyRequest(BaseModel):
    inference_id: str

class InferenceVerifyResponse(BaseModel):
    inference_id: str
    status: str  # "VERIFIED" or "TAMPER DETECTED"
    recomputed_record_hash: str
    stored_record_hash: str
    is_valid: bool
    evidence: Dict[str, Any]

class InferenceTamperTestRequest(BaseModel):
    inference_id: str
    tamper_field: str = "prediction_result"  # prediction_result, model_hash, input_hash
    new_value: str = "TAMPERED_CLASS"

class InferenceTamperTestResponse(BaseModel):
    inference_id: str
    status: str = "TAMPER DETECTED"
    original_hash: str
    current_hash: str
    tampered_field: str
    original_value: Any
    tampered_value: Any
    explanation: str

class InferenceReplayTestRequest(BaseModel):
    sequence_number: int
    nonce: str
    timestamp: str
    record_hash: str

class InferenceReplayTestResponse(BaseModel):
    status: str  # "REPLAY DETECTED" or "SEQUENCE VALID"
    reasons: List[str]
    is_replay: bool

# ---------------------------------------------------------------------------
# Distribution Shift Schemas (M4 Integration)
# ---------------------------------------------------------------------------

class DistributionAnalyzeRequest(BaseModel):
    reference_dataset_id: str
    current_dataset_id: str

class DistributionAnalyzeResponse(BaseModel):
    reference_dataset_id: str
    current_dataset_id: str
    shift_score: float  # 0.0 to 1.0
    cosine_distance: float
    wasserstein_distance: float
    brightness_shift: float
    contrast_shift: float
    interpretation: str
    limitation: str = "Distribution shifts reflect domain and environmental changes; not necessarily adversarial."

# ---------------------------------------------------------------------------
# Security Lab / Attack Simulator Schemas (M4 Integration)
# ---------------------------------------------------------------------------

class SimulatorCreateRequest(BaseModel):
    attack_type: str  # label_flip, duplicate_flooding, ood_injection, image_corruption, metadata_manipulation, model_substitution, trigger_injection, inference_tampering, replay_attack
    target_asset_id: str
    intensity: float = 0.5
    random_seed: int = 42

class SimulatorCreateResponse(BaseModel):
    simulation_id: str
    attack_type: str
    target_asset_id: str
    status: str
    summary: str
    isolated_copy_path: str

class SimulationRunResponse(BaseModel):
    simulation_id: str
    attack_type: str
    target_asset_id: str
    status: str
    result_summary: Optional[str] = None
    created_at: Optional[str] = None

class DemoRunCompleteResponse(BaseModel):
    run_id: str
    status: str
    current_step: int
    total_steps: int = 18
    message: str

class DemoStatusResponse(BaseModel):
    run_id: str
    current_step: int
    total_steps: int
    step_title: str
    progress_percentage: float
    completed: bool
    logs: List[str]

# ---------------------------------------------------------------------------
# Trust & Assurance Engine Schemas (M4 Integration)
# ---------------------------------------------------------------------------

class ComponentScore(BaseModel):
    name: str
    weight_percentage: float
    raw_score: float
    weighted_score: float
    status: str

class AssuranceRunResponse(BaseModel):
    report_uuid: str
    overall_trust_score: float
    score_band: str  # CRITICAL, HIGH, MEDIUM, LOW, TRUSTED
    disposition: str  # ACCEPT, REVIEW, QUARANTINE
    components: Dict[str, ComponentScore]
    executive_summary: str
    findings_count: int
    timestamp: str

# ---------------------------------------------------------------------------
# Audit Trail & Ledger Schemas (M1 Core)
# ---------------------------------------------------------------------------

class LedgerBlockSchema(BaseModel):
    block_index: int
    timestamp: str
    event_type: str
    entity_type: str
    entity_id: str
    payload_hash: str
    payload: Dict[str, Any]
    previous_hash: str
    nonce: str
    operator_id: str
    block_hash: str

class AuditVerifyResponse(BaseModel):
    chain_status: str  # "VERIFIED" or "TAMPER DETECTED"
    total_blocks: int
    is_valid: bool
    broken_block_index: Optional[int] = None
    verification_message: str

class AuditTamperSimulateRequest(BaseModel):
    block_index: int
    field_to_tamper: str = "payload"
    tampered_value: Dict[str, Any] = {"unauthorized_change": True}

class AuditTamperSimulateResponse(BaseModel):
    block_index: int
    status: str
    original_block_hash: str
    new_invalid_hash: str
    message: str

# ---------------------------------------------------------------------------
# Disposition & Evidence Explorer Schemas (M4 Integration)
# ---------------------------------------------------------------------------

class DispositionRequest(BaseModel):
    disposition: str  # ACCEPT, REVIEW, QUARANTINE
    justification: str
    analyst_name: Optional[str] = "Lead Security Analyst"

class DispositionResponse(BaseModel):
    asset_id: str
    disposition: str
    analyst_name: str
    recorded_at: str
    ledger_block_index: int

class EvidenceItem(BaseModel):
    finding_id: str
    finding_type: str
    what_happened: str
    why_flagged: str
    severity: str
    confidence: float
    affected_asset: str
    recommended_action: str
    limitations: str
    disposition: str
    timestamp: str

# ---------------------------------------------------------------------------
# System Status Schemas (M1 Core)
# ---------------------------------------------------------------------------

class SystemStatusResponse(BaseModel):
    status: str
    offline_mode: bool
    air_gapped_ready: bool
    version: str
    active_ledger_blocks: int
    registered_datasets: int
    registered_models: int
    inference_records_count: int
    detected_anomalies_count: int
    hardware_info: Dict[str, Any]
