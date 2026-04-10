"""
Celery Beat Schedule Configuration
Add this to your teralinkx/celery.py file
"""

# Celery Beat Schedule for Smart Business Management
CELERY_BEAT_SCHEDULE = {
    # Retention Workflow (Phase 1.3)
    'create-retention-tasks-daily': {
        'task': 'finance.create_retention_tasks',
        'schedule': crontab(hour=7, minute=0),  # Daily at 7am
        'options': {'queue': 'default'}
    },
    'monitor-retention-outcomes-daily': {
        'task': 'finance.monitor_retention_outcomes',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8am
        'options': {'queue': 'default'}
    },
    
    # Revenue at Risk Dashboard (Phase 1.4)
    'refresh-revenue-at-risk-cache': {
        'task': 'finance.refresh_revenue_at_risk_cache',
        'schedule': 600.0,  # Every 10 minutes
        'options': {'queue': 'default'}
    },
    
    # KPI Refresh (Phase 4.1)
    'refresh-kpi-snapshot': {
        'task': 'finance.refresh_kpi_snapshot',
        'schedule': 300.0,  # Every 5 minutes
        'options': {'queue': 'default'}
    },
    
    # Cash Flow Forecasting (Phase 2.2)
    'generate-cash-flow-forecast-daily': {
        'task': 'finance.generate_cash_flow_forecast',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6am
        'options': {'queue': 'ml'}
    },
    
    # Churn Model Retraining (Phase 1.2)
    'retrain-churn-model-weekly': {
        'task': 'finance.retrain_churn_model',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),  # Monday 2am
        'options': {'queue': 'ml'}
    },
    
    # Transaction Queue Cleanup
    'cleanup-expired-transactions': {
        'task': 'finance.cleanup_expired_transactions',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3am
        'options': {'queue': 'default'}
    },
    
    # Board Report Generation (Phase 4.2)
    'generate-monthly-board-report': {
        'task': 'finance.generate_monthly_board_report',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),  # 1st of month at 6am
        'options': {'queue': 'default'}
    },
}

# Queue Configuration
CELERY_TASK_ROUTES = {
    'finance.refresh_churn_prediction': {'queue': 'ml'},
    'finance.retrain_churn_model': {'queue': 'ml'},
    'finance.generate_cash_flow_forecast': {'queue': 'ml'},
    'finance.process_invoice_ocr': {'queue': 'ocr'},
    'finance.check_fraud_correlation': {'queue': 'hids'},
    'finance.*': {'queue': 'default'},
}
