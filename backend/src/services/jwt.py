from datetime import datetime, timedelta, timezone
from typing import Dict, Any, List, Optional
import jwt
from fastapi import HTTPException, status
from uuid import uuid4

from config import settings


class JWTTokenService():
    """JWT implementation of token service with refresh tokens"""
    
    def create_access_token(
        self,
        user_id: str,
    ) -> str:
        """Create JWT access token (short-lived)"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.jwt.access_token.expire_minutes)
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "type": "access"
        }
        return jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create refresh token (long-lived)"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.jwt.refresh_token.expire_days)
        
        payload = {
            "sub": user_id,
            "exp": expire,
            "iat": now,
            "type": "refresh"
        }
        return jwt.encode(payload, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT access token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
                options={"verify_exp": True}
            )
            if payload.get("type") != "access":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT refresh token"""
        try:
            payload = jwt.decode(
                token,
                settings.jwt.secret_key,
                algorithms=[settings.jwt.algorithm],
                options={"verify_exp": True}
            )
            if payload.get("type") != "refresh":
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token type")
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired")
        except jwt.InvalidTokenError as e:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))