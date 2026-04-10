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
    recalculate_budget_utilization,
    check_fraud_correlation,
    send_retention_sms
)
import logging

logger = logging.getLogger(__name__)


@receiver(payment_completed)
def handle_payment_completed(sender, payment, **kwargs):
    """
    Handle payment completion event.
    Triggers churn model refresh for the customer.
    """
    logger.info(f"Payment completed: {payment.transaction_id} for customer {payment.user_id}")
    
    # Refresh churn prediction for this customer
    refresh_churn_prediction.delay(customer_id=payment.user_id)
    
    # Update customer payment history
    logger.info(f"Triggered churn prediction refresh for customer {payment.user_id}")


@receiver(expense_created)
def handle_expense_created(sender, expense, **kwargs):
    """
    Handle expense creation event.
    Triggers budget utilization recalculation.
    """
    logger.info(f"Expense created: {expense.id} - {expense.category} - {expense.amount}")
    
    # Recalculate budget utilization
    recalculate_budget_utilization.delay(
        category=expense.category,
        month=expense.date.month,
        year=expense.date.year
    )
    
    logger.info(f"Triggered budget recalculation for {expense.category}")


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
    
    # Check for fraud correlation with recent payments
    check_fraud_correlation.delay(
        anomaly_type=anomaly.get('type'),
        src_ip=anomaly.get('src_ip'),
        timestamp=anomaly.get('timestamp')
    )
    
    logger.info(f"Triggered fraud correlation check for anomaly")


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
