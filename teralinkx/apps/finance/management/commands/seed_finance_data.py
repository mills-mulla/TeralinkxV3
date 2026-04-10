# apps/finance/management/commands/seed_finance_data.py
import random
import uuid
from decimal import Decimal
from datetime import timedelta, date
from django.core.management.base import BaseCommand
from django.utils import timezone

PACKAGES = [
    ('PKG001', 'Basic 5Mbps',        Decimal('999')),
    ('PKG002', 'Standard 10Mbps',    Decimal('1499')),
    ('PKG003', 'Premium 20Mbps',     Decimal('2499')),
    ('PKG004', 'Business 50Mbps',    Decimal('4999')),
    ('PKG005', 'Enterprise 100Mbps', Decimal('9999')),
]

VENDORS = ['Safaricom', 'Kenya Power', 'Zuku', 'Liquid Telecom',
           'Microsoft', 'Google', 'AWS', 'Local Supplier', 'Airtel']

EXPENSE_CATEGORIES = ['network', 'maintenance', 'salaries', 'marketing',
                      'office', 'utility', 'software', 'travel', 'other']

CHURN_FACTORS = [
    'No session in 14+ days', 'No session in 30+ days',
    '2 late payments (90d)', '3 billing disputes (90d)',
    'Downgraded package last month', 'Support tickets increasing',
    'Usage below package tier', 'Payment method changed',
]

FIRST_NAMES = ['James', 'Mary', 'John', 'Patricia', 'Robert', 'Jennifer',
               'Michael', 'Linda', 'William', 'Barbara', 'David', 'Susan',
               'Richard', 'Jessica', 'Joseph', 'Sarah', 'Thomas', 'Karen']

LAST_NAMES = ['Kamau', 'Wanjiku', 'Ochieng', 'Mwangi', 'Njoroge', 'Otieno',
              'Kariuki', 'Mutua', 'Kimani', 'Waweru', 'Gitau', 'Ndungu',
              'Mugo', 'Kiprotich', 'Achieng', 'Wekesa', 'Chebet', 'Rotich']


def rand_dt(days_ago_max=45, days_ago_min=0):
    """Random datetime within the last N days"""
    days = random.randint(days_ago_min, days_ago_max)
    hours = random.randint(0, 23)
    minutes = random.randint(0, 59)
    return timezone.now() - timedelta(days=days, hours=hours, minutes=minutes)


def rand_date(days_ago_max=45, days_ago_min=0):
    return rand_dt(days_ago_max, days_ago_min).date()


