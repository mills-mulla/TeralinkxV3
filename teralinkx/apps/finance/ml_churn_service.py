"""
ML Churn Prediction Service
"""
import joblib
import numpy as np
from finance.models import MLModel, ChurnPrediction


class MLChurnPredictor:
    """ML-based churn prediction using trained XGBoost model"""
    
    def __init__(self):
        self.model = None
        self.ml_model_record = None
        self._load_model()
    
    def _load_model(self):
        """Load active ML model"""
        try:
            self.ml_model_record = MLModel.get_active_model('churn_prediction')
            if self.ml_model_record:
                self.model = joblib.load(self.ml_model_record.model_file_path)
        except Exception:
            self.model = None
    
    def predict(self, customer):
        """Predict churn probability for customer"""
        if not self.model:
            return None
        
        try:
            features = self._extract_features(customer)
            features_array = np.array([list(features.values())])
            
            proba = self.model.predict_proba(features_array)[0][1]
            
            return {
                'churn_score': float(proba),
                'features': features,
                'model_version': self.ml_model_record.version
            }
        except Exception:
            return None
    
    def _extract_features(self, customer):
        """Extract features for prediction"""
        from finance.models import PaymentTransaction
        from django.utils import timezone
        
        # Days since last payment
        last_payment = PaymentTransaction.objects.filter(
            user=customer
        ).order_by('-created_at').first()
        
        days_inactive = 0
        if last_payment:
            days_inactive = (timezone.now() - last_payment.created_at).days
        
        # Late payments count
        late_payments = PaymentTransaction.objects.filter(user=customer).count()
        
        return {
            'days_since_last_session': days_inactive,
            'support_tickets_90d': 0,
            'late_payments_count': late_payments,
            'package_downgrades_count': 0
        }
    
    def is_available(self):
        """Check if ML model is available"""
        return self.model is not None


def predict_churn_ml(customer):
    """Predict churn using ML model with fallback to rules"""
    predictor = MLChurnPredictor()
    
    if predictor.is_available():
        result = predictor.predict(customer)
        if result:
            return result['churn_score'], 'ml_model'
    
    # Fallback to rule-based
    score, _ = ChurnPrediction.calculate_rule_based_score(customer)
    return score, 'rule_based'
