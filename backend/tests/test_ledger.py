import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.provenance.ledger import SQLiteLedgerBackend, GENESIS_PREV_HASH

@pytest.fixture
def isolated_ledger():
    """
    Creates an isolated in-memory SQLite database for ledger test execution.
    """
    test_engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=test_engine)
    test_session_factory = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    ledger = SQLiteLedgerBackend(db_factory=test_session_factory)
    return ledger

def test_genesis_block(isolated_ledger):
    blocks = isolated_ledger.get_all_blocks()
    assert len(blocks) == 1
    genesis = blocks[0]
    assert genesis.block_index == 0
    assert genesis.event_type == "GENESIS"
    assert genesis.previous_hash == GENESIS_PREV_HASH
    assert len(genesis.block_hash) == 64

    is_valid, broken_idx, msg = isolated_ledger.verify_chain()
    assert is_valid is True
    assert broken_idx is None

def test_append_and_verify_chain(isolated_ledger):
    # Append multiple blocks
    b1 = isolated_ledger.append_block(
        event_type="DATASET_REGISTERED",
        entity_type="DATASET",
        entity_id="DS-001",
        payload={"name": "Recon 1", "sample_count": 100},
        operator_id="DATA_CONTRIBUTOR"
    )
    assert b1.block_index == 1
    assert b1.previous_hash == isolated_ledger.get_block(0).block_hash

    b2 = isolated_ledger.append_block(
        event_type="MODEL_REGISTERED",
        entity_type="MODEL",
        entity_id="MOD-001",
        payload={"model_name": "ResNet-18", "framework": "PyTorch"},
        operator_id="MODEL_TRAINER"
    )
    assert b2.block_index == 2
    assert b2.previous_hash == b1.block_hash

    is_valid, broken_idx, msg = isolated_ledger.verify_chain()
    assert is_valid is True
    assert broken_idx is None
    assert "verified successfully" in msg.lower()

def test_tamper_detection_in_payload(isolated_ledger):
    isolated_ledger.append_block("EVENT_1", "TYPE_A", "ID_1", {"key": "val1"})
    isolated_ledger.append_block("EVENT_2", "TYPE_B", "ID_2", {"key": "val2"})
    isolated_ledger.append_block("EVENT_3", "TYPE_C", "ID_3", {"key": "val3"})

    # Verify initial valid state
    is_valid, _, _ = isolated_ledger.verify_chain()
    assert is_valid is True

    # Tamper with block 2 payload
    isolated_ledger.simulate_tampering(
        block_index=2,
        field_to_tamper="payload",
        new_value={"MALICIOUS_INJECTION": "TAMPERED_CONTENT"}
    )

    # Chain verification MUST fail and pinpoint block 2!
    is_valid, broken_idx, msg = isolated_ledger.verify_chain()
    assert is_valid is False
    assert broken_idx == 2
    assert "tampering detected" in msg.lower()

def test_tamper_detection_in_previous_hash(isolated_ledger):
    isolated_ledger.append_block("EVENT_1", "TYPE_A", "ID_1", {"key": "val1"})
    isolated_ledger.append_block("EVENT_2", "TYPE_B", "ID_2", {"key": "val2"})

    # Break hash-chain link in block 2
    isolated_ledger.simulate_tampering(
        block_index=2,
        field_to_tamper="previous_hash",
        new_value="0" * 64
    )

    is_valid, broken_idx, msg = isolated_ledger.verify_chain()
    assert is_valid is False
    assert broken_idx == 2
    assert "broken chain" in msg.lower()

def test_find_artifact(isolated_ledger):
    isolated_ledger.append_block("EVENT_1", "MODEL", "MOD-XYZ", {"step": 1})
    isolated_ledger.append_block("EVENT_2", "DATASET", "DS-ABC", {"step": 1})
    isolated_ledger.append_block("EVENT_3", "MODEL", "MOD-XYZ", {"step": 2})

    matches = isolated_ledger.find_artifact("MOD-XYZ")
    assert len(matches) == 2
    assert matches[0].payload["step"] == 1
    assert matches[1].payload["step"] == 2
