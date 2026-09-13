import pytest
from fastapi.testclient import TestClient
import uuid
from app.main import app
from app.db.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.models.workspace import Workspace
from app.models.workspace_member import WorkspaceMember

client = TestClient(app)

@pytest.fixture(scope="module")
def setup_auth_db():
    db = SessionLocal()
    
    # 1. Create User
    test_id = str(uuid.uuid4())[:8]
    user = User(
        username=f"authuser_{test_id}",
        email=f"auth_{test_id}@example.com",
        password_hash=get_password_hash("securepassword"),
        full_name="Auth User"
    )
    db.add(user)
    
    # 2. Create another user without access
    unauth_user = User(
        username=f"hacker_{test_id}",
        email=f"hacker_{test_id}@example.com",
        password_hash=get_password_hash("securepassword")
    )
    db.add(unauth_user)
    
    # 3. Create Role
    role = Role(name="user")
    db.add(role)
    db.commit()
    
    ur = UserRole(user_id=user.id, role_id=role.id)
    db.add(ur)
    
    # 4. Create Workspace
    ws = Workspace(name="Auth Workspace", created_by=user.id)
    db.add(ws)
    db.commit()
    db.refresh(user)
    db.refresh(unauth_user)
    db.refresh(ws)
    
    yield {
        "user": user, 
        "unauth_user": unauth_user,
        "password": "securepassword", 
        "workspace_id": str(ws.id)
    }
    
    db.delete(ws)
    db.delete(unauth_user)
    db.delete(user)
    db.delete(role)
    db.commit()
    db.close()

def test_login_success(setup_auth_db):
    app.dependency_overrides.clear() # Clear conftest mocks
    res = client.post("/auth/login", data={
        "username": setup_auth_db["user"].username,
        "password": setup_auth_db["password"]
    })
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert "refresh_token" in data
    return data["access_token"], data["refresh_token"]

def test_login_failure(setup_auth_db):
    app.dependency_overrides.clear()
    res = client.post("/auth/login", data={
        "username": setup_auth_db["user"].username,
        "password": "wrongpassword"
    })
    assert res.status_code == 401

def test_get_me(setup_auth_db):
    app.dependency_overrides.clear()
    access_token, _ = test_login_success(setup_auth_db)
    
    res = client.get("/auth/me", headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    data = res.json()
    assert data["username"] == setup_auth_db["user"].username
    assert "user" in data["roles"]

def test_refresh_token(setup_auth_db):
    app.dependency_overrides.clear()
    _, rt = test_login_success(setup_auth_db)
    
    res = client.post("/auth/refresh", json={"refresh_token": rt})
    assert res.status_code == 200
    data = res.json()
    assert "access_token" in data
    assert data["refresh_token"] != rt

def test_logout(setup_auth_db):
    app.dependency_overrides.clear()
    access_token, rt = test_login_success(setup_auth_db)
    
    res = client.post("/auth/logout", json={"refresh_token": rt}, headers={"Authorization": f"Bearer {access_token}"})
    assert res.status_code == 200
    
    # Try using the old refresh token
    res2 = client.post("/auth/refresh", json={"refresh_token": rt})
    assert res2.status_code == 401

def test_unauthorized_workspace_access(setup_auth_db):
    app.dependency_overrides.clear()
    
    # Login as unauth_user
    res = client.post("/auth/login", data={
        "username": setup_auth_db["unauth_user"].username,
        "password": setup_auth_db["password"]
    })
    access_token = res.json()["access_token"]
    
    # Attempt to list conversations in the other user's workspace
    ws_id = setup_auth_db["workspace_id"]
    res2 = client.get(f"/conversations?workspace_id={ws_id}", headers={"Authorization": f"Bearer {access_token}"})
    
    # Expect 403 Forbidden due to IDOR RBAC check
    assert res2.status_code == 403

def test_admin_endpoint_as_user(setup_auth_db):
    app.dependency_overrides.clear()
    access_token, _ = test_login_success(setup_auth_db)
    
    res = client.get("/workers", headers={"Authorization": f"Bearer {access_token}"})
    # Since role is "user", require_admin will fail
    assert res.status_code == 403
