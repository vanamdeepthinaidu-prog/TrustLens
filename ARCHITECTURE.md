# VisionTrust AI — System Architecture & Modular Ledger Design

## 1. High-Level Architecture Overview

VisionTrust AI is organized as a decoupled, multi-tier assurance platform operating completely offline in defense/air-gapped environments:

```
                            ┌──────────────────────────────────────┐
                            │    React Security Console (M5)       │
                            │ (SOC Dark Theme / Pipeline Visual)   │
                            └──────────────────┬───────────────────┘
                                               │ REST (Port 8000)
    ┌──────────────────────────────────────────┴──────────────────────────────────────────┐
    │                               FastAPI Application Gateway (M1)                     │
    ├───────────────────┬───────────────────┬────────────────────┬────────────────────────┤
    │   Dataset Layer   │    Model Layer    │  Inference Layer   │  Distribution Shift    │
    │   Integrity (M2)  │   Security (M3)   │  Provenance (M3)   │   & Attack Sim (M4)    │
    └─────────┬─────────┴─────────┬─────────┴──────────┬─────────┴───────────┬────────────┘
              │                   │                    │                     │
              ▼                   ▼                    ▼                     ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                       Deterministic Hashing Service (M1 Core)                       │
    │            SHA-256 File Chunks | Canonical JSON | Directory Merkle Manifest         │
    └──────────────────────────────────────────┬──────────────────────────────────────────┘
                                               │
                                               ▼
    ┌─────────────────────────────────────────────────────────────────────────────────────┐
    │                   Tamper-Evident Hash Chain Audit Ledger (M1)                       │
    │          Abstract Interface: LedgerBackend (SQLite Default ──> Hyperledger Fabric)  │
    └─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Tamper-Evident Ledger Design

The ledger records immutable pipeline lifecycle events (`DATASET_REGISTERED`, `MODEL_FINGERPRINTED`, `INFERENCE_COMMITTED`, `ANOMALY_LOGGED`, `DISPOSITION_RECORDED`).

### Block Schema
Each block contains:
- `index`: Monotonically increasing integer (0 = Genesis).
- `timestamp`: UTC ISO-8601 formatted timestamp.
- `event_type`: Lifecycle action identifier.
- `entity_type`: Target entity class (`DATASET`, `MODEL`, `INFERENCE`, `SYSTEM`).
- `entity_id`: Identifier of the artifact.
- `payload_hash`: Cryptographic SHA-256 of canonicalized JSON payload.
- `payload`: Structured event payload.
- `previous_hash`: SHA-256 hash of previous block in the chain (`0000...` for genesis).
- `nonce`: Cryptographic nonce ensuring block uniqueness.
- `operator_id`: Identity of submitting user/operator.
- `block_hash`: Cryptographic hash over all fields:
  ```
  block_hash = SHA256(index + timestamp + event_type + entity_type + entity_id + payload_hash + previous_hash + nonce + operator_id)
  ```

### Chain Verification & Tamper Detection
- When `verify_chain()` executes, it traverses from block 0 to the latest block.
- For each block \(i > 0\), it asserts `block[i].previous_hash == block[i-1].block_hash`.
- It recomputes `block_hash` from contents and verifies equality.
- If any byte in block data or payload is modified, the hash calculation fails immediately, flagging the exact block index and field discrepancy.

---

## 3. Modular DLT Design: Hyperledger Fabric Migration

VisionTrust AI decouples business logic from persistence using the `LedgerBackend` abstract base class:

```python
class LedgerBackend(ABC):
    @abstractmethod
    def append_block(self, event_type: str, entity_type: str, entity_id: str, payload: dict, operator_id: str) -> LedgerBlock:
        pass

    @abstractmethod
    def verify_chain(self) -> tuple[bool, int | None, str]:
        pass

    @abstractmethod
    def get_block(self, block_index: int) -> LedgerBlock | None:
        pass

    @abstractmethod
    def get_all_blocks(self) -> list[LedgerBlock]:
        pass

    @abstractmethod
    def find_artifact(self, entity_id: str) -> list[LedgerBlock]:
        pass
```

### Current Implementation: `SQLiteLedgerBackend`
- For offline air-gapped demo execution without complex infrastructure overhead, the default backend persists blocks directly to the SQLite `audit_logs` table.
- Cryptographic hash chaining ensures tamper-evident detection without external services.

### Enterprise Adaptation: `HyperledgerFabricBackend`
For multi-organization defense consortia (e.g. Army, Ordnance, R&D Labs):
1. **Smart Contracts (Chaincode):** The `append_block` and `verify_chain` methods map directly to Fabric chaincode invocations (`SubmitTransaction('RecordAuditBlock', ...)`).
2. **Consensus & Multi-Party Endorsement:** Fabric peer endorsement policies enforce that a minimum threshold of contributors sign off on dataset/model provenance before a block is committed.
3. **Zero Code Changes to Upstream Services:** Route handlers in `app/api/audit.py`, `app/api/inference.py`, and `app/api/datasets.py` interact strictly with `get_ledger()`, leaving pipeline code completely agnostic of whether SQLite or Hyperledger Fabric is running underneath.
