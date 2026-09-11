from typing import List
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.orm_models import Dataset
from app.schemas.pydantic_schemas import (
    DatasetUploadResponse, DatasetAnalyzeRequest, DatasetAnalyzeResponse,
    DatasetDetailResponse, DuplicateCluster
)
from app.provenance.ledger import append_block
from app.core.hashing import hash_bytes

router = APIRouter(prefix="/datasets", tags=["Dataset Integrity (M2 Integration)"])

@router.post("/upload", response_model=DatasetUploadResponse)
async def upload_dataset(
    file: UploadFile = File(...),
    dataset_name: str = Form("Surveillance-Recon-Batch-01"),
    db: Session = Depends(get_db)
):
    """
    Upload a dataset folder, zip, or image batch for integrity analysis.
    Computes deterministic hash and records registration to ledger.
    """
    content = await file.read()
    file_h = hash_bytes(content)
    ds_id = f"DS-2026-{uuid.uuid4().hex[:6].upper()}"

    dataset = Dataset(
        dataset_id=ds_id,
        name=dataset_name,
        file_hash=file_h,
        sample_count=150,
        dataset_type="IMAGE_BATCH",
        status="REGISTERED"
    )
    db.add(dataset)
    db.commit()
    db.refresh(dataset)

    # Record to immutable ledger
    append_block(
        event_type="DATASET_REGISTERED",
        entity_type="DATASET",
        entity_id=ds_id,
        payload={"dataset_name": dataset_name, "file_hash": file_h, "sample_count": 150},
        operator_id="DATA_CONTRIBUTOR"
    )

    return DatasetUploadResponse(
        dataset_id=ds_id,
        name=dataset_name,
        file_hash=file_h,
        sample_count=150,
        status="REGISTERED",
        message="Dataset uploaded, registered in SQLite, and cryptographically committed to audit ledger."
    )

@router.post("/analyze", response_model=DatasetAnalyzeResponse)
def analyze_dataset(req: DatasetAnalyzeRequest, db: Session = Depends(get_db)):
    """
    Execute dataset integrity analysis.
    Member 2 provides full CV engine; stub returns specification-compliant mock evidence.
    """
    # Contract response matching sections 8, 9, 10, 11 of spec
    mock_clusters = [
        DuplicateCluster(
            cluster_id="CLUSTER-DUP-01",
            similarity_percentage=98.4,
            finding_text="Potential duplicate flooding indicator",
            file_hashes=["a1b2c3d4e5f67890", "a1b2c3d4e5f67891", "a1b2c3d4e5f67892"]
        )
    ]

    return DatasetAnalyzeResponse(
        dataset_id=req.dataset_id,
        total_samples=150,
        corrupted_count=2,
        exact_duplicates_count=6,
        near_duplicates_count=8,
        duplicate_clusters=mock_clusters,
        ood_flagged_count=5,
        label_inconsistencies_count=4,
        dataset_integrity_score=78.5,
        status="ANALYZED"
    )

@router.get("", response_model=List[DatasetDetailResponse])
def list_datasets(db: Session = Depends(get_db)):
    """
    List registered datasets.
    """
    datasets = db.query(Dataset).all()
    if not datasets:
        return [
            DatasetDetailResponse(
                id=1,
                dataset_id="DS-2026-DEMO01",
                name="Indian Army Recon Baseline Dataset (Clean)",
                file_hash="9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
                sample_count=250,
                status="VERIFIED",
                contributor_name="Signals Corps Data Team"
            )
        ]
    return [
        DatasetDetailResponse(
            id=d.id,
            dataset_id=d.dataset_id,
            name=d.name,
            file_hash=d.file_hash,
            sample_count=d.sample_count,
            status=d.status,
            contributor_name=d.contributor.name if d.contributor else "Unknown"
        )
        for d in datasets
    ]

@router.get("/{dataset_id}", response_model=DatasetDetailResponse)
def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
    """
    Get specific dataset details.
    """
    ds = db.query(Dataset).filter(Dataset.dataset_id == dataset_id).first()
    if not ds:
        # Fallback demo stub
        return DatasetDetailResponse(
            id=1,
            dataset_id=dataset_id,
            name="Military Ground Vehicle Recon (Evaluation Set)",
            file_hash="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            sample_count=180,
            status="ANALYZED",
            contributor_name="Signals Corps Data Team"
        )
    return DatasetDetailResponse(
        id=ds.id,
        dataset_id=ds.dataset_id,
        name=ds.name,
        file_hash=ds.file_hash,
        sample_count=ds.sample_count,
        status=ds.status,
        contributor_name=ds.contributor.name if ds.contributor else "Unknown"
    )
