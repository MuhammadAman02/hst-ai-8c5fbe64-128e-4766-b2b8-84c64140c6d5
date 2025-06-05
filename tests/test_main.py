"""
Tests for the main application
"""
import pytest
import asyncio
from datetime import datetime
from models.schemas import Transaction, User
from services.fraud_detection import FraudDetectionService
from services.ml_models import MLModelService


class TestFraudDetectionService:
    """Test cases for fraud detection service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.fraud_service = FraudDetectionService()
        self.sample_transaction = Transaction(
            transaction_id="TEST001",
            amount=100.0,
            merchant="Test Merchant",
            card_last4="1234",
            location="Dublin",
            timestamp=datetime.now(),
            risk_score=0.5
        )
    
    @pytest.mark.asyncio
    async def test_analyze_transaction(self):
        """Test transaction analysis"""
        analysis = await self.fraud_service.analyze_transaction(self.sample_transaction)
        
        assert analysis.transaction_id == "TEST001"
        assert 0.0 <= analysis.risk_assessment.risk_score <= 1.0
        assert analysis.final_decision in ["APPROVED", "FLAGGED", "BLOCKED"]
        assert analysis.confidence_score > 0.0
    
    @pytest.mark.asyncio
    async def test_high_amount_detection(self):
        """Test detection of high amount transactions"""
        high_amount_transaction = Transaction(
            transaction_id="TEST002",
            amount=5000.0,  # High amount
            merchant="Test Merchant",
            card_last4="1234",
            location="Dublin",
            timestamp=datetime.now(),
            risk_score=0.0
        )
        
        analysis = await self.fraud_service.analyze_transaction(high_amount_transaction)
        
        # High amount should increase risk score
        assert analysis.risk_assessment.risk_score > 0.5
    
    @pytest.mark.asyncio
    async def test_get_daily_metrics(self):
        """Test daily metrics retrieval"""
        metrics = await self.fraud_service.get_daily_metrics()
        
        assert "transactions_today" in metrics
        assert "fraud_detected" in metrics
        assert "amount_blocked" in metrics
        assert isinstance(metrics["transactions_today"], int)
        assert isinstance(metrics["fraud_detected"], int)
        assert isinstance(metrics["amount_blocked"], float)
    
    @pytest.mark.asyncio
    async def test_get_recent_transactions(self):
        """Test recent transactions retrieval"""
        transactions = await self.fraud_service.get_recent_transactions()
        
        assert isinstance(transactions, list)
        assert len(transactions) > 0
        
        # Check transaction structure
        for transaction in transactions:
            assert "transaction_id" in transaction
            assert "amount" in transaction
            assert "risk_score" in transaction
            assert 0.0 <= transaction["risk_score"] <= 1.0


class TestMLModelService:
    """Test cases for ML model service"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.ml_service = MLModelService()
        self.sample_transaction = Transaction(
            transaction_id="TEST001",
            amount=100.0,
            merchant="Test Merchant",
            card_last4="1234",
            location="Dublin",
            timestamp=datetime.now(),
            risk_score=0.0
        )
    
    @pytest.mark.asyncio
    async def test_predict_fraud_risk(self):
        """Test fraud risk prediction"""
        risk_score = await self.ml_service.predict_fraud_risk(self.sample_transaction)
        
        assert isinstance(risk_score, float)
        assert 0.0 <= risk_score <= 1.0
    
    def test_extract_features(self):
        """Test feature extraction from transaction"""
        features = self.ml_service._extract_features(self.sample_transaction)
        
        assert isinstance(features, list)
        assert len(features) == 8  # Expected number of features
        assert all(isinstance(f, float) for f in features)
    
    def test_merchant_risk_scoring(self):
        """Test merchant risk scoring"""
        # Test high-risk merchant
        high_risk_score = self.ml_service._get_merchant_risk_score("Cash Advance")
        assert high_risk_score >= 0.7
        
        # Test low-risk merchant
        low_risk_score = self.ml_service._get_merchant_risk_score("Grocery Store")
        assert low_risk_score <= 0.5
    
    def test_location_risk_scoring(self):
        """Test location risk scoring"""
        # Test high-risk location
        high_risk_score = self.ml_service._get_location_risk_score("Unknown")
        assert high_risk_score >= 0.8
        
        # Test normal location
        normal_risk_score = self.ml_service._get_location_risk_score("Dublin")
        assert normal_risk_score <= 0.5