class Command(BaseCommand):
    help = 'Seed all finance models with 45 days of random data'

    def add_arguments(self, parser):
        parser.add_argument('--customers',      type=int, default=60,  help='Number of customers (default: 60)')
        parser.add_argument('--transactions',   type=int, default=300, help='TransactionQueue records (default: 300)')
        parser.add_argument('--payments',       type=int, default=150, help='PaymentTransaction records (default: 150)')
        parser.add_argument('--expenses',       type=int, default=120, help='Expense records (default: 120)')
        parser.add_argument('--churn',          type=int, default=50,  help='ChurnPrediction records (default: 50)')
        parser.add_argument('--investments',    type=int, default=5,   help='Investment records (default: 5)')
        parser.add_argument('--recon-jobs',     type=int, default=4,   help='ReconciliationJob records (default: 4)')
        parser.add_argument('--clear',          action='store_true',   help='Clear existing seeded data first')

    def handle(self, *args, **options):
        if options['clear']:
            self._clear()

        self.stdout.write('🌱 Seeding finance data (45-day window)...\n')

        currency = self._seed_currency()
        gateway  = self._seed_gateway(currency)
        depts    = self._seed_departments()
        self._seed_budget_categories(depts)
        customers = self._seed_customers(options['customers'])
        self._seed_transaction_queues(options['transactions'], customers)
        self._seed_payment_transactions(options['payments'], customers, currency, gateway)
        self._seed_expenses(options['expenses'], depts, currency)
        self._seed_investments(options['investments'], currency)
        self._seed_churn_predictions(options['churn'], customers)
        self._seed_retention_tasks(customers)
        self._seed_reconciliation(options['recon_jobs'])
        self._seed_cashflow_forecasts()
        self._seed_revenue_streams()
        self._seed_kpi_snapshot()

        self.stdout.write(self.style.SUCCESS(
            f'\n✅ Done! Seeded:\n'
            f'   {options["customers"]} customers\n'
            f'   {options["transactions"]} transaction queue records\n'
            f'   {options["payments"]} payment transactions\n'
            f'   {options["expenses"]} expenses\n'
            f'   {options["churn"]} churn predictions\n'
            f'   {options["investments"]} investments\n'
            f'   {options["recon_jobs"]} reconciliation jobs\n'
            f'   Cash flow forecasts (45-day history for Prophet)\n'
        ))

    # ─── CLEAR ────────────────────────────────────────────────────────────────

    def _clear(self):
        from finance.models import (
            Expense, Department, BudgetCategory, TransactionQueue,
            PaymentTransaction, Investment, RevenueStream
        )
        from finance.models_churn import ChurnPrediction, RetentionTask
        from finance.models_cashflow import CashFlowForecast, CashFlowAlert
        from finance.models_reconciliation import ReconciliationJob, ReconciliationMatch
        from finance.models_kpi import KPISnapshot, WeeklySummary

        for model in [ChurnPrediction, RetentionTask, ReconciliationMatch,
                      ReconciliationJob, CashFlowAlert, CashFlowForecast,
                      KPISnapshot, WeeklySummary, Expense, BudgetCategory,
                      Department, Investment, RevenueStream,
                      TransactionQueue, PaymentTransaction]:
            count = model.objects.count()
            model.objects.all().delete()
            self.stdout.write(f'   🗑️  Cleared {count} {model.__name__} records')

    # ─── CURRENCY & GATEWAY ───────────────────────────────────────────────────

    def _seed_currency(self):
        from finance.models import Currency
        currency, _ = Currency.objects.get_or_create(
            code='KES',
            defaults={
                'name': 'Kenyan Shilling', 'symbol': 'KSh',
                'is_base_currency': True, 'is_active': True
            }
        )
        self.stdout.write('💱 Currency: KES')
        return currency

    def _seed_gateway(self, currency):
        from finance.models import PaymentGateway
        gateway = PaymentGateway.objects.filter(gateway_type='mpesa').first()
        if not gateway:
            try:
                gateway = PaymentGateway.objects.create(
                    name='M-Pesa', gateway_type='mpesa',
                    is_default=True, default_currency=currency,
                    config={
                        'consumer_key': 'seed_key', 'consumer_secret': 'seed_secret',
                        'shortcode': '174379', 'lipa_na_mpesa_passkey': 'seed_passkey'
                    },
                    test_mode=True
                )
            except Exception:
                gateway = None
        self.stdout.write('💳 Gateway: M-Pesa')
        return gateway

    # ─── DEPARTMENTS & BUDGETS ────────────────────────────────────────────────

    def _seed_departments(self):
        from finance.models import Department
        dept_data = [
            ('OPS',  'Operations',       Decimal('150000')),
            ('TECH', 'Technology',        Decimal('200000')),
            ('MKT',  'Marketing',         Decimal('80000')),
            ('HR',   'Human Resources',   Decimal('120000')),
            ('FIN',  'Finance',           Decimal('60000')),
        ]
        depts = []
        for code, name, budget in dept_data:
            dept, _ = Department.objects.get_or_create(
                code=code, defaults={'name': name, 'budget': budget, 'is_active': True}
            )
            depts.append(dept)
        self.stdout.write(f'🏢 Departments: {len(depts)}')
        return depts

    def _seed_budget_categories(self, depts):
        from finance.models import BudgetCategory
        cats = {
            'OPS':  [('Network Equipment', 80000), ('Maintenance', 40000), ('Utilities', 30000)],
            'TECH': [('Software Licenses', 60000), ('Cloud Services', 80000), ('Hardware', 60000)],
            'MKT':  [('Digital Ads', 40000), ('Events', 20000), ('Content', 20000)],
            'HR':   [('Salaries', 100000), ('Training', 20000)],
            'FIN':  [('Accounting', 30000), ('Compliance', 30000)],
        }
        year = timezone.now().year
        for dept in depts:
            for name, amount in cats.get(dept.code, []):
                BudgetCategory.objects.get_or_create(
                    name=name, department=dept, fiscal_year=year,
                    defaults={'planned_amount': Decimal(str(amount)), 'is_active': True}
                )
        self.stdout.write('📋 Budget categories seeded')

    # ─── CUSTOMERS ────────────────────────────────────────────────────────────

    def _seed_customers(self, count):
        from django.contrib.auth.models import User
        from users.models import ClientH
        from locations.models import Location

        existing = list(ClientH.objects.all())
        if len(existing) >= count:
            self.stdout.write(f'👥 Using {count} existing customers')
            return existing[:count]

        locations = list(Location.objects.all())
        if not locations:
            self.stdout.write(self.style.WARNING('⚠️  No locations found — skipping customer creation'))
            return existing

        needed = count - len(existing)
        created = []
        for i in range(needed):
            fname = random.choice(FIRST_NAMES)
            lname = random.choice(LAST_NAMES)
            username = f'cust_{uuid.uuid4().hex[:8]}'
            try:
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@example.com',
                    password='seed1234',
                    first_name=fname,
                    last_name=lname,
                )
                last = ClientH.objects.order_by('-account').first()
                try:
                    num = int(last.account.replace('CLI', '')) + 1 if last else len(existing) + len(created) + 1
                except (ValueError, AttributeError):
                    num = len(existing) + len(created) + 1

                c = ClientH.objects.create(
                    user=user,
                    account=f'CLI{num:06d}',
                    status=random.choices(['active', 'inactive'], weights=[85, 15])[0],
                    balance=Decimal(str(random.randint(0, 5000))),
                    credit_limit=Decimal('0'),
                    total_spent=Decimal(str(random.randint(0, 50000))),
                    lifetime_data_used=random.randint(0, 100000),
                    failed_login_attempts=0,
                    two_factor_enabled=False,
                    auto_renew=random.choice([True, False]),
                    reward_points=random.randint(0, 500),
                    reward_tier='bronze',
                    total_points_earned=random.randint(0, 500),
                    total_points_redeemed=0,
                    home_location=random.choice(locations),
                )
                created.append(c)
            except Exception as e:
                pass

        all_customers = existing + created
        self.stdout.write(f'👥 Customers: {len(all_customers)} ({len(created)} new)')
        return all_customers

    # ─── TRANSACTION QUEUE ────────────────────────────────────────────────────

    def _seed_transaction_queues(self, count, customers):
        from finance.models import TransactionQueue
        if not customers:
            return

        statuses = ['completed', 'completed', 'completed', 'completed',
                    'processed', 'failed', 'pending']
        created = 0
        from django.db import connection
        for _ in range(count):
            customer = random.choice(customers)
            pkg_code, pkg_name, price = random.choice(PACKAGES)
            dt = rand_dt(45)
            phone = customer.phone_number or f'2547{random.randint(10000000,99999999)}'
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO finance_transactionqueue
                        (created_at, updated_at, queue_type, method, initiator,
                         checkout_request_id, package_code, package, price, status,
                         account_reference, used_credit, failure_reason, error_code,
                         failure_category, retry_count, max_retries, last_retry_at,
                         priority, expires_at, pending_timeout_hours,
                         gateway_result_data, metadata, completed_at, failed_at, user_id)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        [dt, dt, 'payment_processing', 'mpesa', phone,
                         None, pkg_code, pkg_name, float(price),
                         random.choice(statuses), customer.account, None,
                         '', '', '', 0, 3, None, 'normal', None, 24,
                         '{}', '{}', None, None, customer.id]
                    )
                created += 1
            except Exception:
                pass

        self.stdout.write(f'📥 TransactionQueue: {created}')

    # ─── PAYMENT TRANSACTIONS ─────────────────────────────────────────────────

    def _seed_payment_transactions(self, count, customers, currency, gateway):
        from finance.models import PaymentTransaction
        if not customers:
            return

        created = 0
        from django.db import connection
        gw_id = gateway.id if gateway else None
        cur_id = currency.id
        for _ in range(count):
            customer = random.choice(customers)
            _, _, price = random.choice(PACKAGES)
            dt = rand_dt(45)
            phone = customer.phone_number or f'2547{random.randint(10000000,99999999)}'
            txn_id = f'TXN_{uuid.uuid4().hex[:12].upper()}'
            gw_ref = f'MP{random.randint(100000000, 999999999)}'
            try:
                with connection.cursor() as cursor:
                    cursor.execute(
                        """INSERT INTO finance_paymenttransaction
                        (created_at, updated_at, transaction_id, user_id, payment_method,
                         payment_gateway_id, amount, currency_id, exchange_rate, amount_base,
                         initiator, balance, date, result_code, result_desc,
                         merchant_request_id, checkout_request_id, transaction_time,
                         gateway_reference, account_reference, raw_callback_data,
                         status, description)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        [dt, dt, txn_id, customer.id, 'mpesa',
                         gw_id, float(price), cur_id, 1.0, float(price),
                         phone, None, None, 0, '',
                         '', '', dt,
                         gw_ref, customer.account, '{}',
                         'completed', '']
                    )
                created += 1
            except Exception:
                pass

        self.stdout.write(f'💰 PaymentTransactions: {created}')

    # ─── EXPENSES ─────────────────────────────────────────────────────────────

    def _seed_expenses(self, count, depts, currency):
        from finance.models import Expense, BudgetCategory
        if not depts:
            return

        approval_statuses = ['draft', 'submitted', 'approved', 'paid', 'paid', 'paid']
        created = 0
        for _ in range(count):
            dept = random.choice(depts)
            cat  = random.choice(EXPENSE_CATEGORIES)
            exp_date = rand_date(45)
            amount = Decimal(str(random.randint(500, 50000)))

            budget_cat = BudgetCategory.objects.filter(department=dept).first()

            try:
                Expense.objects.create(
                    expense_date=exp_date,
                    description=f'{cat.title()} expense - {random.choice(VENDORS)}',
                    amount=amount,
                    currency=currency,
                    category=cat,
                    vendor=random.choice(VENDORS),
                    department=dept,
                    budget_category=budget_cat,
                    approval_status=random.choice(approval_statuses),
                    is_recurring=random.random() < 0.15,
                    is_capex=random.random() < 0.10,
                    vat_rate=Decimal('16.0'),
                )
                created += 1
            except Exception:
                pass

        self.stdout.write(f'🧾 Expenses: {created}')

    # ─── INVESTMENTS ──────────────────────────────────────────────────────────

    def _seed_investments(self, count, currency):
        from finance.models import Investment
        types    = ['seed', 'loan', 'personal', 'equity']
        statuses = ['active', 'disbursed', 'proposed']
        created  = 0
        for i in range(count):
            try:
                Investment.objects.create(
                    investor_name=f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}',
                    investment_date=rand_date(365, 30),
                    amount=Decimal(str(random.randint(100000, 2000000))),
                    currency=currency,
                    investment_type=random.choice(types),
                    investment_status=random.choice(statuses),
                    description=f'Investment round {i + 1}',
                )
                created += 1
            except Exception:
                pass
        self.stdout.write(f'📈 Investments: {created}')

    # ─── CHURN PREDICTIONS ────────────────────────────────────────────────────

    def _seed_churn_predictions(self, count, customers):
        from finance.models_churn import ChurnPrediction
        if not customers:
            return

        risk_weights = {'low': 40, 'medium': 30, 'high': 20, 'critical': 10}
        risk_levels  = list(risk_weights.keys())
        risk_probs   = [v / 100 for v in risk_weights.values()]

        sample   = random.sample(customers, min(count, len(customers)))
        created  = 0
        for customer in sample:
            risk  = random.choices(risk_levels, weights=list(risk_weights.values()))[0]
            score = {
                'low':      random.uniform(0.05, 0.29),
                'medium':   random.uniform(0.30, 0.54),
                'high':     random.uniform(0.55, 0.74),
                'critical': random.uniform(0.75, 0.95),
            }[risk]
            mrr = Decimal(str(random.choice([p for _, _, p in PACKAGES])))
            try:
                ChurnPrediction.objects.update_or_create(
                    customer=customer,
                    defaults={
                        'churn_score': round(score, 4),
                        'risk_level': risk,
                        'prediction_method': 'rule_based',
                        'monthly_recurring_revenue': mrr,
                        
                        'top_factors': random.sample(CHURN_FACTORS, random.randint(2, 4)),
                        'risk_factors': {f: round(random.uniform(0.1, 0.4), 2) for f in random.sample(CHURN_FACTORS, 3)},
                        'days_since_last_session': random.randint(1, 60),
                        'late_payments_count': random.randint(0, 4),
                        'support_tickets_90d': random.randint(0, 5),
                        'package_downgrades_count': random.randint(0, 2),
                        'is_active': True,
                        'confidence': round(random.uniform(0.6, 0.95), 2),
                    }
                )
                created += 1
            except Exception:
                pass
        self.stdout.write(f'🔮 ChurnPredictions: {created}')

    # ─── RETENTION TASKS ──────────────────────────────────────────────────────

    def _seed_retention_tasks(self, customers):
        from finance.models_churn import ChurnPrediction, RetentionTask

        high_risk = ChurnPrediction.objects.filter(risk_level__in=['high', 'critical'])
        created   = 0
        for pred in high_risk[:20]:
            mrr = pred.monthly_recurring_revenue or Decimal('1000')
            if mrr >= Decimal('5000'):
                action = 'auto_discount_20'
            elif mrr >= Decimal('2000'):
                action = 'sms_discount_10'
            else:
                action = 'sms_reengagement'

            priority = float(min(mrr, Decimal('10000')) / Decimal('10000')) * 0.6 + pred.churn_score * 0.4

            try:
                RetentionTask.objects.get_or_create(
                    customer=pred.customer,
                    churn_prediction=pred,
                    defaults={
                        'action_type': action,
                        'status': random.choice(['pending', 'completed', 'in_progress']),
                        'priority_score': round(priority, 4),
                        'monthly_recurring_revenue': mrr,
                        'revenue_at_risk': mrr * Decimal('6'),
                        'outcome': random.choice(['pending', 'retained', 'churned', 'pending', 'pending']),
                        'automated': True,
                    }
                )
                created += 1
            except Exception:
                pass
        self.stdout.write(f'📋 RetentionTasks: {created}')

    # ─── RECONCILIATION ───────────────────────────────────────────────────────

    def _seed_reconciliation(self, job_count):
        from finance.models_reconciliation import ReconciliationJob, ReconciliationMatch

        created_jobs = 0
        for i in range(job_count):
            days_ago     = random.randint(5, 40)
            period_start = rand_date(days_ago + 14, days_ago + 14)
            period_end   = rand_date(days_ago, days_ago)
            total        = random.randint(40, 120)
            matched      = int(total * random.uniform(0.70, 0.90))
            review       = int(total * random.uniform(0.05, 0.15))
            unmatched    = total - matched - review

            try:
                job = ReconciliationJob.objects.create(
                    job_id=f'RECON-{uuid.uuid4().hex[:8].upper()}',
                    status='completed',
                    period_start=period_start,
                    period_end=period_end,
                    total_items=total,
                    matched_items=matched,
                    review_items=review,
                    unmatched_items=max(unmatched, 0),
                    auto_match_rate=round(matched / total * 100, 1),
                    average_confidence=round(random.uniform(0.75, 0.92), 2),
                )
                created_jobs += 1

                # Seed review-queue matches
                for _ in range(review):
                    ReconciliationMatch.objects.create(
                        job=job,
                        source_reference=f'REF{random.randint(100000, 999999)}',
                        source_amount=Decimal(str(random.choice([p for _, _, p in PACKAGES]))),
                        source_date=period_start + timedelta(days=random.randint(0, 14)),
                        source_customer_info=f'{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}',
                        confidence_score=round(random.uniform(0.60, 0.84), 2),
                        amount_match_score=round(random.uniform(0.5, 1.0), 2),
                        customer_match_score=round(random.uniform(0.4, 0.9), 2),
                        date_match_score=round(random.uniform(0.5, 1.0), 2),
                        match_action='review',
                        status='pending',
                    )
            except Exception:
                pass

        self.stdout.write(f'🔄 ReconciliationJobs: {created_jobs}')

    # ─── CASH FLOW FORECASTS (45-day history for Prophet) ─────────────────────

    def _seed_cashflow_forecasts(self):
        from finance.models_cashflow import CashFlowForecast

        today = timezone.now().date()
        scenarios = ['optimistic', 'base', 'conservative']
        multipliers = {'optimistic': 1.15, 'base': 1.0, 'conservative': 0.85}

        # Base daily revenue (realistic ISP numbers)
        base_daily_revenue = 45000
        base_daily_expense = 28000

        created = 0
        for scenario in scenarios:
            mult = multipliers[scenario]

            # Build 45 days of historical + 30 days forecast
            forecast_data = []
            for day_offset in range(-45, 31):
                target_date = today + timedelta(days=day_offset)
                # Add weekly seasonality (lower on weekends)
                weekday_factor = 0.75 if target_date.weekday() >= 5 else 1.0
                # Add monthly seasonality (spike at month end)
                month_end_factor = 1.3 if target_date.day >= 25 else 1.0

                value = base_daily_revenue * mult * weekday_factor * month_end_factor
                value += random.uniform(-3000, 3000)  # noise

                forecast_data.append({
                    'date': target_date.isoformat(),
                    'value': round(value, 2),
                    'lower_bound': round(value * 0.85, 2),
                    'upper_bound': round(value * 1.15, 2),
                })

            total = sum(d['value'] for d in forecast_data if d['date'] >= today.isoformat())
            avg   = total / 30 if total else 0

            try:
                CashFlowForecast.objects.update_or_create(
                    forecast_date=today,
                    forecast_type='revenue',
                    scenario=scenario,
                    horizon_days=30,
                    defaults={
                        'period_start': today,
                        'period_end': today + timedelta(days=30),
                        'forecast_data': forecast_data,
                        'total_forecasted': Decimal(str(round(total, 2))),
                        'average_daily': Decimal(str(round(avg, 2))),
                        'training_data_size': 45,
                        'training_period_days': 45,
                        'has_weekly_seasonality': True,
                        'has_monthly_seasonality': True,
                        'model_accuracy': round(random.uniform(0.82, 0.94), 3),
                        'confidence_interval': 0.95,
                        'is_active': True,
                        'projected_balance': Decimal(str(round(total - base_daily_expense * 30, 2))),
                        'confidence_score': round(random.uniform(0.80, 0.95), 2),
                    }
                )
                created += 1
            except Exception as e:
                # projected_balance may not exist on model — try without it
                try:
                    CashFlowForecast.objects.update_or_create(
                        forecast_date=today,
                        forecast_type='revenue',
                        scenario=scenario,
                        horizon_days=30,
                        defaults={
                            'period_start': today,
                            'period_end': today + timedelta(days=30),
                            'forecast_data': forecast_data,
                            'total_forecasted': Decimal(str(round(total, 2))),
                            'average_daily': Decimal(str(round(avg, 2))),
                            'training_data_size': 45,
                            'training_period_days': 45,
                            'has_weekly_seasonality': True,
                            'has_monthly_seasonality': True,
                            'model_accuracy': round(random.uniform(0.82, 0.94), 3),
                            'confidence_interval': 0.95,
                            'is_active': True,
                        }
                    )
                    created += 1
                except Exception:
                    pass

        self.stdout.write(f'📊 CashFlowForecasts: {created} (3 scenarios × 75 days)')

    # ─── REVENUE STREAMS ──────────────────────────────────────────────────────

    def _seed_revenue_streams(self):
        from finance.models import RevenueStream
        streams = [
            ('Voucher Sales',    'voucher_sales',  Decimal('500000')),
            ('Package Sales',    'package_sales',  Decimal('800000')),
            ('Premium Services', 'premium_services', Decimal('200000')),
        ]
        created = 0
        for name, cat, target in streams:
            _, made = RevenueStream.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat,
                    'target_revenue': target,
                    'is_active': True,
                    'display_order': created,
                }
            )
            if made:
                created += 1
        self.stdout.write(f'💹 RevenueStreams: {created} new')

    # ─── KPI SNAPSHOT ─────────────────────────────────────────────────────────

    def _seed_kpi_snapshot(self):
        from finance.kpi_service import KPICalculationService
        try:
            snap = KPICalculationService.generate_kpi_snapshot()
            self.stdout.write(f'🎯 KPI snapshot generated ({snap.computed_in_ms}ms)')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  KPI snapshot skipped: {e}'))
