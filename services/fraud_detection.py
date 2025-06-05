"""
Irish Bank Fraud Detection System
Core fraud detection service with ML models
"""
import asyncio
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score
import joblib
import os

from models.schemas import (
    Transaction, RiskAssessment, FraudAlert, TransactionAnalysis,
    RiskLevel, RiskFactor, AlertStatus, SystemMetrics
)

logger = logging.getLogger(__name__)

class FraudDetectionService:
    """Advanced fraud detection service with ML capabilities"""
    
    def __init__(self):
        self.rf_model = None
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.model_version = "1.0.0"
        self.feature_columns = [
            'amount', 'hour', 'day_of_week', 'merchant_risk_score',
            'velocity_1h', 'velocity_24h', 'amount_zscore', 'location_risk'
        ]
        self.is_trained = False
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models with default parameters"""
        try:
            self.rf_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
            self.isolation_forest = IsolationForest(
                contamination=0.1,
                random_state=42,
                n_jobs=-1
            )
            logger.info("ML models initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
            raise
    
    async def analyze_transaction(self, transaction: Transaction) -> TransactionAnalysis:
        """Analyze a transaction for fraud risk"""
        start_time = datetime.now()
        
        try:
            # Extract features
            features = await self._extract_features(transaction)
            
            # Calculate risk assessment
            risk_assessment = await self._assess_risk(transaction, features)
            
            # Generate alerts if needed
            alerts = await self._generate_alerts(transaction, risk_assessment)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(risk_assessment)
            
            processing_time = (datetime.now() - start_time).total_seconds() * 1000
            
            return TransactionAnalysis(
                transaction=transaction,
                risk_assessment=risk_assessment,
                alerts=alerts,
                recommendations=recommendations,
                processing_time_ms=processing_time,
                analysis_timestamp=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Error analyzing transaction {transaction.id}: {e}")
            raise
    
    async def _extract_features(self, transaction: Transaction) -> Dict[str, float]:
        """Extract features from transaction for ML models"""
        try:
            features = {}
            
            # Basic transaction features
            features['amount'] = float(transaction.amount)
            features['hour'] = transaction.timestamp.hour
            features['day_of_week'] = transaction.timestamp.weekday()
            features['merchant_risk_score'] = transaction.merchant.risk_score
            
            # Velocity features (simulated for demo)
            features['velocity_1h'] = await self._calculate_velocity(transaction.user_id, hours=1)
            features['velocity_24h'] = await self._calculate_velocity(transaction.user_id, hours=24)
            
            # Amount analysis
            features['amount_zscore'] = await self._calculate_amount_zscore(transaction)
            
            # Location risk
            features['location_risk'] = await self._calculate_location_risk(transaction)
            
            return features
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return {}
    
    async def _calculate_velocity(self, user_id: str, hours: int) -> float:
        """Calculate transaction velocity for user (simulated)"""
        # In production, this would query the database
        # For demo, return simulated values
        base_velocity = np.random.exponential(2.0)
        return min(base_velocity, 10.0)  # Cap at 10 transactions
    
    async def _calculate_amount_zscore(self, transaction: Transaction) -> float:
        """Calculate amount z-score compared to user's history (simulated)"""
        # In production, this would analyze user's transaction history
        # For demo, return simulated z-score
        user_avg = np.random.normal(100, 50)  # Simulated user average
        user_std = np.random.normal(30, 10)   # Simulated user std dev
        
        if user_std <= 0:
            user_std = 1.0
            
        z_score = (transaction.amount - user_avg) / user_std
        return float(z_score)
    
    async def _calculate_location_risk(self, transaction: Transaction) -> float:
        """Calculate location-based risk score"""
        try:
            risk_score = 0.0
            
            # Country risk (Ireland = low risk)
            if transaction.location.country.upper() == 'IRL':
                risk_score += 0.1
            elif transaction.location.country.upper() in ['GBR', 'USA', 'CAN', 'AUS']:
                risk_score += 0.2
            else:
                risk_score += 0.5
            
            # IP address analysis (simulated)
            if transaction.location.ip_address:
                # In production, this would check IP reputation databases
                risk_score += np.random.uniform(0.0, 0.3)
            
            return min(risk_score, 1.0)
            
        except Exception as e:
            logger.error(f"Error calculating location risk: {e}")
            return 0.5  # Default medium risk
    
    async def _assess_risk(self, transaction: Transaction, features: Dict[str, float]) -> RiskAssessment:
        """Assess overall risk for the transaction"""
        try:
            risk_factors = []
            overall_score = 0.0
            
            # Amount risk
            if features.get('amount', 0) > 1000:
                factor = RiskFactor(
                    name="High Amount",
                    description=f"Transaction amount €{transaction.amount:.2f} exceeds normal threshold",
                    weight=0.3,
                    value=min(features.get('amount', 0) / 5000, 1.0),
                    threshold=0.2
                )
                risk_factors.append(factor)
                overall_score += factor.weight * factor.value
            
            # Velocity risk
            velocity_1h = features.get('velocity_1h', 0)
            if velocity_1h > 3:
                factor = RiskFactor(
                    name="High Velocity",
                    description=f"{velocity_1h:.1f} transactions in last hour",
                    weight=0.25,
                    value=min(velocity_1h / 10, 1.0),
                    threshold=0.3
                )
                risk_factors.append(factor)
                overall_score += factor.weight * factor.value
            
            # Time-based risk
            hour = features.get('hour', 12)
            if hour < 6 or hour > 23:
                factor = RiskFactor(
                    name="Unusual Time",
                    description=f"Transaction at {hour:02d}:xx outside normal hours",
                    weight=0.15,
                    value=0.7,
                    threshold=0.5
                )
                risk_factors.append(factor)
                overall_score += factor.weight * factor.value
            
            # Location risk
            location_risk = features.get('location_risk', 0)
            if location_risk > 0.3:
                factor = RiskFactor(
                    name="Location Risk",
                    description="Transaction from high-risk location",
                    weight=0.2,
                    value=location_risk,
                    threshold=0.3
                )
                risk_factors.append(factor)
                overall_score += factor.weight * factor.value
            
            # Merchant risk
            merchant_risk = transaction.merchant.risk_score
            if merchant_risk > 0.4:
                factor = RiskFactor(
                    name="Merchant Risk",
                    description=f"High-risk merchant: {transaction.merchant.name}",
                    weight=0.1,
                    value=merchant_risk,
                    threshold=0.4
                )
                risk_factors.append(factor)
                overall_score += factor.weight * factor.value
            
            # Determine risk level
            if overall_score >= 0.7:
                risk_level = RiskLevel.CRITICAL
            elif overall_score >= 0.5:
                risk_level = RiskLevel.HIGH
            elif overall_score >= 0.3:
                risk_level = RiskLevel.MEDIUM
            else:
                risk_level = RiskLevel.LOW
            
            # ML model prediction (if trained)
            model_confidence = 0.85  # Simulated confidence
            if self.is_trained and len(features) >= len(self.feature_columns):
                try:
                    feature_vector = [features.get(col, 0) for col in self.feature_columns]
                    feature_vector = np.array(feature_vector).reshape(1, -1)
                    
                    # Scale features
                    feature_vector_scaled = self.scaler.transform(feature_vector)
                    
                    # Get predictions
                    rf_prob = self.rf_model.predict_proba(feature_vector_scaled)[0][1]
                    isolation_score = self.isolation_forest.decision_function(feature_vector_scaled)[0]
                    
                    # Combine scores
                    ml_score = (rf_prob + max(0, -isolation_score)) / 2
                    overall_score = (overall_score + ml_score) / 2
                    model_confidence = 0.95
                    
                except Exception as e:
                    logger.warning(f"ML prediction failed: {e}")
            
            return RiskAssessment(
                transaction_id=transaction.id,
                overall_score=min(overall_score, 1.0),
                risk_level=risk_level,
                factors=risk_factors,
                model_confidence=model_confidence,
                assessment_time=datetime.now(),
                model_version=self.model_version
            )
            
        except Exception as e:
            logger.error(f"Error assessing risk: {e}")
            # Return default medium risk assessment
            return RiskAssessment(
                transaction_id=transaction.id,
                overall_score=0.5,
                risk_level=RiskLevel.MEDIUM,
                factors=[],
                model_confidence=0.5,
                assessment_time=datetime.now(),
                model_version=self.model_version
            )
    
    async def _generate_alerts(self, transaction: Transaction, risk_assessment: RiskAssessment) -> List[FraudAlert]:
        """Generate fraud alerts based on risk assessment"""
        alerts = []
        
        try:
            # Generate alert for high/critical risk transactions
            if risk_assessment.risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]:
                alert_id = f"ALERT_{transaction.id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                alert = FraudAlert(
                    id=alert_id,
                    transaction_id=transaction.id,
                    alert_type="FRAUD_RISK",
                    severity=risk_assessment.risk_level,
                    status=AlertStatus.ACTIVE,
                    created_at=datetime.now(),
                    title=f"{risk_assessment.risk_level.value.title()} Risk Transaction Detected",
                    description=f"Transaction €{transaction.amount:.2f} to {transaction.merchant.name} "
                               f"has risk score {risk_assessment.overall_score:.2f}",
                    risk_score=risk_assessment.overall_score,
                    triggered_rules=[factor.name for factor in risk_assessment.factors]
                )
                alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating alerts: {e}")
            return []
    
    async def _generate_recommendations(self, risk_assessment: RiskAssessment) -> List[str]:
        """Generate recommendations based on risk assessment"""
        recommendations = []
        
        try:
            if risk_assessment.risk_level == RiskLevel.CRITICAL:
                recommendations.extend([
                    "Block transaction immediately",
                    "Contact customer for verification",
                    "Review recent account activity",
                    "Consider temporary card suspension"
                ])
            elif risk_assessment.risk_level == RiskLevel.HIGH:
                recommendations.extend([
                    "Hold transaction for manual review",
                    "Send SMS verification to customer",
                    "Monitor account for additional suspicious activity"
                ])
            elif risk_assessment.risk_level == RiskLevel.MEDIUM:
                recommendations.extend([
                    "Allow transaction with enhanced monitoring",
                    "Log for pattern analysis"
                ])
            else:
                recommendations.append("Process transaction normally")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return ["Process with standard monitoring"]
    
    async def train_models(self, transactions: List[Transaction]) -> Dict[str, float]:
        """Train ML models with historical transaction data"""
        try:
            if len(transactions) < 100:
                logger.warning("Insufficient data for training (minimum 100 transactions required)")
                return {"error": "Insufficient training data"}
            
            # Prepare training data
            features_list = []
            labels = []
            
            for transaction in transactions:
                features = await self._extract_features(transaction)
                feature_vector = [features.get(col, 0) for col in self.feature_columns]
                features_list.append(feature_vector)
                labels.append(1 if transaction.is_fraud else 0)
            
            X = np.array(features_list)
            y = np.array(labels)
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train Random Forest
            self.rf_model.fit(X_train_scaled, y_train)
            
            # Train Isolation Forest (unsupervised)
            self.isolation_forest.fit(X_train_scaled)
            
            # Evaluate models
            rf_predictions = self.rf_model.predict(X_test_scaled)
            rf_probabilities = self.rf_model.predict_proba(X_test_scaled)[:, 1]
            
            # Calculate metrics
            from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
            
            accuracy = accuracy_score(y_test, rf_predictions)
            precision = precision_score(y_test, rf_predictions)
            recall = recall_score(y_test, rf_predictions)
            f1 = f1_score(y_test, rf_predictions)
            auc = roc_auc_score(y_test, rf_probabilities)
            
            self.is_trained = True
            
            logger.info(f"Models trained successfully - Accuracy: {accuracy:.3f}, AUC: {auc:.3f}")
            
            return {
                "accuracy": accuracy,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "auc_roc": auc,
                "training_samples": len(X_train),
                "test_samples": len(X_test)
            }
            
        except Exception as e:
            logger.error(f"Error training models: {e}")
            return {"error": str(e)}
    
    async def get_system_metrics(self) -> SystemMetrics:
        """Get current system performance metrics"""
        try:
            # In production, these would be real metrics from database/monitoring
            return SystemMetrics(
                timestamp=datetime.now(),
                total_transactions=np.random.randint(1000, 5000),
                fraud_detected=np.random.randint(10, 50),
                false_positives=np.random.randint(2, 10),
                active_alerts=np.random.randint(5, 25),
                avg_processing_time_ms=np.random.uniform(50, 200),
                model_accuracy=0.95 if self.is_trained else 0.85,
                system_load=np.random.uniform(0.3, 0.8)
            )
            
        except Exception as e:
            logger.error(f"Error getting system metrics: {e}")
            return SystemMetrics(
                timestamp=datetime.now(),
                total_transactions=0,
                fraud_detected=0,
                false_positives=0,
                active_alerts=0,
                avg_processing_time_ms=0,
                model_accuracy=0,
                system_load=0
            )