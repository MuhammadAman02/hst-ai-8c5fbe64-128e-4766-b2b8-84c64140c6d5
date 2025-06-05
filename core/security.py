"""
Irish Bank Fraud Detection System
Security utilities and authentication
"""
import hashlib
import secrets
import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from models.schemas import User, UserLogin

class SecurityService:
    """Security service for authentication and authorization"""
    
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.secret_key = secrets.token_urlsafe(32)
        self.algorithm = "HS256"
        self.access_token_expire_minutes = 30
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password"""
        return self.pwd_context.hash(password)
    
    def create_access_token(self, data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.PyJWTError:
            return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user (demo implementation)"""
        # Demo users
        demo_users = {
            "admin@irishbank.ie": {
                "password_hash": self.get_password_hash("admin123"),
                "user": User(
                    id="admin_001",
                    email="admin@irishbank.ie",
                    full_name="System Administrator",
                    role="admin",
                    created_at=datetime.now()
                )
            }
        }
        
        user_data = demo_users.get(email)
        if user_data and self.verify_password(password, user_data["password_hash"]):
            return user_data["user"]
        return None