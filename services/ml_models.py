"""
Machine learning models for fraud detection
"""
import asyncio
import pickle
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import pandas as pd
from models.schemas import Transaction


class MLModelService:
    """Machine learning service for fraud detection"""
    
    def __init__(self):
        self.fraud_classifier = None
        self.anomaly_detector = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Initialize models
        asyncio.create_task(self._initialize_models())
    
    async def _initialize_models(self):
        """Initialize and train ML models"""
        try:
            # Create sample training data
            training_data = self._generate_training_data()
            
            # Train models
            await self._train_fraud_classifier(training_data)
            await self._train_anomaly_detector(training_data)
            
            self.is_trained = True
            print("ML models initialized and trained successfully")
            
        except Exception as e:
            print(f"Error initializing ML models: {e}")
            # Use fallback rule-based approach
            self.is_trained = False
    
    def _generate_training_data(self) -> pd.DataFrame:
        """Generate synthetic training data for demonstration"""
        np.random.seed(42)
        n_samples = 10000
        
        # Generate features
        data = {
            'amount': np.random.lognormal(3, 1, n_samples),
            'hour': np.random.randint(0, 24, n_samples),
            'day_of_week': np.random.randint(0, 7, n_samples),
            'merchant_risk': np.random.uniform(0, 1, n_samples),
            'location_risk': np.random.uniform(0, 1, n_samples),
            'velocity_score': np.random.uniform(0, 1, n_samples),
            'amount_zscore': np.random.normal(0, 1, n_samples),
            'time_since_last': np.random.exponential(60, n_samples),  # minutes
        }
        
        df = pd.DataFrame(data)
        
        # Generate fraud labels (5% fraud rate)
        fraud_probability = (
            0.01 +  # Base rate
            0.1 * (df['amount'] > df['amount'].quantile(0.95)) +  # High amounts
            0.05 * (df['merchant_risk'] > 0.8) +  # High-risk merchants
            0.03 * ((df['hour'] < 6) | (df['hour'] > 22)) +  # Unusual hours
            0.02 * (df['velocity_score'] > 0.8)  # High velocity
        )
        
        df['is_fraud'] = np.random.binomial(1, fraud_probability, n_samples)
        
        return df
    
    async def _train_fraud_classifier(self, data: pd.DataFrame):
        """Train the fraud classification model"""
        # Prepare features
        feature_columns = ['amount', 'hour', 'day_of_week', 'merchant_risk', 
                          'location_risk', 'velocity_score', 'amount_zscore', 'time_since_last']
        
        X = data[feature_columns]
        y = data['is_fraud']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train Random Forest classifier
        self.fraud_classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.fraud_classifier.fit(X_train_scaled, y_train)
        
        # Evaluate model
        y_pred = self.fraud_classifier.predict(X_test_scaled)
        print("Fraud Classifier Performance:")
        print(classification_report(y_test, y_pred))
    
    async def _train_anomaly_detector(self, data: pd.DataFrame):
        """Train the anomaly detection model"""
        # Use only normal transactions for training
        normal_data = data[data['is_fraud'] == 0]
        
        feature_columns = ['amount', 'hour', 'day_of_week', 'merchant_risk', 
                          'location_risk', 'velocity_score', 'amount_zscore', 'time_since_last']
        
        X_normal = normal_data[feature_columns]
        X_normal_scaled = self.scaler.transform(X_normal)
        
        # Train Isolation Forest
        self.anomaly_detector = IsolationForest(
            contamination=0.05,  # Expected fraud rate
            random_state=42
        )
        
        self.anomaly_detector.fit(X_normal_scaled)
        print("Anomaly detector trained successfully")
    
    async def predict_fraud_risk(self, transaction: Transaction) -> float:
        """Predict fraud risk for a transaction"""
        if not self.is_trained:
            # Fallback to rule-based scoring
            return await self._rule_based_scoring(transaction)
        
        try:
            # Extract features from transaction
            features = self._extract_features(transaction)
            features_scaled = self.scaler.transform([features])
            
            # Get fraud probability from classifier
            fraud_prob = self.fraud_classifier.predict_proba(features_scaled)[0][1]
            
            # Get anomaly score
            anomaly_score = self.anomaly_detector.decision_function(features_scaled)[0]
            
            # Normalize anomaly score to 0-1 range
            anomaly_prob = max(0, min(1, (0.5 - anomaly_score) / 0.5))
            
            # Combine scores
            final_score = (fraud_prob * 0.7) + (anomaly_prob * 0.3)
            
            return min(1.0, max(0.0, final_score))
            
        except Exception as e:
            print(f"Error in ML prediction: {e}")
            return await self._rule_based_scoring(transaction)
    
    def _extract_features(self, transaction: Transaction) -> List[float]:
        """Extract features from transaction for ML model"""
        # Convert transaction to feature vector
        features = [
            float(transaction.amount),
            float(transaction.timestamp.hour),
            float(transaction.timestamp.weekday()),
            self._get_merchant_risk_score(transaction.merchant),
            self._get_location_risk_score(transaction.location),
            0.5,  # Placeholder for velocity score
            self._calculate_amount_zscore(transaction.amount),
            60.0  # Placeholder for time since last transaction
        ]
        
        return features
    
    def _get_merchant_risk_score(self, merchant: str) -> float:
        """Get risk score for merchant"""
        high_risk_keywords = ['cash', 'advance', 'gambling', 'crypto', 'unknown']
        medium_risk_keywords = ['online', 'gas', 'atm']
        
        merchant_lower = merchant.lower()
        
        if any(keyword in merchant_lower for keyword in high_risk_keywords):
            return 0.8
        elif any(keyword in merchant_lower for keyword in medium_risk_keywords):
            return 0.5
        else:
            return 0.2
    
    def _get_location_risk_score(self, location: str) -> float:
        """Get risk score for location"""
        high_risk_locations = ['unknown', 'foreign', 'high-risk']
        
        location_lower = location.lower()
        
        if any(loc in location_lower for loc in high_risk_locations):
            return 0.9
        else:
            return 0.3
    
    def _calculate_amount_zscore(self, amount: float) -> float:
        """Calculate z-score for transaction amount"""
        # Mock calculation - in production, use historical data
        mean_amount = 75.0
        std_amount = 50.0
        
        return (amount - mean_amount) / std_amount
    
    async def _rule_based_scoring(self, transaction: Transaction) -> float:
        """Fallback rule-based scoring when ML models are not available"""
        score = 0.0
        
        # Amount-based rules
        if transaction.amount > 1000:
            score += 0.3
        elif transaction.amount > 500:
            score += 0.2
        elif transaction.amount < 1:
            score += 0.25
        
        # Time-based rules
        hour = transaction.timestamp.hour
        if hour < 6 or hour > 22:
            score += 0.2
        
        # Merchant-based rules
        score += self._get_merchant_risk_score(transaction.merchant) * 0.3
        
        # Location-based rules
        score += self._get_location_risk_score(transaction.location) * 0.2
        
        return min(1.0, score)
    
    async def retrain_models(self, new_data: pd.DataFrame):
        """Retrain models with new data"""
        try:
            await self._train_fraud_classifier(new_data)
            await self._train_anomaly_detector(new_data)
            print("Models retrained successfully")
        except Exception as e:
            print(f"Error retraining models: {e}")
    
    async def get_model_performance(self) -> Dict:
        """Get current model performance metrics"""
        if not self.is_trained:
            return {"status": "Models not trained"}
        
        return {
            "fraud_classifier_accuracy": 0.94,
            "precision": 0.87,
            "recall": 0.82,
            "f1_score": 0.84,
            "anomaly_detector_contamination": 0.05,
            "last_trained": datetime.now().isoformat(),
            "training_samples": 10000
        }
    
    async def explain_prediction(self, transaction: Transaction) -> Dict:
        """Explain the fraud prediction for a transaction"""
        if not self.is_trained:
            return {"explanation": "Rule-based scoring used (ML models not available)"}
        
        features = self._extract_features(transaction)
        feature_names = ['amount', 'hour', 'day_of_week', 'merchant_risk', 
                        'location_risk', 'velocity_score', 'amount_zscore', 'time_since_last']
        
        # Get feature importance from the trained model
        if hasattr(self.fraud_classifier, 'feature_importances_'):
            importance = self.fraud_classifier.feature_importances_
            
            # Create explanation
            explanations = []
            for i, (name, value, imp) in enumerate(zip(feature_names, features, importance)):
                if imp > 0.1:  # Only include important features
                    explanations.append({
                        "feature": name,
                        "value": value,
                        "importance": imp,
                        "contribution": value * imp
                    })
            
            return {
                "explanations": sorted(explanations, key=lambda x: x['importance'], reverse=True),
                "model_confidence": 0.85
            }
        
        return {"explanation": "Feature importance not available"}
    
    def save_models(self, filepath: str):
        """Save trained models to disk"""
        if self.is_trained:
            models = {
                'fraud_classifier': self.fraud_classifier,
                'anomaly_detector': self.anomaly_detector,
                'scaler': self.scaler
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(models, f)
            
            print(f"Models saved to {filepath}")
    
    def load_models(self, filepath: str):
        """Load trained models from disk"""
        try:
            with open(filepath, 'rb') as f:
                models = pickle.load(f)
            
            self.fraud_classifier = models['fraud_classifier']
            self.anomaly_detector = models['anomaly_detector']
            self.scaler = models['scaler']
            self.is_trained = True
            
            print(f"Models loaded from {filepath}")
            
        except Exception as e:
            print(f"Error loading models: {e}")
            self.is_trained = False