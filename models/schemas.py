"""
Irish Bank Fraud Detection System
Pydantic models for data validation and serialization
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from pydantic import BaseModel, Field, validator
from decimal import Decimal

class TransactionStatus(str, Enum):
    """Transaction status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    DECLINED = "declined"
    BLOCKED = "blocked"
    INVESTIGATING = "investigating"

class RiskLevel(str, Enum):
    """Risk level enumeration"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class AlertStatus(str, Enum):
    """Alert status enumeration"""
    ACTIVE = "active"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"

class UserRole(str, Enum):
    """User role enumeration"""
    ADMIN = "admin"
    ANALYST = "analyst"
    INVESTIGATOR = "investigator"
    VIEWER = "viewer"

class Location(BaseModel):
    """Geographic location model"""
    country: str = Field(..., min_length=2, max_length=3)
    city: Optional[str] = Field(None, max_length=100)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    ip_address: Optional[str] = Field(None, pattern=r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$')

class Merchant(BaseModel):
    """Merchant information model"""
    id: str = Field(..., min_length=1, max_length=50)
    name: str = Field(..., min_length=1, max_length=200)
    category: str = Field(..., min_length=1, max_length=100)
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    country: str = Field(..., min_length=2, max_length=3)

class Card(BaseModel):
    """Card information model"""
    last4: str = Field(..., pattern=r'^\d{4}$')
    type: str = Field(..., min_length=1, max_length=20)
    issuer: str = Field(..., min_length=1, max_length=50)
    country: str = Field(..., min_length=2, max_length=3)

class Transaction(BaseModel):
    """Transaction model for fraud detection"""
    id: str = Field(..., min_length=1, max_length=100)
    user_id: str = Field(..., min_length=1, max_length=100)
    amount: float = Field(..., gt=0)
    currency: str = Field("EUR", pattern=r'^[A-Z]{3}$')
    timestamp: datetime
    merchant: Merchant
    card: Card
    location: Location
    status: TransactionStatus = TransactionStatus.PENDING
    description: Optional[str] = Field(None, max_length=500)
    reference: Optional[str] = Field(None, max_length=100)
    
    # Risk assessment fields
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0)
    risk_level: Optional[RiskLevel] = None
    risk_factors: Optional[List[str]] = []
    
    # Fraud detection metadata
    is_fraud: Optional[bool] = None
    fraud_probability: Optional[float] = Field(None, ge=0.0, le=1.0)
    model_version: Optional[str] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class RiskFactor(BaseModel):
    """Individual risk factor model"""
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=500)
    weight: float = Field(..., ge=0.0, le=1.0)
    value: float = Field(..., ge=0.0, le=1.0)
    threshold: float = Field(..., ge=0.0, le=1.0)

class RiskAssessment(BaseModel):
    """Risk assessment model"""
    transaction_id: str = Field(..., min_length=1, max_length=100)
    overall_score: float = Field(..., ge=0.0, le=1.0)
    risk_level: RiskLevel
    factors: List[RiskFactor]
    model_confidence: float = Field(..., ge=0.0, le=1.0)
    assessment_time: datetime
    model_version: str = Field(..., min_length=1, max_length=50)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class FraudAlert(BaseModel):
    """Fraud alert model"""
    id: str = Field(..., min_length=1, max_length=100)
    transaction_id: str = Field(..., min_length=1, max_length=100)
    alert_type: str = Field(..., min_length=1, max_length=100)
    severity: RiskLevel
    status: AlertStatus = AlertStatus.ACTIVE
    created_at: datetime
    updated_at: Optional[datetime] = None
    assigned_to: Optional[str] = Field(None, max_length=100)
    resolution_notes: Optional[str] = Field(None, max_length=1000)
    false_positive: bool = False
    
    # Alert details
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=1000)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    triggered_rules: List[str] = []
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class TransactionAnalysis(BaseModel):
    """Transaction analysis result model"""
    transaction: Transaction
    risk_assessment: RiskAssessment
    alerts: List[FraudAlert] = []
    recommendations: List[str] = []
    processing_time_ms: float = Field(..., ge=0)
    analysis_timestamp: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class User(BaseModel):
    """User model for authentication"""
    id: str = Field(..., min_length=1, max_length=100)
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    full_name: str = Field(..., min_length=1, max_length=200)
    role: UserRole
    is_active: bool = True
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class UserLogin(BaseModel):
    """User login request model"""
    email: str = Field(..., pattern=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    password: str = Field(..., min_length=6, max_length=100)

class SystemMetrics(BaseModel):
    """System performance metrics model"""
    timestamp: datetime
    total_transactions: int = Field(..., ge=0)
    fraud_detected: int = Field(..., ge=0)
    false_positives: int = Field(..., ge=0)
    active_alerts: int = Field(..., ge=0)
    avg_processing_time_ms: float = Field(..., ge=0)
    model_accuracy: float = Field(..., ge=0.0, le=1.0)
    system_load: float = Field(..., ge=0.0, le=1.0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ModelPerformance(BaseModel):
    """ML model performance metrics"""
    model_name: str = Field(..., min_length=1, max_length=100)
    version: str = Field(..., min_length=1, max_length=50)
    accuracy: float = Field(..., ge=0.0, le=1.0)
    precision: float = Field(..., ge=0.0, le=1.0)
    recall: float = Field(..., ge=0.0, le=1.0)
    f1_score: float = Field(..., ge=0.0, le=1.0)
    auc_roc: float = Field(..., ge=0.0, le=1.0)
    training_date: datetime
    evaluation_date: datetime
    sample_size: int = Field(..., ge=0)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class APIResponse(BaseModel):
    """Standard API response model"""
    success: bool
    message: str = Field(..., min_length=1, max_length=500)
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = Field(None, max_length=50)
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }