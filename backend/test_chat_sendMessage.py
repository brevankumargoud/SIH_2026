import requests

base_url = "http://localhost:8001"
login_res = requests.post(f"{base_url}/auth/login", data={"username": "dev_user", "password": "dev_password_only"})
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# Mocking frontend behavior
ws_res = requests.get(f"{base_url}/workspaces/default", headers=headers)
workspace_id = ws_res.json()["id"]

conv_res = requests.post(f"{base_url}/conversations", headers=headers, json={"title": "New Conversation", "workspace_id": workspace_id})
conv_id = conv_res.json()["id"]
print("Created conv:", conv_id)

msg_res = requests.post(f"{base_url}/conversations/{conv_id}/messages", headers=headers, json={"content": "Explain in one sentence what a refinery is."})
print("Message response status:", msg_res.status_code)
if msg_res.status_code != 200:
    print(msg_res.text)

