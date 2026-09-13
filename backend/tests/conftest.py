import pytest
from fastapi.testclient import TestClient
import uuid
from app.main import app
from app.api.deps import get_current_user, require_workspace_access, require_agent_access, require_admin
from app.models.user import User
from app.models.role import Role
from app.models.user_role import UserRole
from app.db.database import SessionLocal

# Mock current user for all non-auth tests
MOCK_USER_ID = uuid.uuid4()

from app.api.deps import get_db
from sqlalchemy.orm import Session
from fastapi import Depends

def get_or_create_mock_user(db: Session):
    u = db.query(User).filter(User.id == MOCK_USER_ID).first()
    if not u:
        email = f"admin_{MOCK_USER_ID.hex[:8]}@test.com"
        u = User(id=MOCK_USER_ID, username=f"testadmin_{MOCK_USER_ID.hex[:8]}", email=email, password_hash="x", is_active=True)
        db.add(u)
        r = db.query(Role).filter(Role.name == "admin").first()
        if not r:
            r = Role(name="admin")
            db.add(r)
        try:
            db.commit()
            ur = UserRole(user_id=u.id, role_id=r.id)
            db.add(ur)
            db.commit()
        except Exception:
            db.rollback()
            u = db.query(User).filter(User.id == MOCK_USER_ID).first()
    return u

def override_get_current_user(db: Session = Depends(get_db)):
    return get_or_create_mock_user(db)

def override_require_admin(db: Session = Depends(get_db)):
    return override_get_current_user(db)

def override_require_workspace_access(db: Session = Depends(get_db)):
    return override_get_current_user(db)

def override_require_agent_access(db: Session = Depends(get_db)):
    pass

@pytest.fixture(autouse=True)
def mock_auth_dependencies():
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[require_admin] = override_require_admin
    app.dependency_overrides[require_workspace_access] = override_require_workspace_access
    app.dependency_overrides[require_agent_access] = override_require_agent_access
    yield
    app.dependency_overrides.clear()
