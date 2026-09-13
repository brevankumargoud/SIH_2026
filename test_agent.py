import requests
import sys
import time

base_url = "http://localhost:8001"

# 1. Login
login_res = requests.post(
    f"{base_url}/auth/login",
    data={"username": "testadmin_55957368", "password": "dev_password_only"}
)
if login_res.status_code != 200:
    print(f"Login failed: {login_res.text}")
    sys.exit(1)
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Setup Default KB first (so the agent can link to it)
requests.get(f"{base_url}/knowledge-bases/default", headers=headers)

# 3. Setup Default Agent
agent_res = requests.get(f"{base_url}/agents/default", headers=headers)
if agent_res.status_code != 200:
    print(f"Agent fetch failed: {agent_res.text}")
    sys.exit(1)
agent_id = agent_res.json()["id"]
print(f"Got Agent: {agent_id}")

# 4. Run Task
run_res = requests.post(
    f"{base_url}/agents/{agent_id}/runs",
    headers=headers,
    json={"input_data": {"task": "Find the safety protocol in the KB."}}
)
if run_res.status_code != 200:
    print(f"Run failed: {run_res.text}")
    sys.exit(1)

print(f"Run Result: {run_res.json()}")
