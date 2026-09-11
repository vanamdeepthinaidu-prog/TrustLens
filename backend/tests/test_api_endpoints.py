import pytest
from fastapi.testclient import TestClient
from app.main import app

@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c

def test_system_status_endpoint(client):
    res = client.get("/api/system/status")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "OPERATIONAL"
    assert data["offline_mode"] is True
    assert data["air_gapped_ready"] is True

def test_auth_login_seeded(client):
    res = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["role"] == "ADMIN"

def test_audit_verify_endpoint(client):
    res = client.post("/api/audit/verify")
    assert res.status_code == 200
    data = res.json()
    assert "chain_status" in data
    assert data["is_valid"] is True

def test_assurance_run_endpoint(client):
    res = client.post("/api/assurance/run")
    assert res.status_code == 200
    data = res.json()
    assert "overall_trust_score" in data
    assert "components" in data
    assert "dataset_integrity" in data["components"]
    assert "model_integrity" in data["components"]
    assert "inference_integrity" in data["components"]
    assert "distribution_stability" in data["components"]

def test_inference_tamper_test(client):
    res = client.post("/api/inference/tamper-test", json={
        "inference_id": "INF-TEST-001",
        "tamper_field": "prediction_result",
        "new_value": "TAMPERED_CLASS"
    })
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "TAMPER DETECTED"
    assert data["original_hash"] != data["current_hash"]

def test_evidence_query(client):
    res = client.get("/api/evidence")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) > 0
    first = data[0]
    assert "what_happened" in first
    assert "why_flagged" in first
    assert "recommended_action" in first
    assert "limitations" in first
