"""
Irish Bank Fraud Detection System
Utility functions and helpers
"""
import random
import string
from datetime import datetime, timedelta
from typing import List
import numpy as np

from models.schemas import Transaction, Merchant, Card, Location, TransactionStatus, RiskLevel

def generate_transaction_id() -> str:
    """Generate a unique transaction ID"""
    return f"TXN_{''.join(random.choices(string.ascii_uppercase + string.digits, k=12))}"

def generate_sample_data(count: int = 100) -> List[Transaction]:
    """Generate sample transaction data for demonstration"""
    transactions = []
    
    # Sample merchants
    merchants = [
        {"name": "SuperValu Dublin", "category": "grocery", "risk": 0.1, "country": "IRL"},
        {"name": "Tesco Express", "category": "grocery", "risk": 0.1, "country": "IRL"},
        {"name": "Amazon EU", "category": "online", "risk": 0.3, "country": "LUX"},
        {"name": "PayPal Transfer", "category": "transfer", "risk": 0.4, "country": "USA"},
        {"name": "Crypto Exchange", "category": "crypto", "risk": 0.8, "country": "MLT"},
        {"name": "Shell Petrol", "category": "fuel", "risk": 0.1, "country": "IRL"},
        {"name": "Starbucks", "category": "restaurant", "risk": 0.1, "country": "IRL"},
        {"name": "Unknown Merchant", "category": "unknown", "risk": 0.9, "country": "RUS"},
        {"name": "Dunnes Stores", "category": "retail", "risk": 0.1, "country": "IRL"},
        {"name": "Penneys", "category": "clothing", "risk": 0.1, "country": "IRL"}
    ]
    
    # Sample card types
    card_types = ["Visa", "Mastercard", "American Express"]
    
    # Sample countries
    countries = ["IRL", "GBR", "USA", "DEU", "FRA", "ESP", "ITA", "RUS", "CHN", "BRA"]
    
    for i in range(count):
        merchant_data = random.choice(merchants)
        
        # Generate transaction
        transaction = Transaction(
            id=generate_transaction_id(),
            user_id=f"USER_{random.randint(1000, 9999)}",
            amount=round(random.lognormal(4, 1.5), 2),  # Log-normal distribution for realistic amounts
            currency="EUR",
            timestamp=datetime.now() - timedelta(
                minutes=random.randint(1, 10080)  # Last week
            ),
            merchant=Merchant(
                id=f"MERCH_{random.randint(100, 999)}",
                name=merchant_data["name"],
                category=merchant_data["category"],
                risk_score=merchant_data["risk"],
                country=merchant_data["country"]
            ),
            card=Card(
                last4=f"{random.randint(1000, 9999)}",
                type=random.choice(card_types),
                issuer="Irish Bank",
                country="IRL"
            ),
            location=Location(
                country=random.choice(countries),
                city=f"City_{random.randint(1, 100)}",
                latitude=random.uniform(51.0, 55.0),  # Ireland-ish coordinates
                longitude=random.uniform(-10.0, -6.0),
                ip_address=f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
            ),
            status=random.choice(list(TransactionStatus)),
            description=f"Payment to {merchant_data['name']}"
        )
        
        # Calculate risk score based on various factors
        risk_score = 0.0
        
        # Amount risk
        if transaction.amount > 1000:
            risk_score += 0.3
        elif transaction.amount > 500:
            risk_score += 0.1
        
        # Merchant risk
        risk_score += merchant_data["risk"] * 0.4
        
        # Time risk (late night/early morning)
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 23:
            risk_score += 0.2
        
        # Location risk (non-Irish transactions)
        if transaction.location.country != "IRL":
            risk_score += 0.3
        
        # Add some randomness
        risk_score += random.uniform(-0.1, 0.1)
        risk_score = max(0.0, min(1.0, risk_score))
        
        transaction.risk_score = risk_score
        
        # Determine risk level
        if risk_score >= 0.7:
            transaction.risk_level = RiskLevel.HIGH
        elif risk_score >= 0.4:
            transaction.risk_level = RiskLevel.MEDIUM
        else:
            transaction.risk_level = RiskLevel.LOW
        
        # Simulate fraud labels (10% fraud rate)
        transaction.is_fraud = risk_score > 0.8 and random.random() < 0.3
        
        transactions.append(transaction)
    
    # Sort by timestamp (newest first)
    transactions.sort(key=lambda x: x.timestamp, reverse=True)
    
    return transactions

def format_currency(amount: float, currency: str = "EUR") -> str:
    """Format currency amount"""
    if currency == "EUR":
        return f"€{amount:,.2f}"
    else:
        return f"{amount:,.2f} {currency}"

def calculate_risk_color(risk_score: float) -> str:
    """Get color based on risk score"""
    if risk_score >= 0.7:
        return "red"
    elif risk_score >= 0.4:
        return "orange"
    else:
        return "green"

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent XSS"""
    if not text:
        return ""
    
    # Basic HTML escaping
    text = text.replace("&", "&amp;")
    text = text.replace("<", "&lt;")
    text = text.replace(">", "&gt;")
    text = text.replace('"', "&quot;")
    text = text.replace("'", "&#x27;")
    
    return text

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_secure_token(length: int = 32) -> str:
    """Generate a secure random token"""
    import secrets
    return secrets.token_urlsafe(length)