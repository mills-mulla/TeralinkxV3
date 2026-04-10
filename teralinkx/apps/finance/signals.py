"""
Finance Event Signals
Event-driven architecture for Smart Business Management system.
"""
from django.dispatch import Signal

# Payment events
payment_completed = Signal()  # Triggered when payment is completed
payment_failed = Signal()  # Triggered when payment fails
payment_pending = Signal()  # Triggered when payment is pending

# Expense events
expense_created = Signal()  # Triggered when expense is created
expense_approved = Signal()  # Triggered when expense is approved
expense_rejected = Signal()  # Triggered when expense is rejected

# Budget events
budget_threshold_exceeded = Signal()  # Triggered when budget threshold exceeded
budget_depleted = Signal()  # Triggered when budget fully depleted

# Invoice events
invoice_uploaded = Signal()  # Triggered when invoice is uploaded
invoice_processed = Signal()  # Triggered when invoice OCR completes

# Reconciliation events
reconciliation_match_found = Signal()  # Triggered when transaction matched
reconciliation_completed = Signal()  # Triggered when reconciliation job completes

# HIDS events
hids_anomaly_detected = Signal()  # Triggered when HIDS detects anomaly
hids_fraud_suspected = Signal()  # Triggered when fraud correlation found

# Customer events
customer_churn_risk_high = Signal()  # Triggered when churn risk > 70%
customer_payment_late = Signal()  # Triggered when payment is late
customer_package_downgraded = Signal()  # Triggered when package downgraded
