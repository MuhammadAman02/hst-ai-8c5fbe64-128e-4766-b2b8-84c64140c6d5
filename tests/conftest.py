"""
Pytest configuration and fixtures
"""
import pytest
import asyncio
from datetime import datetime
from models.schemas import Transaction, User, FraudAlert


@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_transaction():
    """Create a sample transaction for testing"""
    return Transaction(
        transaction_id="TEST001",
        amount=100.0,
        merchant="Test Merchant",
        card_last4="1234",
        location="Dublin",
        timestamp=datetime.now(),
        risk_score=0.5
    )


@pytest.fixture
def high_risk_transaction():
    """Create a high-risk transaction for testing"""
    return Transaction(
        transaction_id="TEST002",
        amount=5000.0,
        merchant="Cash Advance",
        card_last4="5678",
        location="Unknown",
        timestamp=datetime.now(),
        risk_score=0.9
    )


@pytest.fixture
def sample_user():
    """Create a sample user for testing"""
    return User(
        id=1,
        email="test@irishbank.ie",
        full_name="Test User",
        role="analyst",
        is_active=True
    )


@pytest.fixture
def admin_user():
    """Create an admin user for testing"""
    return User(
        id=2,
        email="admin@irishbank.ie",
        full_name="Admin User",
        role="admin",
        is_active=True
    )


@pytest.fixture
def sample_fraud_alert():
    """Create a sample fraud alert for testing"""
    return FraudAlert(
        transaction_id="TEST001",
        alert_type="High Risk Transaction",
        risk_score=0.85,
        description="Suspicious transaction pattern detected",
        created_at=datetime.now()
    )


@pytest.fixture
def mock_transactions():
    """Create a list of mock transactions for testing"""
    transactions = []
    merchants = ["Tesco", "SuperValu", "Amazon", "PayPal", "Starbucks"]
    locations = ["Dublin", "Cork", "Galway", "Limerick"]
    
    for i in range(10):
        transaction = Transaction(
            transaction_id=f"TEST{100 + i}",
            amount=round(50.0 + (i * 25.5), 2),
            merchant=merchants[i % len(merchants)],
            card_last4=f"{1000 + i}",
            location=locations[i % len(locations)],
            timestamp=datetime.now(),
            risk_score=round(0.1 + (i * 0.08), 2)
        )
        transactions.append(transaction)
    
    return transactions


@pytest.fixture
def mock_database_session():
    """Mock database session for testing"""
    class MockSession:
        def __init__(self):
            self.data = {}
        
        def add(self, obj):
            self.data[obj.id] = obj
        
        def commit(self):
            pass
        
        def rollback(self):
            pass
        
        def close(self):
            pass
        
        def query(self, model):
            return MockQuery(self.data.values())
    
    class MockQuery:
        def __init__(self, data):
            self.data = list(data)
        
        def filter(self, *args):
            return self
        
        def first(self):
            return self.data[0] if self.data else None
        
        def all(self):
            return self.data
        
        def count(self):
            return len(self.data)
    
    return MockSession()


@pytest.fixture
def mock_ml_service():
    """Mock ML service for testing"""
    class MockMLService:
        def __init__(self):
            self.is_trained = True
        
        async def predict_fraud_risk(self, transaction):
            # Simple mock prediction based on amount
            if transaction.amount > 1000:
                return 0.8
            elif transaction.amount > 500:
                return 0.6
            else:
                return 0.3
        
        async def get_model_performance(self):
            return {
                "accuracy": 0.94,
                "precision": 0.87,
                "recall": 0.82,
                "f1_score": 0.84
            }
    
    return MockMLService()


@pytest.fixture
def mock_fraud_service():
    """Mock fraud detection service for testing"""
    class MockFraudService:
        def __init__(self):
            self.fraud_threshold = 0.7
            self.high_risk_threshold = 0.9
        
        async def analyze_transaction(self, transaction):
            from models.schemas import TransactionAnalysis, RiskAssessment
            
            risk_score = min(1.0, transaction.amount / 1000.0)
            
            risk_assessment = RiskAssessment(
                transaction_id=transaction.transaction_id,
                risk_score=risk_score,
                risk_factors=["amount_anomaly"] if risk_score > 0.5 else [],
                confidence=0.85,
                recommendation="BLOCK" if risk_score > 0.9 else "REVIEW" if risk_score > 0.7 else "APPROVE"
            )
            
            return TransactionAnalysis(
                transaction_id=transaction.transaction_id,
                analysis_timestamp=datetime.now(),
                risk_assessment=risk_assessment,
                velocity_check={},
                pattern_matches=[],
                final_decision="BLOCKED" if risk_score > 0.9 else "FLAGGED" if risk_score > 0.7 else "APPROVED",
                confidence_score=0.85
            )
        
        async def get_daily_metrics(self):
            return {
                "transactions_today": 1247,
                "fraud_detected": 23,
                "amount_blocked": 45670.50
            }
    
    return MockFraudService()


# Test configuration
pytest_plugins = []

# Async test configuration
def pytest_configure(config):
    """Configure pytest for async testing"""
    config.addinivalue_line(
        "markers", "asyncio: mark test as async"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to handle async tests"""
    for item in items:
        if asyncio.iscoroutinefunction(item.function):
            item.add_marker(pytest.mark.asyncio)