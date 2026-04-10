"""
Train XGBoost Churn Prediction Model
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import numpy as np
import pandas as pd

class Command(BaseCommand):
    help = 'Train XGBoost churn prediction model'
    
    def handle(self, *args, **options):
        self.stdout.write('Installing xgboost...')
        
        try:
            import xgboost as xgb
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import roc_auc_score, classification_report
        except ImportError:
            self.stdout.write(self.style.ERROR(
                'xgboost not installed. Run: pip install xgboost scikit-learn'
            ))
            return
        
        self.stdout.write(self.style.SUCCESS('\n=== Training Churn Model ===\n'))
        
        # Extract features
        self.stdout.write('Extracting features...')
        features_df = self._extract_features()
        
        if len(features_df) < 50:
            self.stdout.write(self.style.WARNING(
                f'Insufficient data: {len(features_df)} samples. Need 50+ for training.'
            ))
            return
        
        self.stdout.write(f'Extracted {len(features_df)} customer records')
        
        # Prepare data
        X = features_df.drop(['customer_id', 'churned'], axis=1)
        y = features_df['churned']
        
        # Split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, stratify=y, random_state=42
        )
        
        self.stdout.write(f'Train: {len(X_train)}, Test: {len(X_test)}')
        
        # Train model
        self.stdout.write('Training XGBoost model...')
        
        scale_pos_weight = len(y_train[y_train==0]) / max(len(y_train[y_train==1]), 1)
        
        model = xgb.XGBClassifier(
            scale_pos_weight=scale_pos_weight,
            max_depth=6,
            learning_rate=0.1,
            n_estimators=100,
            eval_metric='auc',
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred_proba = model.predict_proba(X_test)[:, 1]
        auc_score = roc_auc_score(y_test, y_pred_proba)
        
        self.stdout.write(f'\nAUC Score: {auc_score:.3f}')
        
        if auc_score < 0.75:
            self.stdout.write(self.style.WARNING(
                f'Model AUC {auc_score:.3f} < 0.75 threshold. Not deploying.'
            ))
            return
        
        # Save model
        import joblib
        import os
        
        model_dir = '/home/ghost/Desktop/TeralinkxV3/teralinkx/models'
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = f'{model_dir}/churn_model_v1.pkl'
        joblib.dump(model, model_path)
        
        # Register in database
        from finance.models import MLModel
        
        ml_model = MLModel.objects.create(
            name='churn_prediction',
            version='v1',
            model_type='classification',
            use_case='churn_prediction',
            model_file_path=model_path,
            auc_roc=auc_score,
            training_data_size=len(X_train),
            training_date=timezone.now(),
            status='active',
            is_active=True,
            fallback_strategy='rule_based',
            feature_importance=dict(zip(X.columns, model.feature_importances_.tolist()))
        )
        
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Model trained and deployed\n'
            f'  AUC: {auc_score:.3f}\n'
            f'  Path: {model_path}\n'
            f'  Model ID: {ml_model.id}\n'
        ))
    
    def _extract_features(self):
        """Extract customer features for training"""
        from users.models import ClientH
        from finance.models import PaymentTransaction
        
        customers = ClientH.objects.all()
        data = []
        
        for customer in customers:
            # Calculate features
            days_inactive = self._get_days_inactive(customer)
            support_tickets = 0  # TODO: Implement
            late_payments = self._get_late_payments(customer)
            downgrades = 0  # TODO: Implement
            
            # Label: churned if inactive 60+ days
            churned = 1 if days_inactive and days_inactive > 60 else 0
            
            data.append({
                'customer_id': customer.id,
                'days_since_last_session': days_inactive or 0,
                'support_tickets_90d': support_tickets,
                'late_payments_count': late_payments,
                'package_downgrades_count': downgrades,
                'churned': churned
            })
        
        return pd.DataFrame(data)
    
    def _get_days_inactive(self, customer):
        """Get days since last payment"""
        from finance.models import PaymentTransaction
        
        last_payment = PaymentTransaction.objects.filter(
            user=customer
        ).order_by('-created_at').first()
        
        if last_payment:
            return (timezone.now() - last_payment.created_at).days
        return None
    
    def _get_late_payments(self, customer):
        """Count late payments"""
        # Simplified: count all payments as proxy
        from finance.models import PaymentTransaction
        return PaymentTransaction.objects.filter(user=customer).count()
