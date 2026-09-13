import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app

client = TestClient(app)

def setup_workers():
    # Setup Worker 1 (Text, Coding, Context 4096)
    client.post("/workers/register", json={
        "name": "worker-1",
        "ip_address": "127.0.0.1",
        "port": 8001,
        "models": [
            {
                "model_identifier": "model-text-coding",
                "name": "Coder",
                "model_type": "llm",
                "modalities": ["text"],
                "capabilities": ["coding"],
                "context_length": 4096
            }
        ]
    })
    
    # Setup Worker 2 (Text, Image, Context 8192)
    res = client.post("/workers/register", json={
        "name": "worker-2",
        "ip_address": "127.0.0.1",
        "port": 8002,
        "models": [
            {
                "model_identifier": "model-vision",
                "name": "Vision",
                "model_type": "vlm",
                "modalities": ["text", "image"],
                "capabilities": ["general"],
                "context_length": 8192
            }
        ]
    })
    worker_2_id = res.json()["id"]
    
    # Setup Worker 3 (Offline)
    res = client.post("/workers/register", json={
        "name": "worker-offline",
        "ip_address": "127.0.0.1",
        "port": 8003,
        "models": [
            {
                "model_identifier": "model-offline",
                "name": "Offline",
                "model_type": "llm",
                "context_length": 2048
            }
        ]
    })
    worker_3_id = res.json()["id"]
    client.post(f"/workers/{worker_3_id}/deactivate")

@pytest.fixture(autouse=True)
def run_around_tests():
    # We rely on an empty DB, setup_workers populates it for test.
    # A complete teardown would be better but we'll just populate.
    setup_workers()
    yield

@patch("app.services.model_worker_client.ModelWorkerClient.generate")
def test_successful_routing_and_inference(mock_generate):
    mock_generate.return_value = {
        "output": "Mock output",
        "model": "model-text-coding",
        "metadata": {"tokens": 10}
    }
    
    req = {
        "messages": [{"role": "user", "content": "Code something."}],
        "required_capabilities": ["coding"]
    }
    res = client.post("/models/infer", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["output"] == "Mock output"
    assert data["model"] == "model-text-coding"
    assert "worker_id" in data

@patch("app.services.model_worker_client.ModelWorkerClient.generate")
def test_modality_routing(mock_generate):
    mock_generate.return_value = {"output": "Vision output", "model": "model-vision"}
    
    req = {
        "messages": [{"role": "user", "content": "Look at this."}],
        "required_modalities": ["image"]
    }
    res = client.post("/models/infer", json=req)
    assert res.status_code == 200
    data = res.json()
    assert data["model"] == "model-vision"

def test_no_eligible_candidate():
    req = {
        "messages": [{"role": "user", "content": "Fail me."}],
        "required_capabilities": ["super-magic"]
    }
    res = client.post("/models/infer", json=req)
    assert res.status_code == 400
    assert "No available models match" in res.json()["detail"]

def test_context_length_filtering():
    req = {
        "messages": [{"role": "user", "content": "Long context."}],
        "min_context_length": 8000
    }
    # Only model-vision has 8192, model-text-coding has 4096. 
    # Let's mock generate.
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_generate:
        mock_generate.return_value = {"output": "ok", "model": "model-vision"}
        res = client.post("/models/infer", json=req)
        assert res.status_code == 200
        assert res.json()["model"] == "model-vision"

def test_preferred_model():
    req = {
        "messages": [{"role": "user", "content": "Prefer coding."}],
        "preferred_model": "model-text-coding"
    }
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_generate:
        mock_generate.return_value = {"output": "ok", "model": "model-text-coding"}
        res = client.post("/models/infer", json=req)
        assert res.status_code == 200
        assert res.json()["model"] == "model-text-coding"

def test_offline_model_filtering():
    req = {
        "messages": [{"role": "user", "content": "test"}],
        "preferred_model": "model-offline"
    }
    # It should not match model-offline since its worker is offline.
    # It will fallback to deterministic selection (the highest context length, which is model-vision).
    with patch("app.services.model_worker_client.ModelWorkerClient.generate") as mock_generate:
        mock_generate.return_value = {"output": "ok", "model": "model-vision"}
        res = client.post("/models/infer", json=req)
        assert res.status_code == 200
        assert res.json()["model"] == "model-vision"

@patch("app.services.model_worker_client.ModelWorkerClient.generate")
def test_worker_failure_handling(mock_generate):
    # Simulate a network failure where client returns None
    mock_generate.return_value = None
    
    req = {"messages": [{"role": "user", "content": "Fail via network."}]}
    res = client.post("/models/infer", json=req)
    assert res.status_code == 502
    assert "Worker inference failed" in res.json()["detail"]

def test_validation_failure():
    req = {"messages": "not-a-list"}
    res = client.post("/models/infer", json=req)
    assert res.status_code == 422
