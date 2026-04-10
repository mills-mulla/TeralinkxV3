from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

# Set default Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')

# Create Celery app instance
app = Celery('teralinkx')

# Load config from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks in Django apps
app.autodiscover_tasks()

# Finance app task schedules
app.conf.beat_schedule = {
    'refresh-kpi-snapshot': {
        'task': 'finance.refresh_kpi_snapshot',
        'schedule': 300.0,  # Every 5 minutes
    },
    'refresh-revenue-at-risk-cache': {
        'task': 'finance.refresh_revenue_at_risk_cache',
        'schedule': 600.0,  # Every 10 minutes
    },
    'generate-cash-flow-forecast': {
        'task': 'finance.generate_cash_flow_forecast',
        'schedule': crontab(hour=6, minute=0),  # Daily at 6am
    },
    'create-retention-tasks': {
        'task': 'finance.create_retention_tasks',
        'schedule': crontab(hour=7, minute=0),  # Daily at 7am
    },
    'monitor-retention-outcomes': {
        'task': 'finance.monitor_retention_outcomes',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8am
    },
    'generate-monthly-board-report': {
        'task': 'finance.generate_monthly_board_report',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),  # 1st of month at 6am
    },
}

# Finance app task routing
app.conf.task_routes = {
    'finance.*': {'queue': 'finance'},
}

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')