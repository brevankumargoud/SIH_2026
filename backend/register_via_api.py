import requests

base_url = "http://localhost:8001"
# 1. Login to get token
login_res = requests.post(
    f"{base_url}/auth/login",
    data={"username": "testadmin_55957368", "password": "dev_password_only"}
)
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Register worker
payload = {
    "name": "Laptop-1-Ollama",
    "hostname": "laptop-1",
    "ip_address": "10.151.15.9",
    "port": 11434,
    "protocol": "http",
    "hardware_info": {"type": "ollama"},
    "models": [
        {
            "model_identifier": "llama3.2:1b",
            "name": "Llama 3.2 1B",
            "model_type": "LLM",
            "capabilities": ["chat"],
            "context_length": 131072
        }
    ]
}

reg_res = requests.post(f"{base_url}/workers/register", headers=headers, json=payload)
print(reg_res.status_code)
print(reg_res.text)
