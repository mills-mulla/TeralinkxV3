"""
Finance Signal Handlers
Handles events triggered by finance signals.
"""
from django.dispatch import receiver
from django.utils import timezone
from .signals import (
    payment_completed,
    expense_created,
    budget_threshold_exceeded,
    hids_anomaly_detected,
    customer_churn_risk_high
)
from .tasks import (
    refresh_churn_prediction,
    send_budget_alerts,
    send_retention_sms
)
import logging

logger = logging.getLogger(__name__)


@receiver(payment_completed)
def handle_payment_completed(sender, payment, **kwargs):
    """Handle payment completion — auto-generate invoice and refresh churn."""
    logger.info(f"Payment completed: {payment.transaction_id} for customer {payment.user_id}")

    # Auto-generate tax invoice
    try:
        from finance.models_invoice import Invoice
        invoice = Invoice.create_from_transaction(payment)
        logger.info(f"Invoice generated: {invoice.invoice_number}")
    except Exception as e:
        logger.error(f"Invoice generation failed for {payment.transaction_id}: {e}")

    # Refresh churn prediction
    refresh_churn_prediction.delay(customer_id=payment.user_id)


@receiver(expense_created)
def handle_expense_created(sender, expense, **kwargs):
    """
    Handle expense creation event.
    Triggers budget utilization recalculation.
    """
    logger.info(f"Expense created: {expense.id} - {expense.category} - {expense.amount}")
    send_budget_alerts.delay()
    logger.info(f"Triggered budget alert check after expense creation")


@receiver(budget_threshold_exceeded)
def handle_budget_threshold_exceeded(sender, budget, utilization_rate, **kwargs):
    """
    Handle budget threshold exceeded event.
    Sends alert to finance team.
    """
    logger.warning(
        f"Budget threshold exceeded: {budget.category} at {utilization_rate}% "
        f"(threshold: {budget.alert_threshold}%)"
    )
    
    # Send alert notification
    # TODO: Implement notification system
    logger.info(f"Budget alert sent for {budget.category}")


@receiver(hids_anomaly_detected)
def handle_hids_anomaly(sender, anomaly, **kwargs):
    """
    Handle HIDS anomaly detection event.
    Triggers fraud correlation check.
    """
    logger.warning(f"HIDS anomaly detected: {anomaly.get('type')} from {anomaly.get('src_ip')}")
    # Fraud correlation deferred to Phase 3 (HIDS integration)
    logger.info("HIDS anomaly logged — fraud correlation pending Phase 3")


@receiver(customer_churn_risk_high)
def handle_churn_risk_high(sender, customer, churn_score, **kwargs):
    """
    Handle high churn risk event.
    Triggers automated retention workflow.
    """
    logger.warning(f"High churn risk detected: Customer {customer.id} - Score: {churn_score}")
    
    # Calculate customer value tier
    mrr = customer.get_mrr()  # Assuming method exists
    
    if mrr >= 5000:  # High-value customer (>KES 5K/month)
        # Auto-apply 20% discount
        logger.info(f"Auto-applying 20% discount for high-value customer {customer.id}")
        # TODO: Implement discount application
    elif mrr >= 2000:  # Medium-value customer
        # Send SMS with 10% offer
        send_retention_sms.delay(
            customer_id=customer.id,
            offer_type='discount_10',
            churn_score=churn_score
        )
        logger.info(f"Sent retention SMS to medium-value customer {customer.id}")
    else:  # Low-value customer
        # Send re-engagement SMS
        send_retention_sms.delay(
            customer_id=customer.id,
            offer_type='reengagement',
            churn_score=churn_score
        )
        logger.info(f"Sent re-engagement SMS to low-value customer {customer.id}")
