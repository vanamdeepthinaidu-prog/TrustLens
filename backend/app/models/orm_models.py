from datetime import datetime, timezone
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey
)
from sqlalchemy.orm import relationship
from app.core.database import Base

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="DATA_CONTRIBUTOR")
    created_at = Column(DateTime, default=utc_now)

    actions = relationship("AnalystAction", back_populates="analyst")

class Contributor(Base):
    __tablename__ = "contributors"

    id = Column(Integer, primary_key=True, index=True)
    contributor_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)
    organization = Column(String(150), nullable=True)
    trust_score = Column(Float, default=100.0)
    total_contributions = Column(Integer, default=0)
    flagged_contributions = Column(Integer, default=0)
    risk_indicator = Column(String(50), default="LOW")
    created_at = Column(DateTime, default=utc_now)

    datasets = relationship("Dataset", back_populates="contributor")
    models = relationship("Model", back_populates="contributor")

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    contributor_id = Column(Integer, ForeignKey("contributors.id"), nullable=True)
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=False)
    sample_count = Column(Integer, default=0)
    dataset_type = Column(String(50), default="IMAGE_FOLDER")
    status = Column(String(50), default="UPLOADED")
    created_at = Column(DateTime, default=utc_now)

    contributor = relationship("Contributor", back_populates="datasets")
    samples = relationship("DatasetSample", back_populates="dataset", cascade="all, delete-orphan")

class DatasetSample(Base):
    __tablename__ = "dataset_samples"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_hash = Column(String(64), nullable=False)
    perceptual_hash = Column(String(64), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    aspect_ratio = Column(Float, nullable=True)
    brightness = Column(Float, nullable=True)
    contrast = Column(Float, nullable=True)
    blur_score = Column(Float, nullable=True)
    file_size_bytes = Column(Integer, nullable=True)
    format = Column(String(20), nullable=True)
    label = Column(String(100), nullable=True)
    is_corrupted = Column(Boolean, default=False)
    ood_score = Column(Float, nullable=True)
    duplicate_cluster_id = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=utc_now)

    dataset = relationship("Dataset", back_populates="samples")

class Model(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    contributor_id = Column(Integer, ForeignKey("contributors.id"), nullable=True)
    framework = Column(String(50), default="PyTorch")
    file_path = Column(String(500), nullable=True)
    file_hash = Column(String(64), nullable=False)
    registered_reference_hash = Column(String(64), nullable=True)
    is_substituted = Column(Boolean, default=False)
    status = Column(String(50), default="REGISTERED")
    created_at = Column(DateTime, default=utc_now)

    contributor = relationship("Contributor", back_populates="models")
    fingerprint = relationship("ModelFingerprint", uselist=False, back_populates="model", cascade="all, delete-orphan")
    inferences = relationship("InferenceRecord", back_populates="model")

class ModelFingerprint(Base):
    __tablename__ = "model_fingerprints"

    id = Column(Integer, primary_key=True, index=True)
    model_id = Column(Integer, ForeignKey("models.id"), unique=True, nullable=False)
    sha256 = Column(String(64), nullable=False)
    file_size_bytes = Column(Integer, nullable=False)
    framework = Column(String(50), nullable=False)
    architecture = Column(String(150), nullable=True)
    input_shape = Column(String(100), nullable=True)
    output_shape = Column(String(100), nullable=True)
    parameter_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    model = relationship("Model", back_populates="fingerprint")

class InferenceRecord(Base):
    __tablename__ = "inference_records"

    id = Column(Integer, primary_key=True, index=True)
    inference_uuid = Column(String(100), unique=True, index=True, nullable=False)
    input_hash = Column(String(64), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=True)
    model_identifier = Column(String(100), nullable=False)
    model_hash = Column(String(64), nullable=False)
    preprocessing_config = Column(Text, nullable=True)
    preprocessing_hash = Column(String(64), nullable=False)
    prediction_result = Column(Text, nullable=False)
    result_hash = Column(String(64), nullable=False)
    timestamp = Column(String(50), nullable=False)
    sequence_number = Column(Integer, nullable=False)
    nonce = Column(String(64), nullable=False)
    operator_id = Column(String(100), default="SYSTEM")
    previous_record_hash = Column(String(64), nullable=False)
    record_hash = Column(String(64), unique=True, index=True, nullable=False)
    is_tampered = Column(Boolean, default=False)
    is_replay = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)

    model = relationship("Model", back_populates="inferences")

