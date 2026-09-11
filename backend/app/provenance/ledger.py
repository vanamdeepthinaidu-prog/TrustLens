from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import secrets
from typing import Optional, List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.models.orm_models import AuditLog
from app.core.hashing import hash_bytes, hash_json

GENESIS_PREV_HASH = "0" * 64

@dataclass
class LedgerBlock:
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

    @property
    def index(self) -> int:
        return self.block_index

    @property
    def artifact_type(self) -> str:
        return self.event_type

    @property
    def artifact_hash(self) -> str:
        return self.payload_hash

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        return asdict(self)

    def dict(self, **kwargs) -> Dict[str, Any]:
        return asdict(self)

class VerificationResult(tuple):
    """
    Tuple supporting both tuple unpacking (is_valid, broken_idx, msg)
    and dict indexing res['is_valid'] for universal compatibility across M1-M4.
    """
    def __new__(cls, is_valid: bool, broken_block_index: Optional[int], message: str):
        return super().__new__(cls, (is_valid, broken_block_index, message))

    @property
    def is_valid(self) -> bool:
        return self[0]

    @property
    def broken_block_index(self) -> Optional[int]:
        return self[1]

    @property
    def message(self) -> str:
        return self[2]

    def __getitem__(self, item):
        if isinstance(item, str):
            if item == "is_valid":
                return self[0]
            elif item in ("broken_block_index", "broken_index"):
                return self[1]
            elif item in ("message", "verification_message"):
                return self[2]
            elif item == "status":
                return "CHAIN INTACT: ALL BLOCKS CRYPTOGRAPHICALLY VERIFIED" if self[0] else f"CHAIN TAMPERED AT BLOCK {self[1]}"
            elif item == "total_blocks":
                return len(get_ledger().get_all_blocks())
            raise KeyError(item)
        return super().__getitem__(item)

def compute_block_hash(
    block_index: int,
    timestamp: str,
    event_type: str,
    entity_type: str,
    entity_id: str,
    payload_hash: str,
    previous_hash: str,
    nonce: str,
    operator_id: str
) -> str:
    """
    Deterministic cryptographic hash over all immutable block fields.
    """
    canonical_header = f"{block_index}:{timestamp}:{event_type}:{entity_type}:{entity_id}:{payload_hash}:{previous_hash}:{nonce}:{operator_id}"
    return hash_bytes(canonical_header.encode("utf-8"))

class LedgerBackend(ABC):
    """
    Abstract ledger interface enabling modular persistence.
    Allows seamless swap from local SQLite to Hyperledger Fabric or other DLT.
    """
    @abstractmethod
    def append_block(
        self,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        operator_id: str = "SYSTEM",
        **kwargs
    ) -> LedgerBlock:
        pass

    @abstractmethod
    def verify_chain(self) -> Tuple[bool, Optional[int], str]:
        pass

    @abstractmethod
    def get_block(self, block_index: int) -> Optional[LedgerBlock]:
        pass

    @abstractmethod
    def get_all_blocks(self) -> List[LedgerBlock]:
        pass

    @abstractmethod
    def find_artifact(self, entity_id: str) -> List[LedgerBlock]:
        pass

    @abstractmethod
    def simulate_tampering(
        self,
        block_index: int,
        field_to_tamper: str = "payload",
        new_value: Any = None
    ) -> Dict[str, Any]:
        pass

