"""
Database connection and session management
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from datetime import datetime
from app.config import settings

# Database setup
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Database Models
class TransactionDB(Base):
    """Transaction database model"""
    __tablename__ = "transactions"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, unique=True, index=True)
    amount = Column(Float)
    merchant = Column(String)
    card_last4 = Column(String)
    location = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    risk_score = Column(Float)
    is_fraud = Column(Boolean, default=False)
    status = Column(String, default="pending")


class UserDB(Base):
    """User database model"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    hashed_password = Column(String)
    role = Column(String, default="analyst")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class FraudAlertDB(Base):
    """Fraud alert database model"""
    __tablename__ = "fraud_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    transaction_id = Column(String, index=True)
    alert_type = Column(String)
    risk_score = Column(Float)
    description = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


def init_db():
    """Initialize database and create tables"""
    Base.metadata.create_all(bind=engine)
    
    # Create sample data if database is empty
    db = SessionLocal()
    try:
        if db.query(UserDB).count() == 0:
            create_sample_data(db)
    finally:
        db.close()


def create_sample_data(db: Session):
    """Create sample data for demonstration"""
    from core.security import get_password_hash
    import random
    from datetime import timedelta
    
    # Create admin user
    admin_user = UserDB(
        email="admin@irishbank.ie",
        full_name="Bank Administrator",
        hashed_password=get_password_hash("admin123"),
        role="admin"
    )
    db.add(admin_user)
    
    # Create sample transactions
    merchants = ["Tesco", "SuperValu", "Dunnes Stores", "Amazon", "PayPal", "Starbucks", "McDonald's"]
    locations = ["Dublin", "Cork", "Galway", "Limerick", "Waterford", "Kilkenny"]
    
    for i in range(100):
        transaction = TransactionDB(
            transaction_id=f"TXN{1000 + i}",
            amount=round(random.uniform(5.0, 500.0), 2),
            merchant=random.choice(merchants),
            card_last4=f"{random.randint(1000, 9999)}",
            location=random.choice(locations),
            timestamp=datetime.utcnow() - timedelta(hours=random.randint(0, 72)),
            risk_score=round(random.uniform(0.0, 1.0), 2),
            is_fraud=random.random() < 0.05  # 5% fraud rate
        )
        db.add(transaction)
    
    # Create sample fraud alerts
    for i in range(5):
        alert = FraudAlertDB(
            transaction_id=f"TXN{1000 + i}",
            alert_type="High Risk Transaction",
            risk_score=round(random.uniform(0.7, 1.0), 2),
            description=f"Suspicious transaction pattern detected"
        )
        db.add(alert)
    
    db.commit()


def get_db_session():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()