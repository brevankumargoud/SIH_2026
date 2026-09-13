from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import uuid

from app.api.deps import get_db, get_current_user
from app.core.security import (
    verify_password, get_password_hash, 
    create_access_token, create_refresh_token, 
    REFRESH_TOKEN_EXPIRE_DAYS
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.audit_log import AuditLog
from app.schemas.auth import Token, UserResponse, RefreshRequest

router = APIRouter()

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """OAuth2 compatible token login, get an access token for future requests."""
    user = db.query(User).filter(
        (User.username == form_data.username) | (User.email == form_data.username)
    ).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        if user:
            audit = AuditLog(user_id=user.id, action="AUTH_LOGIN_FAILURE", status="failed", details={"reason": "Invalid password"})
            db.add(audit)
            db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
        
    access_token = create_access_token(subject=user.id)
    secret = create_refresh_token()
    
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    rt = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(secret),
        expires_at=expires
    )
    db.add(rt)
    db.commit()
    db.refresh(rt)
    
    # Store secret alongside ID so we can look it up O(1)
    client_refresh_token = f"{rt.id}:{secret}"
    
    audit = AuditLog(user_id=user.id, action="AUTH_LOGIN_SUCCESS", status="allowed")
    db.add(audit)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": client_refresh_token}

@router.post("/refresh", response_model=Token)
def refresh_token(
    request: RefreshRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    parts = request.refresh_token.split(":")
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token format")
        
    rt_id_str, secret = parts
    try:
        rt_id = uuid.UUID(rt_id_str)
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    rt = db.query(RefreshToken).filter(RefreshToken.id == rt_id).first()
    if not rt:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token not found")
        
    if rt.revoked:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token revoked")
        
    if rt.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
        
    if not verify_password(secret, rt.token_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        
    user = db.query(User).filter(User.id == rt.user_id, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User inactive or deleted")
        
    # Rotate RT
    rt.revoked = True
    
    access_token = create_access_token(subject=user.id)
    new_secret = create_refresh_token()
    new_rt = RefreshToken(
        user_id=user.id,
        token_hash=get_password_hash(new_secret),
        expires_at=datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(new_rt)
    
    audit = AuditLog(user_id=user.id, action="AUTH_TOKEN_REFRESH", status="allowed")
    db.add(audit)
    db.commit()
    db.refresh(new_rt)
    
    client_refresh_token = f"{new_rt.id}:{new_secret}"
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": client_refresh_token}

@router.post("/logout")
def logout(
    request: RefreshRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Revoke refresh token."""
    parts = request.refresh_token.split(":")
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token format")
        
    try:
        rt_id = uuid.UUID(parts[0])
    except ValueError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid refresh token")
        
    rt = db.query(RefreshToken).filter(RefreshToken.id == rt_id).first()
    if rt and rt.user_id == current_user.id:
        rt.revoked = True
        
        audit = AuditLog(user_id=current_user.id, action="AUTH_LOGOUT", status="allowed")
        db.add(audit)
        db.commit()
        
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
def read_current_user(
    current_user: User = Depends(get_current_user)
):
    """Get current user safely."""
    roles = [ur.role.name for ur in current_user.roles]
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        is_active=current_user.is_active,
        roles=roles
    )
