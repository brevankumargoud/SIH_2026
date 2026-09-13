import requests
import time

base_url = "http://localhost:8001"
login_res = requests.post(f"{base_url}/auth/login", data={"username": "dev_user", "password": "dev_password_only"})
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

agent_res = requests.get(f"{base_url}/agents/default", headers=headers)
agent_id = agent_res.json()["id"]

print(f"Running agent {agent_id}...")
start = time.time()
run_res = requests.post(
    f"{base_url}/agents/{agent_id}/runs",
    headers=headers,
    json={"input_data": {"task": "Explain in one sentence what a refinery is."}}
)
print(f"Took {time.time()-start:.2f}s")
print(run_res.json())
