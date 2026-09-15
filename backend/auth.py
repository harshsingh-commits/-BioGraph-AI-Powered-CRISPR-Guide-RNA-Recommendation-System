import hashlib
import json
import os
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

JWT_ALGORITHM = "HS256"
bearer = HTTPBearer(auto_error=False)


def _users():
    configured = os.getenv("BIOGRAPH_USERS")
    if configured:
        return json.loads(configured)
    if os.getenv("BIOGRAPH_ALLOW_DEV_USERS", "true").lower() == "true":
        return {
            "researcher": {"password": "researcher", "role": "Researcher"},
            "reviewer": {"password": "reviewer", "role": "Reviewer"},
            "admin": {"password": "admin", "role": "Admin"},
        }
    return {}


def _secret():
    secret = os.getenv("BIOGRAPH_JWT_SECRET")
    if not secret:
        raise RuntimeError("BIOGRAPH_JWT_SECRET must be configured.")
    return secret


def issue_token(username, role):
    payload = {
        "sub": username,
        "role": role,
        "exp": datetime.now(UTC) + timedelta(hours=8),
    }
    return jwt.encode(payload, _secret(), algorithm=JWT_ALGORITHM)


def authenticate(username, password):
    user = _users().get(username)
    if (
        not user
        or not hashlib.sha256(password.encode()).hexdigest()
        == hashlib.sha256(user["password"].encode()).hexdigest()
    ):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return {
        "access_token": issue_token(username, user["role"]),
        "token_type": "bearer",
        "role": user["role"],
    }


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer)):
    if credentials is None:
        raise HTTPException(status_code=401, detail="Bearer token required")
    try:
        return jwt.decode(credentials.credentials, _secret(), algorithms=[JWT_ALGORITHM])
    except jwt.PyJWTError as error:
        raise HTTPException(status_code=401, detail="Invalid or expired token") from error


def require_roles(*roles):
    def dependency(user=Depends(current_user)):
        if user.get("role") not in roles:
            raise HTTPException(status_code=403, detail="Insufficient role")
        return user

    return dependency
