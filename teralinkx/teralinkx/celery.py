from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')

app = Celery('teralinkx')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

# ─── Queue routing ────────────────────────────────────────────────────────────
app.conf.task_routes = {
    # ML-heavy tasks → ml queue (2 workers, high memory)
    'finance.retrain_churn_model':          {'queue': 'ml'},
    'finance.refresh_churn_predictions_all': {'queue': 'ml'},
    'finance.refresh_churn_prediction':     {'queue': 'ml'},
    'finance.generate_cash_flow_forecast':  {'queue': 'ml'},

    # Notification tasks → notifications queue
    'finance.send_payment_reminders':       {'queue': 'notifications'},
    'finance.send_budget_alerts':           {'queue': 'notifications'},
    'finance.send_retention_sms':           {'queue': 'notifications'},

    # Cleanup tasks → cleanup queue (low priority)
    'finance.cleanup_kpi_snapshots':        {'queue': 'cleanup'},
    'finance.cleanup_expired_transactions': {'queue': 'cleanup'},
    'finance.refresh_timescale_aggregates': {'queue': 'cleanup'},

    # Everything else → default queue
    'finance.*':                            {'queue': 'default'},
    'sync.*':                               {'queue': 'default'},
}

# ─── Beat schedule ────────────────────────────────────────────────────────────
app.conf.beat_schedule = {

    # ── Every 5 minutes ──────────────────────────────────────────────────────
    'refresh-kpi-snapshot': {
        'task': 'finance.refresh_kpi_snapshot',
        'schedule': 300.0,
        'options': {'queue': 'default'}
    },

    # ── Every 10 minutes ─────────────────────────────────────────────────────
    'refresh-revenue-at-risk-cache': {
        'task': 'finance.refresh_revenue_at_risk_cache',
        'schedule': 600.0,
        'options': {'queue': 'default'}
    },

    # ── Hourly ───────────────────────────────────────────────────────────────
    'refresh-timescale-aggregates': {
        'task': 'finance.refresh_timescale_aggregates',
        'schedule': crontab(minute=0),
        'options': {'queue': 'cleanup'}
    },
    'update-exchange-rates': {
        'task': 'finance.update_exchange_rates',
        'schedule': crontab(minute=30),   # Every hour at :30
        'options': {'queue': 'default'}
    },

    # ── Daily tasks ───────────────────────────────────────────────────────────
    'refresh-churn-predictions-all': {
        'task': 'finance.refresh_churn_predictions_all',
        'schedule': crontab(hour=1, minute=0),   # 1am — low traffic
        'options': {'queue': 'ml'}
    },
    'cleanup-expired-transactions': {
        'task': 'finance.cleanup_expired_transactions',
        'schedule': crontab(hour=3, minute=0),   # 3am
        'options': {'queue': 'cleanup'}
    },
    'cleanup-kpi-snapshots': {
        'task': 'finance.cleanup_kpi_snapshots',
        'schedule': crontab(hour=3, minute=15),  # 3:15am
        'options': {'queue': 'cleanup'}
    },
    'generate-cash-flow-forecast': {
        'task': 'finance.generate_cash_flow_forecast',
        'schedule': crontab(hour=5, minute=0),   # 5am — before business day
        'options': {'queue': 'ml'}
    },
    'send-payment-reminders': {
        'task': 'finance.send_payment_reminders',
        'schedule': crontab(hour=8, minute=0),   # 8am
        'options': {'queue': 'notifications'}
    },
    'send-budget-alerts': {
        'task': 'finance.send_budget_alerts',
        'schedule': crontab(hour=9, minute=0),   # 9am
        'options': {'queue': 'notifications'}
    },
    'create-retention-tasks': {
        'task': 'finance.create_retention_tasks',
        'schedule': crontab(hour=7, minute=0),   # 7am
        'options': {'queue': 'default'}
    },
    'monitor-retention-outcomes': {
        'task': 'finance.monitor_retention_outcomes',
        'schedule': crontab(hour=8, minute=30),  # 8:30am
        'options': {'queue': 'default'}
    },
    'process-recurring-billing': {
        'task': 'finance.process_recurring_billing',
        'schedule': crontab(hour=0, minute=5),   # Midnight + 5min
        'options': {'queue': 'default'}
    },

    # ── Weekly tasks ──────────────────────────────────────────────────────────
    'generate-weekly-summary': {
        'task': 'finance.generate_weekly_summary',
        'schedule': crontab(day_of_week=1, hour=7, minute=0),  # Monday 7am
        'options': {'queue': 'default'}
    },
    'retrain-churn-model': {
        'task': 'finance.retrain_churn_model',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),  # Monday 2am
        'options': {'queue': 'ml'}
    },

    # ── Monthly tasks ─────────────────────────────────────────────────────────
    'generate-monthly-board-report': {
        'task': 'finance.generate_monthly_board_report',
        'schedule': crontab(day_of_month=1, hour=6, minute=0),  # 1st of month 6am
        'options': {'queue': 'default'}
    },
}

app.conf.timezone = 'Africa/Nairobi'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
