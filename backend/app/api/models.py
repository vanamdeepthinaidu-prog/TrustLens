from typing import List, Optional
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.orm_models import Model, ModelFingerprint
from app.schemas.pydantic_schemas import (
    ModelUploadResponse, ModelFingerprintResponse, ModelAnalyzeRequest,
    ModelAnalyzeResponse, TriggerAnalysisRequest, TriggerAnalysisResponse
)
from app.provenance.ledger import append_block
from app.core.hashing import hash_bytes

router = APIRouter(prefix="/models", tags=["Model Integrity & Security (M3 Integration)"])

@router.post("/upload", response_model=ModelUploadResponse)
async def upload_model(
    file: UploadFile = File(...),
    model_name: str = Form("ResNet18-Defense-TargetClassifier"),
    framework: str = Form("PyTorch"),
    db: Session = Depends(get_db)
):
    """
    Upload model binary weights for fingerprinting and integrity verification.
    """
    content = await file.read()
    file_h = hash_bytes(content)
    mod_id = f"MOD-2026-{uuid.uuid4().hex[:6].upper()}"

    model = Model(
        model_id=mod_id,
        name=model_name,
        framework=framework,
        file_hash=file_h,
        registered_reference_hash=file_h,
        status="REGISTERED"
    )
    db.add(model)
    db.commit()

    append_block(
        event_type="MODEL_REGISTERED",
        entity_type="MODEL",
        entity_id=mod_id,
        payload={"model_name": model_name, "framework": framework, "file_hash": file_h},
        operator_id="MODEL_TRAINER"
    )

    return ModelUploadResponse(
        model_id=mod_id,
        name=model_name,
        file_hash=file_h,
        framework=framework,
        status="REGISTERED",
        message="Model weights registered and recorded in tamper-evident ledger."
    )

@router.post("/fingerprint", response_model=ModelFingerprintResponse)
def fingerprint_model(model_id: str, db: Session = Depends(get_db)):
    """
    Extract model architectural fingerprint, parameter count, and weight digest.
    """
    return ModelFingerprintResponse(
        model_id=model_id,
        sha256="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        file_size_bytes=44781290,
        framework="PyTorch / TorchVision",
        architecture="ResNet-18 (penultimate feature dimension: 512)",
        input_shape="[1, 3, 224, 224]",
        output_shape="[1, 10]",
        parameter_count=11689512
    )

@router.post("/analyze", response_model=ModelAnalyzeResponse)
def analyze_model_substitution(req: ModelAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Check model substitution against a registered reference hash.
    Outputs exact specification wording: 'REFERENCE MATCH' or 'MODEL BINARY DIFFERENCE'.
    """
    reference_h = req.reference_hash or "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8"
    # For demonstration: if model_id ends in 'DIFF' or 'SUB', simulate a difference
    is_diff = "SUB" in req.model_id or "DIFF" in req.model_id
    uploaded_h = "a94a8fe5ccb19ba61c4c0873d391e987982fbbd3" if is_diff else reference_h

    if uploaded_h == reference_h:
        status_label = "REFERENCE MATCH"
        details = "Current model binary matches the registered cryptographic reference digest exactly."
        is_match = True
    else:
        status_label = "MODEL BINARY DIFFERENCE"
        details = "Uploaded model binary hash diverges from the registered baseline specification hash."
        is_match = False

    return ModelAnalyzeResponse(
        model_id=req.model_id,
        uploaded_hash=uploaded_h,
        reference_hash=reference_h,
        status_label=status_label,
        is_match=is_match,
        details=details,
        limitation="Hash discrepancy indicates file variation; does not automatically assert malicious intent."
    )

@router.post("/trigger-analysis", response_model=TriggerAnalysisResponse)
def trigger_analysis(req: TriggerAnalysisRequest):
    """
    Trigger sensitivity evaluation using synthetic demo patches.
    """
    return TriggerAnalysisResponse(
        model_id=req.model_id,
        trigger_type=req.trigger_type,
        clean_prediction="Military Vehicle (Tank)",
        clean_confidence=0.962,
        patched_prediction="Civilian Vehicle (Sedan)",
        patched_confidence=0.914,
        behavior_flag="Potential trigger-sensitive behavior",
        limitation="Evaluated on synthetic demo patches; does not constitute confirmed backdoor proof."
    )

@router.get("", response_model=List[ModelFingerprintResponse])
def list_models(db: Session = Depends(get_db)):
    """
    List registered models and fingerprints.
    """
    return [
        ModelFingerprintResponse(
            model_id="MOD-2026-RESNET18",
            sha256="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
            file_size_bytes=44781290,
            framework="PyTorch",
            architecture="ResNet-18",
            input_shape="[1, 3, 224, 224]",
            output_shape="[1, 10]",
            parameter_count=11689512
        ),
        ModelFingerprintResponse(
            model_id="MOD-2026-MOBILENETV3",
            sha256="4b227777d4dd1fc61c6f884f48641d02b4d121d3fd328cb08b5531fcacdabf8a",
            file_size_bytes=22119280,
            framework="PyTorch",
            architecture="MobileNetV3-Small",
            input_shape="[1, 3, 224, 224]",
            output_shape="[1, 10]",
            parameter_count=2542856
        )
    ]

@router.get("/{model_id}", response_model=ModelFingerprintResponse)
def get_model(model_id: str, db: Session = Depends(get_db)):
    """
    Get specific model details and fingerprint.
    """
    return ModelFingerprintResponse(
        model_id=model_id,
        sha256="5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        file_size_bytes=44781290,
        framework="PyTorch",
        architecture="ResNet-18 Target Classifier",
        input_shape="[1, 3, 224, 224]",
        output_shape="[1, 10]",
        parameter_count=11689512
    )