class Anomaly(Base):
    __tablename__ = "anomalies"

    id = Column(Integer, primary_key=True, index=True)
    anomaly_id = Column(String(100), unique=True, index=True, nullable=False)
    asset_type = Column(String(50), nullable=False)  # DATASET, MODEL, INFERENCE, DISTRIBUTION
    asset_id = Column(String(100), nullable=False)
    finding_type = Column(String(100), nullable=False)
    what_happened = Column(Text, nullable=False)
    why_flagged = Column(Text, nullable=False)
    severity = Column(String(50), nullable=False)     # CRITICAL, HIGH, MEDIUM, LOW, INFO
    confidence = Column(Float, nullable=False)
    affected_asset = Column(String(200), nullable=False)
    recommended_action = Column(Text, nullable=False)
    limitations = Column(Text, nullable=False)
    evidence_data = Column(Text, nullable=True)
    disposition = Column(String(50), default="PENDING")
    created_at = Column(DateTime, default=utc_now)

class AttackSimulation(Base):
    __tablename__ = "attack_simulations"

    id = Column(Integer, primary_key=True, index=True)
    simulation_id = Column(String(100), unique=True, index=True, nullable=False)
    attack_type = Column(String(100), nullable=False)
    target_asset_type = Column(String(50), nullable=False)
    target_asset_id = Column(String(100), nullable=False)
    parameters = Column(Text, nullable=True)
    random_seed = Column(Integer, default=42)
    status = Column(String(50), default="COMPLETED")
    result_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    block_index = Column(Integer, unique=True, index=True, nullable=False)
    timestamp = Column(String(50), nullable=False)
    previous_hash = Column(String(64), nullable=False)
    block_hash = Column(String(64), unique=True, index=True, nullable=False)
    event_type = Column(String(100), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100), nullable=False)
    payload_hash = Column(String(64), nullable=False)
    payload_json = Column(Text, nullable=False)
    nonce = Column(String(64), nullable=False)
    operator_id = Column(String(100), default="SYSTEM")
    created_at = Column(DateTime, default=utc_now)

class AssuranceReport(Base):
    __tablename__ = "assurance_reports"

    id = Column(Integer, primary_key=True, index=True)
    report_uuid = Column(String(100), unique=True, index=True, nullable=False)
    overall_score = Column(Float, nullable=False)
    score_band = Column(String(50), nullable=False)  # CRITICAL, HIGH, MEDIUM, LOW, TRUSTED
    dataset_integrity_score = Column(Float, nullable=False)
    model_integrity_score = Column(Float, nullable=False)
    inference_integrity_score = Column(Float, nullable=False)
    distribution_stability_score = Column(Float, nullable=False)
    executive_summary = Column(Text, nullable=False)
    findings_summary = Column(Text, nullable=True)
    json_payload = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now)

class AnalystAction(Base):
    __tablename__ = "analyst_actions"

    id = Column(Integer, primary_key=True, index=True)
    asset_id = Column(String(100), nullable=False)
    asset_type = Column(String(50), nullable=False)
    analyst_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    analyst_name = Column(String(100), nullable=False)
    disposition = Column(String(50), nullable=False)  # ACCEPT, REVIEW, QUARANTINE
    justification = Column(Text, nullable=False)
    timestamp = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=utc_now)

    analyst = relationship("User", back_populates="actions")
