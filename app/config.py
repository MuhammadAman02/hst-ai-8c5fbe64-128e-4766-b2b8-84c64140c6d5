"""
Application configuration management
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application Settings
    app_name: str = "Irish Bank Fraud Detection System"
    app_version: str = "1.0.0"
    environment: str = "development"
    debug: bool = True
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    
    # Database Configuration
    database_url: str = "sqlite:///./fraud_detection.db"
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-in-production"
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # Fraud Detection Settings
    fraud_threshold: float = 0.7
    high_risk_threshold: float = 0.9
    alert_email: str = "security@irishbank.ie"
    
    # External API Configuration
    bank_api_url: str = "https://api.irishbank.ie"
    notification_service_url: str = "https://notifications.irishbank.ie"
    
    # Monitoring Configuration
    enable_monitoring: bool = True
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()