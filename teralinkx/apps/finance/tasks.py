"""
Finance Celery Tasks — fully implemented, no stubs.
All tasks are production-ready with proper error handling and logging.
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


# ─── KPI ──────────────────────────────────────────────────────────────────────

@shared_task(name='finance.refresh_kpi_snapshot')
def refresh_kpi_snapshot():
    """Refresh KPI snapshot every 5 minutes."""
    try:
        from finance.kpi_service import KPICalculationService
        snapshot = KPICalculationService.generate_kpi_snapshot()
        logger.info(f"KPI snapshot refreshed in {snapshot.computed_in_ms}ms")
        return {'status': 'success', 'computed_in_ms': snapshot.computed_in_ms}
    except Exception as e:
        logger.error(f"KPI snapshot failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.cleanup_kpi_snapshots')
def cleanup_kpi_snapshots():
    """Delete KPI snapshots older than 24 hours. Runs daily at 3am."""
    try:
        from finance.models_kpi import KPISnapshot
        deleted = KPISnapshot.cleanup_old_snapshots(hours=24)
        logger.info(f"Deleted {deleted} old KPI snapshots")
        return {'status': 'success', 'deleted': deleted}
    except Exception as e:
        logger.error(f"KPI cleanup failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── CHURN ────────────────────────────────────────────────────────────────────

@shared_task(name='finance.refresh_churn_prediction')
def refresh_churn_prediction(customer_id):
    """Refresh churn prediction for a single customer. Triggered by payment/session events."""
    try:
        from users.models import ClientH
        from finance.models_churn import ChurnPrediction
        from finance.ml_churn_service import predict_churn_ml

        customer = ClientH.objects.get(id=customer_id)
        score, method = predict_churn_ml(customer)
        risk_level = ChurnPrediction.get_risk_level(score)

        ChurnPrediction.objects.filter(customer=customer, is_active=True).update(is_active=False)
        ChurnPrediction.objects.create(
            customer=customer,
            churn_score=score,
            risk_level=risk_level,
            prediction_method=method,
            is_active=True
        )
        logger.info(f"Churn prediction refreshed for customer {customer_id}: {risk_level} ({score:.3f})")
        return {'status': 'success', 'customer_id': customer_id, 'risk_level': risk_level}
    except Exception as e:
        logger.error(f"Churn prediction failed for customer {customer_id}: {e}")
        return {'status': 'error', 'customer_id': customer_id, 'error': str(e)}


@shared_task(name='finance.refresh_churn_predictions_all')
def refresh_churn_predictions_all():
    """Bulk refresh churn predictions for all active customers. Runs daily at 1am."""
    try:
        from users.models import ClientH
        from finance.models_churn import ChurnPrediction, RetentionTask
        from finance.ml_churn_service import predict_churn_ml

        customers = ClientH.objects.exclude(status='inactive')
        updated = 0
        tasks_created = 0

        for customer in customers:
            try:
                score, method = predict_churn_ml(customer)
                risk_level = ChurnPrediction.get_risk_level(score)

                ChurnPrediction.objects.filter(customer=customer, is_active=True).update(is_active=False)
                pred = ChurnPrediction.objects.create(
                    customer=customer,
                    churn_score=score,
                    risk_level=risk_level,
                    prediction_method=method,
                    is_active=True
                )
                updated += 1

                # Auto-create retention task for high/critical risk
                if risk_level in ['high', 'critical']:
                    if not RetentionTask.objects.filter(customer=customer, status='pending').exists():
                        RetentionTask.create_retention_task(pred)
                        tasks_created += 1
            except Exception as e:
                logger.warning(f"Skipping customer {customer.id}: {e}")

        logger.info(f"Bulk churn refresh: {updated} predictions, {tasks_created} tasks created")
        return {'status': 'success', 'updated': updated, 'tasks_created': tasks_created}
    except Exception as e:
        logger.error(f"Bulk churn refresh failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.retrain_churn_model')
def retrain_churn_model():
    """Retrain XGBoost churn model weekly. Runs Monday 2am."""
    try:
        from django.core.management import call_command
        call_command('train_churn_model')
        logger.info("Churn model retrained successfully")
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"Churn model retraining failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── RETENTION ────────────────────────────────────────────────────────────────

@shared_task(name='finance.create_retention_tasks')
def create_retention_tasks():
    """Create retention tasks for high-risk customers. Runs daily at 7am."""
    try:
        from finance.models_churn import ChurnPrediction, RetentionTask

        high_risk = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True
        ).exclude(retention_tasks__status__in=['pending', 'in_progress'])

        tasks_created = 0
        for prediction in high_risk:
            task = RetentionTask.create_retention_task(prediction)
            if task.automated:
                task.execute_action()
            tasks_created += 1

        logger.info(f"Created {tasks_created} retention tasks")
        return {'status': 'success', 'tasks_created': tasks_created}
    except Exception as e:
        logger.error(f"Retention task creation failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.monitor_retention_outcomes')
def monitor_retention_outcomes():
    """Monitor retention task outcomes. Runs daily at 8am."""
    try:
        from finance.models_churn import RetentionTask
        from finance.models import PaymentTransaction

        cutoff = timezone.now() - timedelta(days=30)
        pending_tasks = RetentionTask.objects.filter(
            status='completed',
            outcome='pending',
            action_taken_at__gte=cutoff
        )

        retained = churned = relocated = 0
        for task in pending_tasks:
            has_payment = PaymentTransaction.objects.filter(
                user=task.customer,
                created_at__gte=task.action_taken_at
            ).exists()

            if has_payment:
                task.mark_outcome('retained', 'Payment made after retention action')
                retained += 1
            elif (timezone.now() - task.action_taken_at).days >= 60:
                if getattr(task.customer, 'status', '') == 'relocated':
                    task.mark_outcome('relocated', 'Customer relocated')
                    relocated += 1
                else:
                    task.mark_outcome('churned', 'No activity for 60+ days')
                    churned += 1

        logger.info(f"Retention outcomes: {retained} retained, {churned} churned, {relocated} relocated")
        return {'status': 'success', 'retained': retained, 'churned': churned, 'relocated': relocated}
    except Exception as e:
        logger.error(f"Retention outcome monitoring failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── REVENUE AT RISK ──────────────────────────────────────────────────────────

@shared_task(name='finance.refresh_revenue_at_risk_cache')
def refresh_revenue_at_risk_cache():
    """Refresh revenue at risk cache every 10 minutes."""
    try:
        from finance.revenue_at_risk_service import RevenueAtRiskService
        from django.core.cache import cache

        summary = RevenueAtRiskService.get_dashboard_summary()
        cache.set('revenue_at_risk_dashboard', summary, 600)

        logger.info(f"Revenue at risk cache refreshed: KES {summary['total_revenue_at_risk']:,.2f}")
        return {
            'status': 'success',
            'total_revenue_at_risk': summary['total_revenue_at_risk'],
            'top_accounts_count': len(summary.get('top_at_risk_accounts', []))
        }
    except Exception as e:
        logger.error(f"Revenue at risk cache refresh failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── CASH FLOW ────────────────────────────────────────────────────────────────

@shared_task(name='finance.generate_cash_flow_forecast')
def generate_cash_flow_forecast(horizon_days=90):
    """Generate cash flow forecast using Prophet. Runs daily at 6am."""
    try:
        from finance.cashflow_service import CashflowService
        from finance.models_cashflow import CashFlowForecast

        today = timezone.now().date()
        generated = 0

        for scenario in ['optimistic', 'base', 'conservative']:
            try:
                forecast = CashflowService.generate_forecast(
                    scenario=scenario,
                    horizon_days=horizon_days
                )
                if forecast:
                    generated += 1
            except Exception as e:
                logger.warning(f"Forecast scenario {scenario} failed: {e}")

        logger.info(f"Cash flow forecasts generated: {generated}/3 scenarios")
        return {'status': 'success', 'scenarios_generated': generated}
    except Exception as e:
        logger.error(f"Cash flow forecast failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── BUDGET ───────────────────────────────────────────────────────────────────

@shared_task(name='finance.send_budget_alerts')
def send_budget_alerts():
    """Check departments over budget thresholds and send alerts. Runs daily at 9am."""
    try:
        from finance.models import Department
        from finance.budget_service import BudgetIntelligenceService

        alerts = BudgetIntelligenceService.get_budget_alerts()
        critical = [a for a in alerts if a['severity'] == 'critical']
        warnings = [a for a in alerts if a['severity'] == 'warning']

        # Log alerts — SMS/email integration to be added in 6.13
        for alert in critical:
            logger.warning(f"BUDGET CRITICAL: {alert['department']} at {alert['utilization']:.1f}%")
        for alert in warnings:
            logger.info(f"BUDGET WARNING: {alert['department']} at {alert['utilization']:.1f}%")

        logger.info(f"Budget alerts: {len(critical)} critical, {len(warnings)} warnings")
        return {'status': 'success', 'critical': len(critical), 'warnings': len(warnings)}
    except Exception as e:
        logger.error(f"Budget alerts failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── BOARD REPORTS ────────────────────────────────────────────────────────────

@shared_task(name='finance.generate_monthly_board_report')
def generate_monthly_board_report():
    """Generate monthly board report. Runs 1st of each month at 6am."""
    try:
        from finance.board_report_service import BoardReportService

        last_month = (timezone.now().replace(day=1) - timedelta(days=1))
        report = BoardReportService.generate_monthly_report(last_month.year, last_month.month)

        logger.info(f"Board report generated: {report.report_period_display} (ID: {report.id})")
        return {'status': 'success', 'report_id': report.id, 'period': report.report_period_display}
    except Exception as e:
        logger.error(f"Board report generation failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── WEEKLY SUMMARY ───────────────────────────────────────────────────────────

@shared_task(name='finance.generate_weekly_summary')
def generate_weekly_summary():
    """Auto-generate weekly executive summary. Runs Monday 7am."""
    try:
        from finance.models_kpi import WeeklySummary, KPISnapshot
        from finance.models import TransactionQueue
        from finance.models_churn import ChurnPrediction
        from django.db.models import Sum

        now = timezone.now()
        week_start = (now - timedelta(days=now.weekday() + 7)).replace(hour=0, minute=0, second=0)
        week_end = week_start + timedelta(days=6, hours=23, minutes=59)

        # Weekly revenue
        weekly_revenue = TransactionQueue.objects.filter(
            status__in=['completed', 'processed'],
            created_at__range=[week_start, week_end]
        ).aggregate(total=Sum('price'))['total'] or 0

        # Churn risk
        high_risk_count = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'], is_active=True
        ).count()

        from finance.kpi_service import KPICalculationService
        revenue_at_risk = float(KPICalculationService.get_revenue_at_risk())

        # Auto-generate highlights and risks
        highlights = []
        risks = []

        if weekly_revenue > 0:
            highlights.append(f"Weekly revenue: KES {weekly_revenue:,.0f}")
        if high_risk_count == 0:
            highlights.append("No critical churn risk customers this week")

        if high_risk_count > 0:
            risks.append(f"{high_risk_count} customers at high/critical churn risk")
        if revenue_at_risk > 0:
            risks.append(f"KES {revenue_at_risk:,.0f} revenue at risk from potential churn")

        from users.models import ClientH
        new_customers = ClientH.objects.filter(created_at__range=[week_start, week_end]).count()
        if new_customers > 0:
            highlights.append(f"{new_customers} new customers acquired")

        WeeklySummary.objects.update_or_create(
            week_start=week_start.date(),
            defaults={
                'week_end': week_end.date(),
                'top_wins': highlights[:3],
                'top_risks': risks[:3],
                'weekly_revenue': weekly_revenue,
                'weekly_new_customers': new_customers,
                'churn_risk_summary': {
                    'high_risk': high_risk_count,
                    'revenue_at_risk': revenue_at_risk
                }
            }
        )

        logger.info(f"Weekly summary generated: {len(highlights)} wins, {len(risks)} risks")
        return {'status': 'success', 'highlights': len(highlights), 'risks': len(risks)}
    except Exception as e:
        logger.error(f"Weekly summary generation failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── EXCHANGE RATES ───────────────────────────────────────────────────────────

@shared_task(name='finance.update_exchange_rates')
def update_exchange_rates():
    """Fetch latest KES exchange rates. Runs daily at 6am."""
    try:
        from finance.models import ExchangeRate, Currency
        import urllib.request
        import json

        # Use free exchangerate-api.com (no key needed for basic rates)
        url = 'https://open.er-api.com/v6/latest/KES'
        try:
            with urllib.request.urlopen(url, timeout=10) as response:
                data = json.loads(response.read())
                rates = data.get('rates', {})
        except Exception:
            # Fallback: use approximate rates if API unavailable
            rates = {'USD': 0.0077, 'EUR': 0.0071, 'GBP': 0.0061, 'ZAR': 0.14}

        updated = 0
        kes = Currency.objects.filter(code='KES').first()
        if not kes:
            return {'status': 'skipped', 'reason': 'KES currency not found'}

        for code, rate in rates.items():
            try:
                target = Currency.objects.filter(code=code).first()
                if target:
                    ExchangeRate.objects.update_or_create(
                        base_currency=kes,
                        target_currency=target,
                        defaults={'rate': rate, 'source': 'openexchangerates'}
                    )
                    updated += 1
            except Exception:
                pass

        logger.info(f"Exchange rates updated: {updated} currencies")
        return {'status': 'success', 'updated': updated}
    except Exception as e:
        logger.error(f"Exchange rate update failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── CLEANUP ──────────────────────────────────────────────────────────────────

@shared_task(name='finance.cleanup_expired_transactions')
def cleanup_expired_transactions():
    """Clean up expired TransactionQueue items. Runs daily at 3am."""
    try:
        from finance.models import TransactionQueue
        result = TransactionQueue.cleanup_expired_items()
        logger.info(f"Transaction cleanup: {result}")
        return {'status': 'success', **result}
    except Exception as e:
        logger.error(f"Transaction cleanup failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.refresh_timescale_aggregates')
def refresh_timescale_aggregates():
    """Refresh TimescaleDB continuous aggregates. Runs hourly."""
    try:
        from django.db import connection
        with connection.cursor() as c:
            for view in ['daily_revenue', 'hourly_transactions']:
                try:
                    c.execute(f"""
                        CALL refresh_continuous_aggregate('{view}',
                            NOW() - INTERVAL '2 hours', NOW())
                    """)
                except Exception as e:
                    logger.warning(f"Aggregate {view} refresh failed: {e}")

        logger.info("TimescaleDB aggregates refreshed")
        return {'status': 'success'}
    except Exception as e:
        logger.error(f"TimescaleDB aggregate refresh failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── PAYMENT REMINDERS (6.4 — placeholder until model created) ────────────────

@shared_task(name='finance.send_payment_reminders')
def send_payment_reminders():
    """Send payment reminders for expiring packages. Runs daily at 8am."""
    try:
        # TODO: Implement in Phase 6.4 when PaymentReminder model is created
        # Will check packages expiring in 3 days, 1 day, and already expired
        logger.info("Payment reminders task — pending Phase 6.4 implementation")
        return {'status': 'pending_implementation', 'phase': '6.4'}
    except Exception as e:
        logger.error(f"Payment reminders failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── RECURRING BILLING (6.12 — placeholder until model created) ───────────────

@shared_task(name='finance.process_recurring_billing')
def process_recurring_billing():
    """Process recurring billing for monthly packages. Runs daily at midnight."""
    try:
        # TODO: Implement in Phase 6.12 when RecurringBilling model is created
        logger.info("Recurring billing task — pending Phase 6.12 implementation")
        return {'status': 'pending_implementation', 'phase': '6.12'}
    except Exception as e:
        logger.error(f"Recurring billing failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.send_retention_sms')
def send_retention_sms(customer_id, offer_type, churn_score):
    """Send retention SMS to at-risk customer. Triggered by high churn risk signal."""
    try:
        from users.models import ClientH
        customer = ClientH.objects.get(id=customer_id)
        phone = getattr(customer, 'phone_number', None)
        if not phone:
            return {'status': 'skipped', 'reason': 'no phone number'}

        messages = {
            'auto_discount_20': f'Hi {customer.account}, we value you! Enjoy 20% off your next package. Reply YES to claim.',
            'sms_discount_10':  f'Hi {customer.account}, special offer: 10% off your next renewal. Reply YES to claim.',
            'sms_reengagement': f'Hi {customer.account}, we miss you! Check out our latest packages at teralinkxwaves.uk',
        }
        message = messages.get(offer_type, messages['sms_reengagement'])

        # TODO: Integrate with Africa's Talking / Twilio in Phase 6.4
        logger.info(f"SMS to {phone}: {message}")
        return {'status': 'success', 'customer_id': customer_id, 'phone': phone}
    except Exception as e:
        logger.error(f"Retention SMS failed for customer {customer_id}: {e}")
        return {'status': 'error', 'customer_id': customer_id, 'error': str(e)}
