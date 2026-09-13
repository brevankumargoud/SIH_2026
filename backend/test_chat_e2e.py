import requests

base_url = "http://localhost:8001"
login_res = requests.post(f"{base_url}/auth/login", data={"username": "dev_user", "password": "dev_password_only"})
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

ws_res = requests.get(f"{base_url}/workspaces/default", headers=headers)
print("Workspace:", ws_res.json())
workspace_id = ws_res.json()["id"]

conv_res = requests.post(f"{base_url}/conversations", headers=headers, json={"title": "New Conversation", "workspace_id": workspace_id})
print("Conversation:", conv_res.json())

