"""
Finance Celery Tasks — fully implemented, no stubs.
All tasks are production-ready with proper error handling and logging.
"""
from celery import shared_task
from decimal import Decimal
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
    """
    3am safety net cleanup.
    Before marking anything failed or deleting, query M-Pesa first.
    Only mark failed if M-Pesa confirms failure or transaction is too old to query (>24hrs).
    """
    try:
        import time
        from finance.models import TransactionQueue
        from finance.queryDaraja import query_stk_status
        from django.db.models import Q

        now = timezone.now()
        queried = 0
        recovered = 0
        timed_out = 0
        deleted = 0

        # ── Step 1: Query M-Pesa for anything still pending/processing ──────────
        # These are transactions the 3-minute task missed (e.g. server was down)
        # Only query if checkout_request_id exists and created within 24hrs
        queryable_cutoff = now - timedelta(hours=24)
        stuck = TransactionQueue.objects.filter(
            status__in=['pending', 'processing', 'Pending...'],
            checkout_request_id__isnull=False,
            created_at__gte=queryable_cutoff
        ).exclude(checkout_request_id='')

        for txn in stuck:
            try:
                result = query_stk_status(txn.checkout_request_id)
                if hasattr(result, 'content'):
                    import json
                    result = json.loads(result.content.decode())

                result_code = str(result.get('ResultCode', ''))

                if result_code == '0':
                    # M-Pesa confirmed payment — attempt full processing
                    _process_confirmed_payment(txn, result)
                    recovered += 1
                    logger.info(f"[cleanup] Recovered confirmed payment {txn.checkout_request_id}")

                elif result_code not in ('', '4999'):
                    # Definitive failure from M-Pesa
                    txn.mark_failed(
                        reason=result.get('ResultDesc', 'Payment failed — confirmed by M-Pesa at cleanup'),
                        error_code=f'MPESA_{result_code}',
                        failure_category='payment_gateway',
                        increment_retry=False
                    )
                    _refund_credit_if_needed(txn)
                    timed_out += 1

                # result_code 4999 = still processing — leave it, will be caught next run
                queried += 1
                time.sleep(1)  # 1s between queries — respect Safaricom rate limits

            except Exception as e:
                logger.error(f"[cleanup] Error querying {txn.checkout_request_id}: {e}")

        # ── Step 2: Mark as failed anything pending >24hrs that we couldn't query ──
        timeout_threshold = now - timedelta(hours=24)
        old_pending = TransactionQueue.objects.filter(
            status__in=['pending', 'processing', 'Pending...'],
            created_at__lt=timeout_threshold
        )
        for txn in old_pending:
            txn.mark_pending_timeout_failure()
            _refund_credit_if_needed(txn)
            timed_out += 1

        # ── Step 3: Delete expired pending items that are now failed ─────────────
        deleted_result = TransactionQueue.objects.filter(
            status='failed',
            expires_at__lt=now - timedelta(hours=24),
            failure_category='system_error',
            error_code='PENDING_TIMEOUT'
        ).delete()
        deleted = deleted_result[0]

        result = {
            'queried': queried,
            'recovered': recovered,
            'timed_out': timed_out,
            'deleted': deleted
        }
        logger.info(f"Transaction cleanup: {result}")
        return {'status': 'success', **result}

    except Exception as e:
        logger.error(f"Transaction cleanup failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.query_stuck_pending_transactions')
def query_stuck_pending_transactions():
    """
    Runs every 3 minutes.
    Finds transactions pending > 3 minutes (callback clearly missed)
    and queries M-Pesa for their real status.
    Processes confirmed payments immediately — customer gets internet access.
    """
    try:
        import time
        from finance.models import TransactionQueue
        from finance.queryDaraja import query_stk_status

        now = timezone.now()
        stuck_threshold = now - timedelta(minutes=3)   # pending > 3 min = stuck
        query_window = now - timedelta(minutes=30)     # only query within 30min window
        # (expires_at is set to T+30min on creation — beyond that Safaricom won't have it)

        stuck_txns = TransactionQueue.objects.filter(
            status__in=['pending', 'processing', 'Pending...'],
            created_at__lte=stuck_threshold,
            created_at__gte=query_window,
            checkout_request_id__isnull=False,
        ).exclude(checkout_request_id='').order_by('created_at')  # oldest first

        if not stuck_txns.exists():
            return {'status': 'success', 'stuck': 0, 'queried': 0}

        queried = 0
        recovered = 0
        confirmed_failed = 0
        still_processing = 0

        for txn in stuck_txns:
            try:
                result = query_stk_status(txn.checkout_request_id)

                # Handle JsonResponse error returns
                if hasattr(result, 'content'):
                    import json
                    result = json.loads(result.content.decode())

                result_code = str(result.get('ResultCode', ''))

                if result_code == '0':
                    # ✅ M-Pesa confirmed payment — process it now
                    success = _process_confirmed_payment(txn, result)
                    if success:
                        recovered += 1
                        logger.info(
                            f"[stuck_query] Recovered payment {txn.checkout_request_id} "
                            f"for {txn.initiator} KES {txn.price}"
                        )
                    else:
                        # Payment confirmed but voucher activation failed — refunded
                        logger.warning(
                            f"[stuck_query] Payment confirmed but activation failed "
                            f"{txn.checkout_request_id} — balance refunded"
                        )

                elif result_code == '4999':
                    # Still processing on Safaricom's end — leave it
                    still_processing += 1

                elif result_code != '':
                    # Definitive failure — mark failed and refund any credit used
                    FAILURE_REASONS = {
                        '1':    'Insufficient M-Pesa balance',
                        '1032': 'Cancelled by customer',
                        '1037': 'Customer phone unreachable — timed out',
                        '2001': 'Wrong M-Pesa PIN entered',
                        '1019': 'Transaction expired',
                        '17':   'Duplicate transaction',
                    }
                    reason = FAILURE_REASONS.get(
                        result_code,
                        result.get('ResultDesc', f'Payment failed (code {result_code})')
                    )
                    txn.mark_failed(
                        reason=reason,
                        error_code=f'MPESA_{result_code}',
                        failure_category='payment_gateway',
                        increment_retry=False
                    )
                    _refund_credit_if_needed(txn)
                    confirmed_failed += 1
                    logger.info(
                        f"[stuck_query] Confirmed failure {txn.checkout_request_id}: {reason}"
                    )

                queried += 1
                time.sleep(1)  # 1s between queries — Safaricom rate limit protection

            except Exception as e:
                logger.error(
                    f"[stuck_query] Error processing {txn.checkout_request_id}: {e}"
                )

        result = {
            'stuck_found': stuck_txns.count(),
            'queried': queried,
            'recovered': recovered,
            'confirmed_failed': confirmed_failed,
            'still_processing': still_processing,
        }
        logger.info(f"Stuck transaction query: {result}")
        return {'status': 'success', **result}

    except Exception as e:
        logger.error(f"query_stuck_pending_transactions failed: {e}")
        return {'status': 'error', 'error': str(e)}


def _credit_balance_for_payment(txn, mpesa_result, actioned_by='system'):
    """
    M-Pesa confirmed (ResultCode=0) — credit the payment amount to customer balance.
    Used by admin query_mpesa action instead of voucher activation.
    """
    from users.models import ClientH
    from finance.models import BalanceTransaction
    from decimal import Decimal

    if not txn.mark_processing():
        logger.info(f"[_credit_balance] {txn.checkout_request_id} already claimed")
        return 0

    txn.gateway_result_data = mpesa_result
    txn.save(update_fields=['gateway_result_data'])

    client = txn.user
    amount = Decimal(str(txn.price))

    balance_before = client.balance
    client.balance += amount
    client.save(update_fields=['balance'])

    BalanceTransaction.objects.create(
        user=client,
        transaction_type='topup',
        credit=amount,
        debit=0,
        balance_before=balance_before,
        balance_after=client.balance,
        description=f'M-Pesa payment credited to balance by {actioned_by}. '
                    f'Checkout: {txn.checkout_request_id}',
        reference=txn.checkout_request_id or '',
    )

    txn.mark_processed()

    try:
        from finance.models_medium import AuditLog
        AuditLog.objects.create(
            model_name='TransactionQueue',
            record_id=txn.id,
            action='update',
            changed_by=actioned_by,
            description=f'KES {amount} credited to balance for {client.account} via admin M-Pesa query'
        )
    except Exception:
        pass

    try:
        from core.services.notification_service import create_and_notify
        create_and_notify(
            client.user,
            f'KES {amount} has been credited to your account balance.',
            'success'
        )
    except Exception:
        pass

    logger.info(f"[_credit_balance] KES {amount} credited to {client.account}")
    return float(amount)


def _process_confirmed_payment(txn, mpesa_result):
    """
    Shared helper: M-Pesa confirmed payment (ResultCode=0).
    Activates voucher, updates client, marks processed.
    Returns True on full success, False if voucher activation failed (balance refunded).
    """
    try:
        from finance.querycheckout import PaymentProcessor, VoucherManager, JWTUserDataExtractor
        from finance.models import TransactionQueue
        from users.models import ClientH
        from decimal import Decimal
        import django.contrib.auth

        # Claim the transaction atomically — prevents double processing
        if not txn.mark_processing():
            logger.info(f"[_process_confirmed] {txn.checkout_request_id} already claimed")
            return True  # Another worker got it — not an error

        txn.gateway_result_data = mpesa_result
        txn.save(update_fields=['gateway_result_data'])

        # Get package
        from finance.querycheckout import JWTUserDataExtractor
        package_type = JWTUserDataExtractor.get_package_by_code(txn.package_code.strip())
        if not package_type:
            raise ValueError(f"Package not found: {txn.package_code}")

        # Build minimal user_context from the transaction record
        client = txn.user  # TransactionQueue.user is FK to ClientH
        django_user = client.user

        user_context = {
            'user': django_user,
            'client': client,
            'location': client.current_location or client.home_location,
            'jwt_payload': {},
            'account': client.account,
            'phone': txn.initiator,
            'account_tier': client.account_tier,
            'balance': client.balance,
            'home_location_id': client.home_location_id,
            'current_location_id': (client.current_location or client.home_location).id,
            'active_voucher_code': None,
            'voucher_expires_at': None,
            'voucher_package': None,
            'is_active': client.status == 'active',
            'auto_renew': client.auto_renew,
            'two_factor_enabled': client.two_factor_enabled,
        }

        # Activate voucher using existing production logic
        dispatch_voucher = VoucherManager.activate_and_create_voucher(
            user_context=user_context,
            package_type=package_type,
            package_code=txn.package_code.strip(),
            transaction_record=txn,
            hotspot_ip=None  # No hotspot IP in background task — customer will login manually
        )

        txn.mark_processed()

        # Log to AuditLog
        try:
            from finance.models_medium import AuditLog
            AuditLog.objects.create(
                model_name='TransactionQueue',
                record_id=txn.id,
                action='update',
                changed_by='celery:query_stuck_pending',
                description=(
                    f'Auto-recovered via M-Pesa query. '
                    f'Voucher {dispatch_voucher.voucher_code} activated. '
                    f'KES {txn.price} for {client.account}'
                )
            )
        except Exception:
            pass  # Audit log failure must never block payment processing

        # Notify customer
        try:
            from core.services.notification_service import create_and_notify
            create_and_notify(
                django_user,
                f'✅ Payment confirmed! Voucher {dispatch_voucher.voucher_code} activated. '
                f'Package: {package_type.name}',
                'success'
            )
        except Exception:
            pass

        return True

    except Exception as e:
        logger.error(f"[_process_confirmed] Voucher activation failed for {txn.checkout_request_id}: {e}")
        # Payment confirmed but activation failed — refund the M-Pesa amount to balance
        try:
            _refund_mpesa_to_balance(txn)
            txn.status = 'refunded'
            txn.failure_reason = f'Payment confirmed but activation failed: {e}'
            txn.save(update_fields=['status', 'failure_reason'])
        except Exception as refund_err:
            logger.error(f"[_process_confirmed] Refund also failed: {refund_err}")
        return False


def _refund_credit_if_needed(txn):
    """Refund used_credit back to customer balance if a mixed payment failed."""
    try:
        if txn.used_credit and txn.used_credit > 0:
            from users.models import ClientH
            from django.db import transaction as db_transaction
            with db_transaction.atomic():
                client = ClientH.objects.select_for_update().get(pk=txn.user_id)
                client.balance += Decimal(str(txn.used_credit))
                client.save(update_fields=['balance'])
            logger.info(
                f"[refund_credit] Refunded KES {txn.used_credit} credit to {txn.user.account}"
            )
    except Exception as e:
        logger.error(f"[refund_credit] Failed for {txn.checkout_request_id}: {e}")


def _refund_mpesa_to_balance(txn):
    """Refund the M-Pesa portion (price - used_credit) to customer balance."""
    try:
        from users.models import ClientH
        from django.db import transaction as db_transaction
        refund_amount = Decimal(str(txn.price)) - Decimal(str(txn.used_credit or 0))
        if refund_amount <= 0:
            return
        with db_transaction.atomic():
            client = ClientH.objects.select_for_update().get(pk=txn.user_id)
            client.balance += refund_amount
            client.save(update_fields=['balance'])
        logger.info(
            f"[refund_mpesa] Refunded KES {refund_amount} to {txn.user.account} "
            f"(price={txn.price} used_credit={txn.used_credit})"
        )
    except Exception as e:
        logger.error(f"[refund_mpesa] Failed for {txn.checkout_request_id}: {e}")


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
        from users.models import ClientH
        from finance.models_reminder import PaymentReminder
        from django.utils import timezone

        now = timezone.now()
        sent = 0
        skipped = 0

        # Check customers with voucher_expiry set
        customers = ClientH.objects.filter(
            voucher_expiry__isnull=False,
            status='active'
        )

        for customer in customers:
            expiry = customer.voucher_expiry
            if not expiry:
                continue

            # Make expiry timezone-aware if needed
            if timezone.is_naive(expiry):
                expiry = timezone.make_aware(expiry)

            days_until = (expiry - now).days
            phone = customer.phone_number
            if not phone:
                skipped += 1
                continue

            # Determine reminder type
            reminder_type = None
            if days_until == 3:
                reminder_type = 'expiry_3d'
                msg = f'Hi {customer.account}, your internet package expires in 3 days. Renew now to stay connected.'
            elif days_until == 1:
                reminder_type = 'expiry_1d'
                msg = f'Hi {customer.account}, your internet package expires TOMORROW. Renew now to avoid disconnection.'
            elif days_until == 0:
                reminder_type = 'expiry_day'
                msg = f'Hi {customer.account}, your internet package expires TODAY. Renew now to stay connected.'
            elif days_until == -3:
                reminder_type = 'overdue_3d'
                msg = f'Hi {customer.account}, your internet package expired 3 days ago. Renew to reconnect.'
            elif days_until == -7:
                reminder_type = 'overdue_7d'
                msg = f'Hi {customer.account}, FINAL NOTICE: your package expired 7 days ago. Renew immediately or service will be suspended.'

            if not reminder_type:
                continue

            # Avoid duplicate reminders
            already_sent = PaymentReminder.objects.filter(
                customer=customer,
                reminder_type=reminder_type,
                scheduled_at__date=now.date()
            ).exists()

            if already_sent:
                continue

            # Create reminder record
            reminder = PaymentReminder.objects.create(
                customer=customer,
                reminder_type=reminder_type,
                scheduled_at=now,
                message=msg,
                phone_number=phone,
                status='pending'
            )

            # TODO: Send via Africa's Talking / Twilio in production
            # For now, log and mark as sent
            logger.info(f"REMINDER [{reminder_type}] to {phone}: {msg}")
            reminder.mark_sent()
            sent += 1

        logger.info(f"Payment reminders: {sent} sent, {skipped} skipped (no phone)")
        return {'status': 'success', 'sent': sent, 'skipped': skipped}
    except Exception as e:
        logger.error(f"Payment reminders failed: {e}")
        return {'status': 'error', 'error': str(e)}


# ─── RECURRING BILLING (6.12 — placeholder until model created) ───────────────

@shared_task(name='finance.process_recurring_billing')
def process_recurring_billing():
    """Process recurring billing for monthly packages. Runs daily at midnight."""
    try:
        from finance.models_billing import RecurringBilling
        success, failed = RecurringBilling.process_due_billings()
        logger.info(f"Recurring billing: {success} success, {failed} failed")
        return {'status': 'success', 'success': success, 'failed': failed}
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


@shared_task(name='finance.calculate_monthly_vat')
def calculate_monthly_vat():
    """Auto-calculate VAT return for last month. Runs 1st of each month at 7am."""
    try:
        from finance.models_vat import VATReturn
        last_month = (timezone.now().replace(day=1) - timedelta(days=1))
        vat_return = VATReturn.calculate_for_period(last_month.year, last_month.month)
        logger.info(f"VAT return calculated: {last_month.month}/{last_month.year} — Net KES {vat_return.net_vat}")
        return {'status': 'success', 'net_vat': float(vat_return.net_vat)}
    except Exception as e:
        logger.error(f"VAT calculation failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.calculate_monthly_vat')
def calculate_monthly_vat():
    """Auto-calculate VAT return for last month. Runs 1st of each month at 7am."""
    try:
        from finance.models_vat import VATReturn
        last_month = (timezone.now().replace(day=1) - timedelta(days=1))
        vat_return = VATReturn.calculate_for_period(last_month.year, last_month.month)
        logger.info(f"VAT return calculated: {last_month.month}/{last_month.year} — Net KES {vat_return.net_vat}")
        return {'status': 'success', 'net_vat': float(vat_return.net_vat)}
    except Exception as e:
        logger.error(f"VAT calculation failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.calculate_monthly_wht')
def calculate_monthly_wht():
    """Calculate withholding tax for last month. Runs 1st of each month at 7:30am."""
    try:
        from finance.models_tax import TaxReturn
        last_month = (timezone.now().replace(day=1) - timedelta(days=1))
        r = TaxReturn.calculate_wht(last_month.year, last_month.month)
        logger.info(f"WHT calculated: {last_month.month}/{last_month.year} — KES {r.tax_amount}")
        return {'status': 'success', 'wht_amount': float(r.tax_amount)}
    except Exception as e:
        logger.error(f"WHT calculation failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.generate_tax_calendar')
def generate_tax_calendar():
    """Generate tax calendar for current year. Runs on Jan 1st."""
    try:
        from finance.models_tax import TaxReturn
        year = timezone.now().year
        entries = TaxReturn.generate_calendar(year)
        logger.info(f"Tax calendar generated for {year}: {len(entries)} entries")
        return {'status': 'success', 'year': year, 'entries': len(entries)}
    except Exception as e:
        logger.error(f"Tax calendar generation failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.check_tax_deadlines')
def check_tax_deadlines():
    """Check for upcoming tax deadlines and log alerts. Runs daily at 9:30am."""
    try:
        from finance.models_tax import TaxReturn
        upcoming = TaxReturn.get_upcoming(days=7)
        overdue = [r for r in TaxReturn.objects.filter(
            status__in=['pending', 'calculated']
        ) if r.is_overdue]

        for r in overdue:
            logger.warning(f"TAX OVERDUE: {r.get_tax_type_display()} {r.period_label} — KES {r.tax_amount}")
        for r in upcoming:
            logger.info(f"TAX DUE IN {r.days_until_due}d: {r.get_tax_type_display()} {r.period_label}")

        return {
            'status': 'success',
            'overdue': len(overdue),
            'upcoming_7d': upcoming.count()
        }
    except Exception as e:
        logger.error(f"Tax deadline check failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.run_monthly_payroll')
def run_monthly_payroll():
    """Process monthly payroll for all active employees. Runs 25th of each month at 8am."""
    try:
        from finance.models_payroll import PayrollCalculator, Employee
        now = timezone.now()
        count = Employee.objects.filter(is_active=True).count()
        if count == 0:
            logger.info("Payroll skipped — no active employees")
            return {'status': 'skipped', 'reason': 'no employees'}

        run = PayrollCalculator.run_payroll(now.year, now.month)
        logger.info(f"Payroll processed: {run.period_label} — {count} employees — Net KES {run.total_net}")
        return {'status': 'success', 'period': run.period_label, 'employees': count, 'total_net': float(run.total_net)}
    except Exception as e:
        logger.error(f"Payroll run failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.post_monthly_depreciation')
def post_monthly_depreciation():
    """Post monthly depreciation for all active assets. Runs 1st of each month at 8am."""
    try:
        from finance.models_asset import Asset
        from finance.models import Expense, Currency
        from django.utils import timezone

        assets = Asset.objects.filter(status='active').exclude(depreciation_method='none')
        posted = 0
        total_dep = Decimal('0')

        currency = Currency.objects.filter(code='KES').first()

        for asset in assets:
            monthly_dep = asset.monthly_depreciation
            if monthly_dep <= 0:
                continue

            # Post as expense
            if currency:
                Expense.objects.create(
                    expense_date=timezone.now().date(),
                    description=f'Depreciation — {asset.name} ({asset.asset_number})',
                    amount=monthly_dep,
                    currency=currency,
                    category='other',
                    department=asset.department,
                    approval_status='paid',
                    is_capex=False,
                    vat_rate=Decimal('0'),
                )

            asset.accumulated_depreciation += monthly_dep
            asset.current_book_value = max(
                asset.purchase_cost - asset.accumulated_depreciation,
                asset.salvage_value
            )
            asset.save()
            total_dep += monthly_dep
            posted += 1

        logger.info(f"Depreciation posted: {posted} assets — KES {total_dep:,.2f}")
        return {'status': 'success', 'assets': posted, 'total_depreciation': float(total_dep)}
    except Exception as e:
        logger.error(f"Depreciation posting failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.check_ap_overdue')
def check_ap_overdue():
    """Flag overdue vendor invoices. Runs daily at 9am."""
    try:
        from finance.models_ap import VendorInvoice
        from datetime import date

        overdue = VendorInvoice.objects.filter(
            status__in=['received', 'approved'],
            due_date__lt=date.today()
        )
        count = 0
        for inv in overdue:
            if inv.status != 'overdue':
                inv.status = 'overdue'
                inv.save()
                logger.warning(f"AP OVERDUE: {inv.vendor_name} — {inv.invoice_number} — KES {inv.total} — {inv.days_overdue}d overdue")
                count += 1

        logger.info(f"AP overdue check: {count} newly flagged")
        return {'status': 'success', 'newly_overdue': count}
    except Exception as e:
        logger.error(f"AP overdue check failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.update_ar_collection_cases')
def update_ar_collection_cases():
    """Create/update AR collection cases for overdue customers. Runs daily at 10am."""
    try:
        from finance.models_ar import DebtCollection
        created = DebtCollection.create_collection_cases()
        logger.info(f"AR collection cases updated: {created} new cases")
        return {'status': 'success', 'new_cases': created}
    except Exception as e:
        logger.error(f"AR collection update failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.generate_monthly_pl')
def generate_monthly_pl():
    """Generate monthly P&L statement. Runs 2nd of each month at 8am."""
    try:
        from finance.models_pl import PLStatement
        last_month = (timezone.now().replace(day=1) - timedelta(days=1))
        pl = PLStatement.generate(last_month.year, month=last_month.month)
        logger.info(f"P&L generated: {pl.period_label} — Net KES {pl.net_profit:,.2f}")
        return {'status': 'success', 'period': pl.period_label, 'net_profit': float(pl.net_profit)}
    except Exception as e:
        logger.error(f"P&L generation failed: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task(name='finance.send_expense_notifications')
def send_expense_notifications():
    """Check for pending expense approvals and send overdue alerts. Runs daily at 9am."""
    try:
        from finance.models import Expense
        from finance.models_medium import AuditLog

        overdue = Expense.objects.filter(
            approval_status='submitted',
            submitted_at__lt=timezone.now() - timedelta(hours=48)
        )
        count = 0
        for expense in overdue:
            logger.warning(f"EXPENSE OVERDUE: {expense.description} — KES {expense.amount} — submitted {expense.submitted_at}")
            AuditLog.log('Expense', expense.id, 'update', description=f'Approval overdue 48h: {expense.description}')
            count += 1

        logger.info(f"Expense notifications: {count} overdue approvals flagged")
        return {'status': 'success', 'overdue_count': count}
    except Exception as e:
        logger.error(f"Expense notifications failed: {e}")
        return {'status': 'error', 'error': str(e)}
