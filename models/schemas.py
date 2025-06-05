"""
Pydantic models for data validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, validator
from enum import Enum


class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    ANALYST = "analyst"
    VIEWER = "viewer"


class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    BLOCKED = "blocked"
    INVESTIGATING = "investigating"


class AlertStatus(str, Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class User(BaseModel):
    """User model"""
    id: int
    email: EmailStr
    full_name: str
    role: UserRole
    is_active: bool = True
    created_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """User creation model"""
    email: EmailStr
    full_name: str
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.ANALYST
    
    @validator('password')
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        return v


class UserLogin(BaseModel):
    """User login model"""
    email: EmailStr
    password: str


class Transaction(BaseModel):
    """Transaction model"""
    id: Optional[int] = None
    transaction_id: str
    amount: float = Field(..., gt=0)
    merchant: str
    card_last4: str = Field(..., regex=r'^\d{4}$')
    location: str
    timestamp: datetime
    risk_score: float = Field(..., ge=0.0, le=1.0)
    is_fraud: bool = False
    status: TransactionStatus = TransactionStatus.PENDING
    
    class Config:
        from_attributes = True
    
    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be positive')
        if v > 1000000:  # 1 million limit
            raise ValueError('Amount exceeds maximum limit')
        return round(v, 2)


class TransactionCreate(BaseModel):
    """Transaction creation model"""
    amount: float = Field(..., gt=0)
    merchant: str
    card_last4: str = Field(..., regex=r'^\d{4}$')
    location: str
    
    @validator('merchant')
    def validate_merchant(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Merchant name must be at least 2 characters')
        return v.strip()


class FraudAlert(BaseModel):
    """Fraud alert model"""
    id: Optional[int] = None
    transaction_id: str
    alert_type: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    description: str
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime
    resolved_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class FraudAlertCreate(BaseModel):
    """Fraud alert creation model"""
    transaction_id: str
    alert_type: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    description: str


class RiskAssessment(BaseModel):
    """Risk assessment model"""
    transaction_id: str
    risk_score: float = Field(..., ge=0.0, le=1.0)
    risk_factors: List[str]
    confidence: float = Field(..., ge=0.0, le=1.0)
    recommendation: str
    
    @validator('risk_factors')
    def validate_risk_factors(cls, v):
        if not v:
            raise ValueError('At least one risk factor must be provided')
        return v


class SystemMetrics(BaseModel):
    """System metrics model"""
    timestamp: datetime
    transactions_today: int
    fraud_detected: int
    amount_blocked: float
    system_status: str
    cpu_usage: float = Field(..., ge=0.0, le=100.0)
    memory_usage: float = Field(..., ge=0.0, le=100.0)
    active_connections: int


class FraudPattern(BaseModel):
    """Fraud pattern model"""
    pattern_id: str
    pattern_type: str
    description: str
    risk_weight: float = Field(..., ge=0.0, le=1.0)
    detection_count: int = 0
    last_detected: Optional[datetime] = None


class GeolocationData(BaseModel):
    """Geolocation data model"""
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    city: str
    country: str
    ip_address: Optional[str] = None


class TransactionAnalysis(BaseModel):
    """Transaction analysis result model"""
    transaction_id: str
    analysis_timestamp: datetime
    risk_assessment: RiskAssessment
    geolocation: Optional[GeolocationData] = None
    velocity_check: Dict[str, Any]
    pattern_matches: List[FraudPattern]
    final_decision: str
    confidence_score: float = Field(..., ge=0.0, le=1.0)


class AlertSummary(BaseModel):
    """Alert summary model"""
    total_alerts: int
    active_alerts: int
    resolved_alerts: int
    false_positives: int
    high_risk_alerts: int
    medium_risk_alerts: int
    low_risk_alerts: int


class DashboardData(BaseModel):
    """Dashboard data model"""
    metrics: SystemMetrics
    recent_transactions: List[Transaction]
    active_alerts: List[FraudAlert]
    alert_summary: AlertSummary
    risk_distribution: Dict[str, int]


class APIResponse(BaseModel):
    """Generic API response model"""
    success: bool
    message: str
    data: Optional[Any] = None
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class HealthCheck(BaseModel):
    """Health check response model"""
    status: str
    timestamp: datetime
    version: str
    database_status: str
    ml_model_status: str
    external_services_status: Dict[str, str]


# Token models
class Token(BaseModel):
    """JWT token model"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    """Token data model"""
    email: Optional[str] = None
    role: Optional[str] = None