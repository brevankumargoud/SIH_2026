import requests
import uuid
import sys
import time

base_url = "http://localhost:8001"

# 1. Login with dev user
login_res = requests.post(
    f"{base_url}/auth/login",
    data={"username": "dev_user", "password": "dev_password_only"}
)
if login_res.status_code != 200:
    print(f"Login failed: {login_res.text}")
    sys.exit(1)
token = login_res.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}

# 2. Get default KB
kb_res = requests.get(f"{base_url}/knowledge-bases/default", headers=headers)
if kb_res.status_code != 200:
    print(f"KB fetch failed: {kb_res.text}")
    sys.exit(1)
kb_id = kb_res.json()["id"]
print(f"Got KB: {kb_id}")

# 3. Create a unique document
test_text = "The quick brown fox jumps over the lazy dog. In the year 2029, Sovereign AI achieved general artificial intelligence in a lab in Nevada."
with open("test_doc.txt", "w") as f:
    f.write(test_text)

# 4. Upload document
with open("test_doc.txt", "rb") as f:
    upload_res = requests.post(
        f"{base_url}/knowledge-bases/{kb_id}/documents",
        headers=headers,
        files={"file": ("test_doc.txt", f, "text/plain")}
    )
if upload_res.status_code != 200:
    print(f"Upload failed: {upload_res.text}")
    sys.exit(1)
print(f"Upload success: {upload_res.json()}")

# wait briefly
time.sleep(1)

# 5. Search document
search_res = requests.post(
    f"{base_url}/knowledge-bases/{kb_id}/search",
    headers=headers,
    json={"knowledge_base_id": kb_id, "query": "Where did Sovereign AI achieve general artificial intelligence?"}
)
if search_res.status_code != 200:
    print(f"Search failed: {search_res.text}")
    sys.exit(1)

print(f"Search results:")
for r in search_res.json():
    print(f" - {r['filename']}: {r['content']} (Score: {r['score']})")
