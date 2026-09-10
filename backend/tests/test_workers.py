import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from app.main import app
from app.services.model_worker_client import ModelWorkerClient

client = TestClient(app)

def test_register_worker():
    payload = {
        "name": "test-worker",
        "ip_address": "127.0.0.1",
        "port": 8001,
        "hardware_info": {"ram": "16GB"},
        "models": [
            {
                "model_identifier": "test-model-1",
                "name": "Test Model",
                "model_type": "llm"
            }
        ]
    }
    response = client.post("/workers/register", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-worker"
    assert data["status"] == "available"
    assert len(data["models"]) == 1
    assert data["models"][0]["model_identifier"] == "test-model-1"
    
    return data["id"]

def test_list_workers():
    response = client.get("/workers")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_worker():
    worker_id = test_register_worker()
    response = client.get(f"/workers/{worker_id}")
    assert response.status_code == 200
    assert response.json()["id"] == worker_id

def test_heartbeat():
    worker_id = test_register_worker()
    response = client.post(f"/workers/{worker_id}/heartbeat")
    assert response.status_code == 200
    assert response.json()["status"] == "available"

def test_deactivate_worker():
    worker_id = test_register_worker()
    response = client.post(f"/workers/{worker_id}/deactivate")
    assert response.status_code == 200
    assert response.json()["status"] == "offline"
    assert response.json()["is_active"] is False

@patch("httpx.Client.get")
def test_worker_client_health_success(mock_get):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"status": "ok"}
    mock_get.return_value = mock_resp
    
    cl = ModelWorkerClient("127.0.0.1", 8001)
    assert cl.check_health() is True

@patch("httpx.Client.get")
def test_worker_client_health_failure(mock_get):
    mock_get.side_effect = Exception("Connection refused")
    cl = ModelWorkerClient("127.0.0.1", 8001)
    assert cl.check_health() is False
