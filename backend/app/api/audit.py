from typing import List
from fastapi import APIRouter, HTTPException
from app.provenance.ledger import (
    get_ledger, verify_chain, simulate_tampering, LedgerBlock
)
from app.schemas.pydantic_schemas import (
    LedgerBlockSchema, AuditVerifyResponse, AuditTamperSimulateRequest,
    AuditTamperSimulateResponse
)

router = APIRouter(prefix="/audit", tags=["Tamper-Evident Ledger & Audit Trail (M1 Core)"])

@router.get("", response_model=List[LedgerBlockSchema])
def get_audit_trail():
    """
    Retrieve full chronological tamper-evident ledger history with cryptographic block hashes.
    """
    blocks = get_ledger().get_all_blocks()
    return [
        LedgerBlockSchema(
            block_index=b.block_index,
            timestamp=b.timestamp,
            event_type=b.event_type,
            entity_type=b.entity_type,
            entity_id=b.entity_id,
            payload_hash=b.payload_hash,
            payload=b.payload,
            previous_hash=b.previous_hash,
            nonce=b.nonce,
            operator_id=b.operator_id,
            block_hash=b.block_hash
        )
        for b in blocks
    ]

@router.post("/verify", response_model=AuditVerifyResponse)
def verify_audit_chain():
    """
    Cryptographically verify the entire block hash chain from Genesis to tip.
    Asserts previous_hash continuity, payload hashes, and block headers.
    """
    is_valid, broken_idx, msg = verify_chain()
    blocks = get_ledger().get_all_blocks()

    return AuditVerifyResponse(
        chain_status="VERIFIED" if is_valid else "TAMPER DETECTED",
        total_blocks=len(blocks),
        is_valid=is_valid,
        broken_block_index=broken_idx,
        verification_message=msg
    )

@router.post("/tamper-simulate", response_model=AuditTamperSimulateResponse)
def tamper_simulation(req: AuditTamperSimulateRequest):
    """
    Simulate intentional tampering of an existing block in the ledger.
    Used for live hackathon demo to demonstrate instant detection by verify_chain().
    """
    try:
        res = simulate_tampering(
            block_index=req.block_index,
            field_to_tamper=req.field_to_tamper,
            new_value=req.tampered_value
        )
        return AuditTamperSimulateResponse(
            block_index=req.block_index,
            status="TAMPERING_INJECTED",
            original_block_hash=res["original_block_hash"],
            new_invalid_hash="INVALIDATED_DUE_TO_MODIFIED_PAYLOAD",
            message=f"Block {req.block_index} {req.field_to_tamper} mutated directly in database. Subsequent calls to /api/audit/verify will flag this block."
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