class SQLiteLedgerBackend(LedgerBackend):
    """
    Default offline tamper-evident ledger persisted in SQLite audit_logs table.
    """
    def __init__(self, db_factory=SessionLocal):
        self.db_factory = db_factory
        try:
            Base.metadata.create_all(bind=engine)
        except Exception:
            pass
        self._ensure_genesis_block()

    def _ensure_genesis_block(self):
        with self.db_factory() as db:
            count = db.query(AuditLog).count()
            if count == 0:
                now_str = datetime.now(timezone.utc).isoformat()
                payload = {
                    "system": "VisionTrust AI",
                    "protocol": "AirGapped-Integrity-Chain-v1",
                    "description": "Genesis block initializing tamper-evident audit ledger"
                }
                payload_h = hash_json(payload)
                nonce = secrets.token_hex(16)
                genesis_hash = compute_block_hash(
                    block_index=0,
                    timestamp=now_str,
                    event_type="GENESIS",
                    entity_type="SYSTEM",
                    entity_id="VISIONTRUST-ROOT",
                    payload_hash=payload_h,
                    previous_hash=GENESIS_PREV_HASH,
                    nonce=nonce,
                    operator_id="INITIALIZER"
                )
                
                log = AuditLog(
                    block_index=0,
                    timestamp=now_str,
                    previous_hash=GENESIS_PREV_HASH,
                    block_hash=genesis_hash,
                    event_type="GENESIS",
                    entity_type="SYSTEM",
                    entity_id="VISIONTRUST-ROOT",
                    payload_hash=payload_h,
                    payload_json=json.dumps(payload, sort_keys=True),
                    nonce=nonce,
                    operator_id="INITIALIZER"
                )
                db.add(log)
                db.commit()

    @property
    def chain(self) -> List[LedgerBlock]:
        return self.get_all_blocks()

    def append_block(
        self,
        event_type: Optional[str] = None,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        payload: Optional[Dict[str, Any]] = None,
        operator_id: str = "SYSTEM",
        # compatibility parameters for M3 and M4
        artifact_type: Optional[str] = None,
        artifact_hash: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> LedgerBlock:
        # Handle positional: append_block("INFERENCE_RECORD", inf_hash, clean_inf_dict)
        if isinstance(entity_id, dict) and payload is None:
            p_load = entity_id
            en_id = str(entity_type)
            en_type = str(event_type)
            ev_type = str(event_type)
        else:
            ev_type = str(event_type or artifact_type or "GENERIC_EVENT")
            en_type = str(entity_type or artifact_type or "ARTIFACT")
            en_id = str(entity_id or artifact_hash or "ENTITY-001")
            p_load = payload if payload is not None else (metadata if metadata is not None else {})
        op_id = str(operator_id if operator_id != "SYSTEM" else kwargs.get("operator_id", "SYSTEM"))

        with self.db_factory() as db:
            last_block = db.query(AuditLog).order_by(AuditLog.block_index.desc()).first()
            if not last_block:
                self._ensure_genesis_block()
                last_block = db.query(AuditLog).order_by(AuditLog.block_index.desc()).first()

            new_index = last_block.block_index + 1
            prev_hash = last_block.block_hash
            now_str = datetime.now(timezone.utc).isoformat()
            payload_h = hash_json(p_load)
            nonce = secrets.token_hex(16)

            block_h = compute_block_hash(
                block_index=new_index,
                timestamp=now_str,
                event_type=ev_type,
                entity_type=en_type,
                entity_id=en_id,
                payload_hash=payload_h,
                previous_hash=prev_hash,
                nonce=nonce,
                operator_id=op_id
            )

            record = AuditLog(
                block_index=new_index,
                timestamp=now_str,
                previous_hash=prev_hash,
                block_hash=block_h,
                event_type=ev_type,
                entity_type=en_type,
                entity_id=en_id,
                payload_hash=payload_h,
                payload_json=json.dumps(p_load, sort_keys=True),
                nonce=nonce,
                operator_id=op_id
            )
            db.add(record)
            db.commit()
            db.refresh(record)

            return LedgerBlock(
                block_index=record.block_index,
                timestamp=record.timestamp,
                event_type=record.event_type,
                entity_type=record.entity_type,
                entity_id=record.entity_id,
                payload_hash=record.payload_hash,
                payload=p_load,
                previous_hash=record.previous_hash,
                nonce=record.nonce,
                operator_id=record.operator_id,
                block_hash=record.block_hash
            )

    def verify_chain(self) -> VerificationResult:
        with self.db_factory() as db:
            blocks = db.query(AuditLog).order_by(AuditLog.block_index.asc()).all()
            if not blocks:
                return VerificationResult(True, None, "Ledger is empty")

            # Check genesis block
            genesis = blocks[0]
            if genesis.block_index != 0 or genesis.previous_hash != GENESIS_PREV_HASH:
                return VerificationResult(False, 0, f"Genesis block corrupted: invalid previous_hash '{genesis.previous_hash}'")

            try:
                gen_payload = json.loads(genesis.payload_json)
            except Exception:
                return VerificationResult(False, 0, "Genesis block payload is not valid JSON")

            expected_gen_payload_h = hash_json(gen_payload)
            if genesis.payload_hash != expected_gen_payload_h:
                return VerificationResult(False, 0, f"Genesis block payload hash mismatch: stored '{genesis.payload_hash}' != calculated '{expected_gen_payload_h}'")

            expected_gen_block_h = compute_block_hash(
                0, genesis.timestamp, genesis.event_type, genesis.entity_type,
                genesis.entity_id, genesis.payload_hash, genesis.previous_hash,
                genesis.nonce, genesis.operator_id
            )
            if genesis.block_hash != expected_gen_block_h:
                return VerificationResult(False, 0, f"Genesis block hash mismatch: stored '{genesis.block_hash}' != calculated '{expected_gen_block_h}'")

            # Check chain sequentially
            for i in range(1, len(blocks)):
                curr = blocks[i]
                prev = blocks[i - 1]

                # 1. Link check
                if curr.previous_hash != prev.block_hash:
                    return VerificationResult(False, curr.block_index, (
                        f"Broken chain at block {curr.block_index}: previous_hash '{curr.previous_hash[:12]}...' "
                        f"does not match block {prev.block_index} block_hash '{prev.block_hash[:12]}...'"
                    ))

                # 2. Payload integrity
                try:
                    curr_payload = json.loads(curr.payload_json)
                except Exception:
                    return VerificationResult(False, curr.block_index, f"Block {curr.block_index} payload is corrupted")

                calc_payload_h = hash_json(curr_payload)
                if curr.payload_hash != calc_payload_h:
                    return VerificationResult(False, curr.block_index, (
                        f"Payload tampering detected at block {curr.block_index}: stored payload_hash '{curr.payload_hash[:12]}...' "
                        f"does not match calculated '{calc_payload_h[:12]}...'"
                    ))

                # 3. Block hash integrity
                calc_block_h = compute_block_hash(
                    curr.block_index, curr.timestamp, curr.event_type, curr.entity_type,
                    curr.entity_id, curr.payload_hash, curr.previous_hash,
                    curr.nonce, curr.operator_id
                )
                if curr.block_hash != calc_block_h:
                    return VerificationResult(False, curr.block_index, (
                        f"Block header tampering at block {curr.block_index}: stored block_hash '{curr.block_hash[:12]}...' "
                        f"does not match calculated '{calc_block_h[:12]}...'"
                    ))

            return VerificationResult(True, None, f"Audit chain verified successfully. All {len(blocks)} blocks cryptographically valid.")

    def get_block(self, block_index: int) -> Optional[LedgerBlock]:
        with self.db_factory() as db:
            rec = db.query(AuditLog).filter(AuditLog.block_index == block_index).first()
            if not rec:
                return None
            return LedgerBlock(
                block_index=rec.block_index,
                timestamp=rec.timestamp,
                event_type=rec.event_type,
                entity_type=rec.entity_type,
                entity_id=rec.entity_id,
                payload_hash=rec.payload_hash,
                payload=json.loads(rec.payload_json),
                previous_hash=rec.previous_hash,
                nonce=rec.nonce,
                operator_id=rec.operator_id,
                block_hash=rec.block_hash
            )

    def get_all_blocks(self) -> List[LedgerBlock]:
        with self.db_factory() as db:
            records = db.query(AuditLog).order_by(AuditLog.block_index.asc()).all()
            return [
                LedgerBlock(
                    block_index=r.block_index,
                    timestamp=r.timestamp,
                    event_type=r.event_type,
                    entity_type=r.entity_type,
                    entity_id=r.entity_id,
                    payload_hash=r.payload_hash,
                    payload=json.loads(r.payload_json),
                    previous_hash=r.previous_hash,
                    nonce=r.nonce,
                    operator_id=r.operator_id,
                    block_hash=r.block_hash
                )
                for r in records
            ]

    def find_artifact(self, entity_id: str) -> List[LedgerBlock]:
        with self.db_factory() as db:
            records = db.query(AuditLog).filter(AuditLog.entity_id == entity_id).order_by(AuditLog.block_index.asc()).all()
            return [
                LedgerBlock(
                    block_index=r.block_index,
                    timestamp=r.timestamp,
                    event_type=r.event_type,
                    entity_type=r.entity_type,
                    entity_id=r.entity_id,
                    payload_hash=r.payload_hash,
                    payload=json.loads(r.payload_json),
                    previous_hash=r.previous_hash,
                    nonce=r.nonce,
                    operator_id=r.operator_id,
                    block_hash=r.block_hash
                )
                for r in records
            ]

    def simulate_tampering(
        self,
        block_index: int,
        field_to_tamper: str = "payload",
        new_value: Any = None,
        modified_fields: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        with self.db_factory() as db:
            rec = db.query(AuditLog).filter(AuditLog.block_index == block_index).first()
            if not rec:
                raise ValueError(f"Block with index {block_index} does not exist in ledger")

            original_hash = rec.block_hash
            original_payload = rec.payload_json

            tampered_fields = []
            if modified_fields:
                for k, v in modified_fields.items():
                    tampered_fields.append(k)
                    if k in ("payload", "metadata"):
                        rec.payload_json = json.dumps(v)
                    elif k == "previous_hash":
                        rec.previous_hash = v or ("f" * 64)
                    elif k in ("block_hash", "hash"):
                        rec.block_hash = v or ("e" * 64)
                    elif k == "artifact_hash":
                        rec.entity_id = v
                        try:
                            p = json.loads(rec.payload_json)
                            if isinstance(p, dict):
                                p["artifact_hash"] = v
                                rec.payload_json = json.dumps(p)
                        except Exception:
                            pass
                    elif k == "artifact_type":
                        rec.event_type = v
                        rec.entity_type = v
                    elif hasattr(rec, k):
                        setattr(rec, k, v)
                    else:
                        try:
                            p = json.loads(rec.payload_json)
                            if isinstance(p, dict):
                                p[k] = v
                                rec.payload_json = json.dumps(p)
                        except Exception:
                            pass
            else:
                tampered_fields.append(field_to_tamper)
                if field_to_tamper == "payload":
                    tampered_payload = new_value if new_value is not None else {"ATTACK_FLAG": "MALICIOUS_UNAUTHORIZED_DATA"}
                    rec.payload_json = json.dumps(tampered_payload)
                elif field_to_tamper == "previous_hash":
                    rec.previous_hash = new_value or ("f" * 64)
                elif field_to_tamper == "block_hash":
                    rec.block_hash = new_value or ("e" * 64)
                elif hasattr(rec, field_to_tamper):
                    setattr(rec, field_to_tamper, new_value)

            final_tampered_payload = rec.payload_json
            db.commit()

        verification = self.verify_chain()

        return {
            "block_index": block_index,
            "tampered_fields": tampered_fields,
            "original_block_hash": original_hash,
            "original_payload": original_payload,
            "tampered_payload": final_tampered_payload,
            "verification_result": verification,
            "note": "Ledger entry was modified directly in persistence layer to test cryptographic detection."
        }

_ledger_instance: Optional[LedgerBackend] = None

def get_ledger() -> LedgerBackend:
    global _ledger_instance
    if _ledger_instance is None:
        _ledger_instance = SQLiteLedgerBackend()
    return _ledger_instance

def append_block(
    event_type: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    payload: Optional[Dict[str, Any]] = None,
    operator_id: str = "SYSTEM",
    **kwargs
) -> LedgerBlock:
    return get_ledger().append_block(
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        payload=payload,
        operator_id=operator_id,
        **kwargs
    )

def verify_chain() -> VerificationResult:
    return get_ledger().verify_chain()

def get_block(block_index: int) -> Optional[LedgerBlock]:
    return get_ledger().get_block(block_index)

def find_artifact(entity_id: str) -> List[LedgerBlock]:
    return get_ledger().find_artifact(entity_id)

def simulate_tampering(
    block_index: int,
    field_to_tamper: str = "payload",
    new_value: Any = None,
    modified_fields: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    return get_ledger().simulate_tampering(
        block_index=block_index,
        field_to_tamper=field_to_tamper,
        new_value=new_value,
        modified_fields=modified_fields,
    )

# Aliases for compatibility across M2, M3, and M4 modules
TamperEvidentLedger = SQLiteLedgerBackend
ledger_instance = get_ledger()
