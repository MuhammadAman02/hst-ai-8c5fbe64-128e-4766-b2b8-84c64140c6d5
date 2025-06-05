"""
Security utilities for authentication and authorization
"""
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    """Create JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def verify_token(token: str) -> Optional[dict]:
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        return None


def get_current_user(token: str) -> Optional[dict]:
    """Get current user from token"""
    payload = verify_token(token)
    if payload is None:
        return None
    
    email: str = payload.get("sub")
    if email is None:
        return None
    
    # In production, fetch user from database
    return {"email": email}


class SecurityHeaders:
    """Security headers for web responses"""
    
    @staticmethod
    def get_security_headers() -> dict:
        """Get security headers"""
        return {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
            "Referrer-Policy": "strict-origin-when-cross-origin"
        }


def validate_input(data: str, max_length: int = 1000) -> str:
    """Validate and sanitize input data"""
    if not data:
        return ""
    
    # Basic sanitization
    sanitized = data.strip()[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", "&", "\"", "'", "/"]
    for char in dangerous_chars:
        sanitized = sanitized.replace(char, "")
    
    return sanitized


def check_rate_limit(user_id: str, action: str, limit: int = 100, window: int = 3600) -> bool:
    """Check rate limiting for user actions"""
    # In production, implement with Redis or similar
    # For now, always allow
    return True