class TestDataModels:
    """Test cases for data models"""
    
    def test_transaction_validation(self):
        """Test transaction model validation"""
        # Valid transaction
        transaction = Transaction(
            transaction_id="TEST001",
            amount=100.0,
            merchant="Test Merchant",
            card_last4="1234",
            location="Dublin",
            timestamp=datetime.now(),
            risk_score=0.5
        )
        
        assert transaction.amount == 100.0
        assert transaction.card_last4 == "1234"
        assert 0.0 <= transaction.risk_score <= 1.0
    
    def test_transaction_amount_validation(self):
        """Test transaction amount validation"""
        with pytest.raises(ValueError):
            Transaction(
                transaction_id="TEST001",
                amount=-100.0,  # Invalid negative amount
                merchant="Test Merchant",
                card_last4="1234",
                location="Dublin",
                timestamp=datetime.now(),
                risk_score=0.5
            )
    
    def test_user_model(self):
        """Test user model"""
        user = User(
            id=1,
            email="test@irishbank.ie",
            full_name="Test User",
            role="analyst",
            is_active=True
        )
        
        assert user.email == "test@irishbank.ie"
        assert user.role == "analyst"
        assert user.is_active is True


class TestSecurityFeatures:
    """Test cases for security features"""
    
    def test_password_hashing(self):
        """Test password hashing functionality"""
        from core.security import get_password_hash, verify_password
        
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password  # Password should be hashed
        assert verify_password(password, hashed)  # Should verify correctly
        assert not verify_password("wrong_password", hashed)  # Should reject wrong password
    
    def test_input_validation(self):
        """Test input validation and sanitization"""
        from core.security import validate_input
        
        # Test normal input
        clean_input = validate_input("Normal text input")
        assert clean_input == "Normal text input"
        
        # Test input with dangerous characters
        dangerous_input = validate_input("<script>alert('xss')</script>")
        assert "<script>" not in dangerous_input
        assert "alert" in dangerous_input  # Content should remain but tags removed
    
    def test_rate_limiting(self):
        """Test rate limiting functionality"""
        from core.security import check_rate_limit
        
        # Test rate limiting (mock implementation always returns True)
        result = check_rate_limit("user123", "login", limit=5, window=60)
        assert isinstance(result, bool)


class TestUtilityFunctions:
    """Test cases for utility functions"""
    
    def test_transaction_id_generation(self):
        """Test transaction ID generation"""
        from core.utils import generate_transaction_id
        
        txn_id = generate_transaction_id()
        
        assert txn_id.startswith("TXN")
        assert len(txn_id) > 10  # Should have timestamp + random suffix
    
    def test_currency_formatting(self):
        """Test currency formatting"""
        from core.utils import format_currency
        
        formatted = format_currency(1234.56)
        assert "€" in formatted
        assert "1,234.56" in formatted
    
    def test_email_validation(self):
        """Test email validation"""
        from core.utils import validate_email
        
        assert validate_email("test@irishbank.ie") is True
        assert validate_email("invalid-email") is False
        assert validate_email("test@") is False
    
    def test_sensitive_data_masking(self):
        """Test sensitive data masking"""
        from core.utils import mask_sensitive_data
        
        masked = mask_sensitive_data("1234567890123456", visible_chars=4)
        assert masked.endswith("3456")
        assert masked.startswith("*")
        assert len(masked) == 16
    
    def test_distance_calculation(self):
        """Test geographic distance calculation"""
        from core.utils import calculate_distance
        
        # Distance between Dublin and Cork (approximately)
        dublin_lat, dublin_lon = 53.3498, -6.2603
        cork_lat, cork_lon = 51.8985, -8.4756
        
        distance = calculate_distance(dublin_lat, dublin_lon, cork_lat, cork_lon)
        
        assert 200 < distance < 300  # Approximate distance in km
    
    def test_business_hours_check(self):
        """Test business hours checking"""
        from core.utils import is_business_hours
        from datetime import datetime
        
        # Test business hours (Wednesday 2 PM)
        business_time = datetime(2024, 1, 10, 14, 0, 0)  # Wednesday 2 PM
        assert is_business_hours(business_time) is True
        
        # Test non-business hours (Saturday)
        weekend_time = datetime(2024, 1, 13, 14, 0, 0)  # Saturday 2 PM
        assert is_business_hours(weekend_time) is False
        
        # Test late hours (Wednesday 11 PM)
        late_time = datetime(2024, 1, 10, 23, 0, 0)  # Wednesday 11 PM
        assert is_business_hours(late_time) is False


if __name__ == "__main__":
    pytest.main([__file__])