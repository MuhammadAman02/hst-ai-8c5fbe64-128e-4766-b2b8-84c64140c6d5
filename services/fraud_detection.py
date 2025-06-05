"""
Core fraud detection service
"""
import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import numpy as np
from models.schemas import Transaction, FraudAlert, RiskAssessment, TransactionAnalysis
from services.ml_models import MLModelService
from core.utils import calculate_distance, is_business_hours, Timer


class FraudDetectionService:
    """Core fraud detection service with ML-powered analysis"""
    
    def __init__(self):
        self.ml_service = MLModelService()
        self.fraud_threshold = 0.7
        self.high_risk_threshold = 0.9
        
        # Risk factors and their weights
        self.risk_factors = {
            'amount_anomaly': 0.25,
            'velocity_check': 0.20,
            'location_anomaly': 0.15,
            'time_anomaly': 0.15,
            'merchant_risk': 0.10,
            'behavioral_pattern': 0.15
        }
    
    async def analyze_transaction(self, transaction: Transaction) -> TransactionAnalysis:
        """Comprehensive transaction analysis for fraud detection"""
        with Timer(f"Fraud analysis for transaction {transaction.transaction_id}"):
            # Parallel analysis of different risk factors
            tasks = [
                self._check_amount_anomaly(transaction),
                self._check_velocity_patterns(transaction),
                self._check_location_anomaly(transaction),
                self._check_time_patterns(transaction),
                self._check_merchant_risk(transaction),
                self._check_behavioral_patterns(transaction)
            ]
            
            risk_scores = await asyncio.gather(*tasks)
            
            # Calculate weighted risk score
            total_risk = sum(
                score * weight for score, weight in zip(risk_scores, self.risk_factors.values())
            )
            
            # Get ML model prediction
            ml_risk_score = await self.ml_service.predict_fraud_risk(transaction)
            
            # Combine rule-based and ML scores
            final_risk_score = (total_risk * 0.6) + (ml_risk_score * 0.4)
            
            # Generate risk assessment
            risk_assessment = RiskAssessment(
                transaction_id=transaction.transaction_id,
                risk_score=final_risk_score,
                risk_factors=self._identify_risk_factors(risk_scores),
                confidence=0.85,
                recommendation=self._get_recommendation(final_risk_score)
            )
            
            return TransactionAnalysis(
                transaction_id=transaction.transaction_id,
                analysis_timestamp=datetime.utcnow(),
                risk_assessment=risk_assessment,
                velocity_check=await self._get_velocity_details(transaction),
                pattern_matches=[],
                final_decision=self._make_decision(final_risk_score),
                confidence_score=0.85
            )
    
    async def _check_amount_anomaly(self, transaction: Transaction) -> float:
        """Check for unusual transaction amounts"""
        # Simulate historical spending analysis
        await asyncio.sleep(0.1)  # Simulate processing time
        
        # Mock logic: flag amounts significantly higher than usual
        if transaction.amount > 1000:
            return 0.8
        elif transaction.amount > 500:
            return 0.5
        elif transaction.amount < 1:
            return 0.7  # Micro-transactions can be suspicious
        else:
            return 0.2
    
    async def _check_velocity_patterns(self, transaction: Transaction) -> float:
        """Check transaction velocity and frequency patterns"""
        await asyncio.sleep(0.1)
        
        # Mock velocity check - in production, query recent transactions
        # Simulate finding multiple transactions in short time
        velocity_risk = random.uniform(0.1, 0.6)
        return velocity_risk
    
    async def _check_location_anomaly(self, transaction: Transaction) -> float:
        """Check for unusual transaction locations"""
        await asyncio.sleep(0.1)
        
        # Mock geolocation analysis
        high_risk_locations = ["Unknown", "Foreign", "High-Risk-Area"]
        if any(location in transaction.location for location in high_risk_locations):
            return 0.9
        
        # Check for impossible travel (transactions too far apart in short time)
        return random.uniform(0.1, 0.4)
    
    async def _check_time_patterns(self, transaction: Transaction) -> float:
        """Check for unusual transaction timing"""
        await asyncio.sleep(0.05)
        
        # Higher risk for transactions outside business hours
        if not is_business_hours(transaction.timestamp):
            return 0.6
        
        # Check for unusual patterns (e.g., exactly on the hour)
        if transaction.timestamp.minute == 0 and transaction.timestamp.second == 0:
            return 0.4
        
        return 0.1
    
    async def _check_merchant_risk(self, transaction: Transaction) -> float:
        """Check merchant risk profile"""
        await asyncio.sleep(0.05)
        
        # Mock merchant risk database
        high_risk_merchants = ["Unknown Merchant", "Cash Advance", "Gambling"]
        medium_risk_merchants = ["Online Store", "Gas Station"]
        
        if any(merchant in transaction.merchant for merchant in high_risk_merchants):
            return 0.8
        elif any(merchant in transaction.merchant for merchant in medium_risk_merchants):
            return 0.4
        else:
            return 0.1
    
    async def _check_behavioral_patterns(self, transaction: Transaction) -> float:
        """Check for unusual behavioral patterns"""
        await asyncio.sleep(0.1)
        
        # Mock behavioral analysis
        # In production, this would analyze user's historical behavior
        return random.uniform(0.1, 0.5)
    
    def _identify_risk_factors(self, risk_scores: List[float]) -> List[str]:
        """Identify which risk factors contributed to the score"""
        factors = []
        factor_names = list(self.risk_factors.keys())
        
        for i, score in enumerate(risk_scores):
            if score > 0.5:
                factors.append(factor_names[i])
        
        return factors
    
    def _get_recommendation(self, risk_score: float) -> str:
        """Get recommendation based on risk score"""
        if risk_score >= self.high_risk_threshold:
            return "BLOCK_TRANSACTION"
        elif risk_score >= self.fraud_threshold:
            return "MANUAL_REVIEW"
        else:
            return "APPROVE"
    
    def _make_decision(self, risk_score: float) -> str:
        """Make final decision on transaction"""
        if risk_score >= self.high_risk_threshold:
            return "BLOCKED"
        elif risk_score >= self.fraud_threshold:
            return "FLAGGED"
        else:
            return "APPROVED"
    
    async def _get_velocity_details(self, transaction: Transaction) -> Dict:
        """Get detailed velocity check information"""
        return {
            "transactions_last_hour": random.randint(0, 5),
            "transactions_last_day": random.randint(5, 20),
            "total_amount_last_hour": random.uniform(0, 1000),
            "average_transaction_amount": random.uniform(50, 200),
            "velocity_score": random.uniform(0.1, 0.8)
        }
    
    async def get_daily_metrics(self) -> Dict:
        """Get daily fraud detection metrics"""
        return {
            "transactions_today": 1247,
            "fraud_detected": 23,
            "amount_blocked": 45670.50,
            "false_positives": 3,
            "accuracy_rate": 0.97,
            "processing_time_avg": 0.15
        }
    
    async def get_realtime_data(self) -> pd.DataFrame:
        """Generate real-time monitoring data"""
        # Generate sample real-time data for the last 30 minutes
        timestamps = [datetime.now() - timedelta(minutes=x) for x in range(30, 0, -1)]
        
        data = {
            'timestamp': timestamps,
            'transaction_count': [random.randint(15, 45) for _ in range(30)],
            'fraud_score': [random.uniform(0.1, 0.8) for _ in range(30)]
        }
        
        return pd.DataFrame(data)
    
    async def get_recent_transactions(self) -> List[Dict]:
        """Get recent transactions with risk scores"""
        merchants = ["Tesco", "SuperValu", "Amazon", "PayPal", "Starbucks", "McDonald's"]
        locations = ["Dublin", "Cork", "Galway", "Limerick"]
        
        transactions = []
        for i in range(10):
            risk_score = random.uniform(0.1, 0.95)
            transactions.append({
                "transaction_id": f"TXN{1000 + i}",
                "amount": round(random.uniform(5.0, 500.0), 2),
                "merchant": random.choice(merchants),
                "card_last4": f"{random.randint(1000, 9999)}",
                "location": random.choice(locations),
                "timestamp": (datetime.now() - timedelta(minutes=random.randint(1, 60))).strftime("%H:%M"),
                "risk_score": risk_score
            })
        
        return sorted(transactions, key=lambda x: x['risk_score'], reverse=True)
    
    async def get_active_alerts(self) -> List[Dict]:
        """Get active fraud alerts"""
        alerts = []
        for i in range(3):
            alerts.append({
                "alert_id": f"ALT{100 + i}",
                "transaction_id": f"TXN{2000 + i}",
                "amount": round(random.uniform(500.0, 2000.0), 2),
                "card_last4": f"{random.randint(1000, 9999)}",
                "risk_score": round(random.uniform(0.8, 0.99), 2),
                "alert_type": "High Risk Transaction",
                "created_at": datetime.now() - timedelta(minutes=random.randint(5, 60))
            })
        
        return alerts
    
    async def get_risk_distribution(self) -> Dict[str, int]:
        """Get risk distribution for the last 24 hours"""
        return {
            "Low Risk": 1156,
            "Medium Risk": 68,
            "High Risk": 23
        }
    
    async def create_fraud_alert(self, transaction: Transaction, risk_score: float) -> FraudAlert:
        """Create a fraud alert for high-risk transactions"""
        alert = FraudAlert(
            transaction_id=transaction.transaction_id,
            alert_type="High Risk Transaction",
            risk_score=risk_score,
            description=f"Transaction flagged with risk score {risk_score:.2f}",
            created_at=datetime.utcnow()
        )
        
        # In production, save to database
        return alert
    
    async def investigate_transaction(self, transaction_id: str) -> Dict:
        """Investigate a specific transaction"""
        # Mock investigation results
        return {
            "transaction_id": transaction_id,
            "investigation_status": "IN_PROGRESS",
            "assigned_analyst": "John Doe",
            "evidence_collected": [
                "IP address analysis",
                "Device fingerprinting",
                "Behavioral pattern analysis"
            ],
            "recommendation": "Continue monitoring",
            "confidence": 0.75
        }
    
    async def block_transaction(self, transaction_id: str) -> Dict:
        """Block a suspicious transaction"""
        # Mock blocking process
        return {
            "transaction_id": transaction_id,
            "status": "BLOCKED",
            "blocked_at": datetime.utcnow(),
            "reason": "High fraud risk detected",
            "blocked_by": "Automated System"
        }