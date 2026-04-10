"""
Dev Data Seeder
Seeds realistic ISP finance data for development and testing.
Generates 60+ days of historical data required for Prophet forecasting.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from decimal import Decimal
import random
import uuid
from datetime import timedelta, date

User = get_user_model()

PACKAGE_PRICES = [8, 15, 20, 30, 50, 100, 200, 500, 1000]


class Command(BaseCommand):
    help = 'Seed dev data: gateways, departments, budgets, transactions, expenses, churn, forecasts, KPIs'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=60, help='Days of historical data (default: 60)')
        parser.add_argument('--clear', action='store_true', help='Clear existing finance data before seeding')

    def handle(self, *args, **options):
        days = options['days']
        self.stdout.write(self.style.SUCCESS(f'\n=== TeralinkX Dev Data Seeder ({days} days) ===\n'))

        if options['clear']:
            self._clear_data()

        with transaction.atomic():
            currency   = self._seed_currency()
            gateway    = self._seed_gateway(currency)
            depts      = self._seed_departments()
            budgets    = self._seed_budget_categories(depts)
            self._seed_revenue_streams()
            from users.models import ClientH
            clients    = list(ClientH.objects.select_related('user').all()[:50])
            users      = list(User.objects.filter(is_staff=True)[:5])  # for expenses/admin
            self._seed_transactions(clients, currency, gateway, days)
            self._seed_expenses(depts, budgets, currency, days)
            self._seed_churn_predictions(clients)
            self._seed_cash_flow_forecasts(days)
            self._seed_kpi_snapshots(days)
            self._seed_weekly_summaries(days)
            self._bump_timescale_rollout()

        self.stdout.write(self.style.SUCCESS('\n✅ Seeding complete!\n'))

    # ── helpers ──────────────────────────────────────────────────────────────

    def _clear_data(self):
        from finance.models import PaymentTransaction, Expense, PaymentGateway, Department, BudgetCategory, RevenueStream
        from finance.models_churn import ChurnPrediction, RetentionTask
        from finance.models_cashflow import CashFlowForecast, CashFlowAlert
        from finance.models_kpi import KPISnapshot, WeeklySummary
        self.stdout.write('Clearing existing finance data...')
        for M in [RetentionTask, ChurnPrediction, CashFlowAlert, CashFlowForecast,
                  KPISnapshot, WeeklySummary, PaymentTransaction, Expense,
                  BudgetCategory, Department, RevenueStream, PaymentGateway]:
            n = M.objects.count()
            M.objects.all().delete()
            self.stdout.write(f'  deleted {n} {M.__name__}')

    # ── currency & gateway ────────────────────────────────────────────────────

    def _seed_currency(self):
        from finance.models import Currency
        c, _ = Currency.objects.get_or_create(
            code='KES',
            defaults={'name': 'Kenyan Shilling', 'symbol': 'KES', 'is_base': True, 'exchange_rate': Decimal('1.0')}
        )
        self.stdout.write(f'  ✓ Currency: {c.code}')
        return c

    def _seed_gateway(self, currency):
        from finance.models import PaymentGateway
        if PaymentGateway.objects.exists():
            gw = PaymentGateway.objects.first()
            self.stdout.write(f'  ✓ Gateway: {gw.name} (existing)')
            return gw
        gw = PaymentGateway.objects.create(
            name='M-Pesa', gateway_type='mpesa', status='active',
            is_default=True, test_mode=True, default_currency=currency,
            callback_url='https://srv.teralinkxwaves.uk/api/finance/mpesa/callback/',
            webhook_url='https://srv.teralinkxwaves.uk/api/finance/mpesa/webhook/',
            config={'shortcode': '174379', 'lipa_na_mpesa_passkey': 'dev_passkey',
                    'consumer_key': 'dev_key', 'consumer_secret': 'dev_secret'},
        )
        self.stdout.write(f'  ✓ Gateway: {gw.name}')
        return gw

    # ── departments & budgets ─────────────────────────────────────────────────

    def _seed_departments(self):
        from finance.models import Department
        admin = User.objects.filter(is_staff=True).first()
        data = [
            ('Operations', 'OPS', 500000),
            ('Network', 'NET', 800000),
            ('Customer Support', 'CS', 300000),
            ('Sales & Marketing', 'SM', 400000),
            ('Finance', 'FIN', 200000),
        ]
        depts = []
        for name, code, budget in data:
            d, _ = Department.objects.get_or_create(
                code=code,
                defaults={'name': name, 'budget': Decimal(budget), 'is_active': True, 'manager': admin}
            )
            depts.append(d)
        self.stdout.write(f'  ✓ Departments: {len(depts)}')
        return depts

    def _seed_budget_categories(self, depts):
        from finance.models import BudgetCategory
        year = timezone.now().year
        data = [
            ('Bandwidth & Transit', depts[1], 600000),
            ('Staff Salaries',      depts[0], 1200000),
            ('Equipment & Hardware',depts[1], 400000),
            ('Office & Utilities',  depts[4], 150000),
            ('Marketing Campaigns', depts[3], 250000),
            ('Customer Support Tools', depts[2], 100000),
            ('Software Licenses',   depts[0], 80000),
            ('Vehicle & Transport', depts[0], 120000),
        ]
        cats = []
        for name, dept, amount in data:
            c, _ = BudgetCategory.objects.get_or_create(
                name=name, fiscal_year=year,
                defaults={'department': dept, 'planned_amount': Decimal(amount), 'is_active': True}
            )
            cats.append(c)
        self.stdout.write(f'  ✓ Budget categories: {len(cats)}')
        return cats

    # ── revenue streams ───────────────────────────────────────────────────────

    def _seed_revenue_streams(self):
        from finance.models import RevenueStream
        data = [
            ('Hotspot Packages',      'hotspot_packages', 1500000, 800),
            ('Home Fiber',            'home_fiber',        800000, 200),
            ('Business Leased Lines', 'business_leased',   600000,  50),
            ('SMS Bundles',           'sms_bundles',       100000, 500),
        ]
        for name, cat, target, customers in data:
            RevenueStream.objects.get_or_create(
                name=name,
                defaults={
                    'category': cat, 'is_active': True,
                    'target_revenue': Decimal(target),
                    'target_growth_rate': Decimal('5.0'),
                    'target_customers': customers,
                    'average_revenue_per_user': Decimal(target) / customers,
                    'display_order': data.index((name, cat, target, customers)) + 1,
                    'kpis': {},
                }
            )
        self.stdout.write(f'  ✓ Revenue streams: {len(data)}')

    # ── transactions ──────────────────────────────────────────────────────────

    def _seed_transactions(self, clients, currency, gateway, days):
        from finance.models import PaymentTransaction
        if PaymentTransaction.objects.count() > 100:
            self.stdout.write(f'  ✓ Transactions: already seeded ({PaymentTransaction.objects.count()})')
            return

        now = timezone.now()
        txns = []
        for day_offset in range(days, 0, -1):
            day = now - timedelta(days=day_offset)
            weekday = day.weekday()
            multiplier = 1.3 if weekday < 5 else 0.7
            growth = 1 + (days - day_offset) * 0.002
            daily_target = 45000 * multiplier * growth
            n = random.randint(8, 25)
            amounts = self._split_amount(daily_target, n)

            for amount in amounts:
                client = random.choice(clients)
                method = random.choices(['mpesa', 'balance', 'cash'], weights=[70, 20, 10])[0]
                txn_time = day.replace(
                    hour=random.randint(7, 22),
                    minute=random.randint(0, 59),
                    second=0, microsecond=0
                )
                txns.append(PaymentTransaction(
                    transaction_id=f'TXN{uuid.uuid4().hex[:12].upper()}',
                    payment_method=method,
                    amount=Decimal(str(round(amount, 2))),
                    exchange_rate=Decimal('1.0'),
                    amount_base=Decimal(str(round(amount, 2))),
                    initiator=client.user.username,
                    result_code=0,
                    result_desc='Success',
                    merchant_request_id=f'MR{uuid.uuid4().hex[:8].upper()}',
                    checkout_request_id=f'CR{uuid.uuid4().hex[:8].upper()}',
                    transaction_time=txn_time,
                    gateway_reference=f'GW{uuid.uuid4().hex[:8].upper()}',
                    raw_callback_data={},
                    status='completed',
                    description='Package purchase',
                    currency=currency,
                    payment_gateway=gateway if method == 'mpesa' else None,
                    user=client,
                    account_reference=client.user.username,
                    created_at=txn_time,
                ))

        PaymentTransaction.objects.bulk_create(txns, batch_size=200)
        self.stdout.write(f'  ✓ Transactions: {len(txns)} over {days} days')

    # ── expenses ──────────────────────────────────────────────────────────────

    def _seed_expenses(self, depts, budgets, currency, days):
        from finance.models import Expense
        if Expense.objects.count() > 50:
            self.stdout.write(f'  ✓ Expenses: already seeded ({Expense.objects.count()})')
            return

        now = timezone.now()
        admin = User.objects.filter(is_staff=True).first()
        monthly = [
            ('Safaricom bandwidth invoice', 'bandwidth',  'Safaricom',   180000),
            ('Staff salaries',              'salaries',   'Internal',    350000),
            ('Office rent',                 'rent',       'Landlord Ltd', 35000),
            ('Electricity bill',            'utilities',  'KPLC',         18000),
            ('Water bill',                  'utilities',  'Nairobi Water', 3500),
        ]
        weekly = [
            ('Mikrotik equipment',       'equipment',  'Westgate IT', 45000),
            ('Marketing - Facebook Ads', 'marketing',  'Meta',         15000),
            ('Fuel & transport',         'transport',  'Shell Kenya',  12000),
            ('Software licenses',        'software',   'Various',       8000),
        ]
        expenses = []
        for day_offset in range(days, 0, -1):
            exp_date = (now - timedelta(days=day_offset)).date()
            if exp_date.day == 1:
                for desc, cat, vendor, base in monthly:
                    expenses.append(self._make_expense(
                        exp_date, desc, cat, vendor,
                        base * random.uniform(0.95, 1.05),
                        currency, depts, budgets, admin, day_offset, recurring=True
                    ))
            if exp_date.weekday() == 0:
                desc, cat, vendor, base = random.choice(weekly)
                expenses.append(self._make_expense(
                    exp_date, desc, cat, vendor,
                    base * random.uniform(0.8, 1.2),
                    currency, depts, budgets, admin, day_offset
                ))

        Expense.objects.bulk_create(expenses, batch_size=200)
        self.stdout.write(f'  ✓ Expenses: {len(expenses)}')

    def _make_expense(self, exp_date, desc, cat, vendor, amount, currency, depts, budgets, admin, day_offset, recurring=False):
        from finance.models import Expense
        return Expense(
            expense_date=exp_date,
            description=desc,
            amount=Decimal(str(round(amount, 2))),
            category=cat,
            vendor=vendor,
            approval_status='approved',
            is_recurring=recurring,
            is_tax_deductible=True,
            tax_amount=Decimal('0'),
            vat_rate=Decimal('16.0'),
            invoice_number=f'INV-{exp_date.strftime("%Y%m%d")}-{random.randint(10,999)}',
            is_capex=False,
            asset_life_years=0,
            depreciation_method='none',
            currency=currency,
            department=random.choice(depts),
            budget_category=random.choice(budgets) if budgets else None,
            submitted_by=admin,
            approved_by=admin,
            submitted_at=timezone.now() - timedelta(days=day_offset),
            approved_at=timezone.now() - timedelta(days=day_offset - 1),
        )

    # ── churn predictions ─────────────────────────────────────────────────────

    def _seed_churn_predictions(self, clients):
        from finance.models_churn import ChurnPrediction
        if ChurnPrediction.objects.count() > 10:
            self.stdout.write(f'  ✓ Churn predictions: already seeded ({ChurnPrediction.objects.count()})')
            return

        risk_bands = [
            ('low',      0.05, 0.25),
            ('medium',   0.25, 0.55),
            ('high',     0.55, 0.75),
            ('critical', 0.75, 0.95),
        ]
        preds = []
        for client in clients:
            level, lo, hi = random.choices(risk_bands, weights=[50, 30, 15, 5])[0]
            score = round(random.uniform(lo, hi), 4)
            days_inactive = random.randint(1, 45)
            mrr = round(random.uniform(200, 2000), 2)
            preds.append(ChurnPrediction(
                customer=client,
                churn_score=score,
                risk_level=level,
                prediction_method='rule_based',
                risk_factors={
                    'days_inactive': days_inactive,
                    'late_payments': random.randint(0, 3),
                    'support_tickets': random.randint(0, 5),
                },
                top_factors=[
                    f'Inactive {days_inactive} days',
                    f'MRR KES {mrr}',
                    f'Risk: {level}',
                ],
                days_since_last_session=days_inactive,
                support_tickets_90d=random.randint(0, 5),
                late_payments_count=random.randint(0, 3),
                package_downgrades_count=random.randint(0, 2),
                avg_session_duration_minutes=round(random.uniform(5, 120), 1),
                monthly_recurring_revenue=Decimal(str(mrr)),
                is_active=True,
                confidence=round(random.uniform(0.7, 0.95), 4),
            ))

        ChurnPrediction.objects.bulk_create(preds, batch_size=100)
        self.stdout.write(f'  ✓ Churn predictions: {len(preds)}')

    # ── cash flow forecasts (Prophet-ready) ───────────────────────────────────

    def _seed_cash_flow_forecasts(self, days):
        from finance.models_cashflow import CashFlowForecast
        if CashFlowForecast.objects.count() > 10:
            self.stdout.write(f'  ✓ Cash flow forecasts: already seeded')
            return

        now = timezone.now()
        base_rev = 1500000
        base_exp = 900000
        forecasts = []

        for forecast_type, scenario in [
            ('revenue',       'base'),
            ('revenue',       'optimistic'),
            ('revenue',       'conservative'),
            ('expense',       'base'),
            ('net_cash_flow', 'base'),
        ]:
            period_start = now.date()
            period_end   = (now + timedelta(days=90)).date()
            multiplier   = {'optimistic': 1.15, 'base': 1.0, 'conservative': 0.85}[scenario]

            daily_data = []
            for i in range(90):
                d = (now + timedelta(days=i)).date()
                growth = 1 + i * 0.001
                if forecast_type == 'revenue':
                    val = base_rev * growth * multiplier * random.uniform(0.95, 1.05) / 30
                elif forecast_type == 'expense':
                    val = base_exp * random.uniform(0.95, 1.05) / 30
                else:
                    rev = base_rev * growth / 30
                    val = rev - base_exp / 30
                daily_data.append({
                    'date': str(d),
                    'value': round(val, 2),
                    'lower_bound': round(val * 0.85, 2),
                    'upper_bound': round(val * 1.15, 2),
                })

            total = sum(d['value'] for d in daily_data)
            forecasts.append(CashFlowForecast(
                forecast_date=now.date(),
                forecast_type=forecast_type,
                scenario=scenario,
                period_start=period_start,
                period_end=period_end,
                horizon_days=90,
                forecast_data=daily_data,
                total_forecasted=Decimal(str(round(total, 2))),
                average_daily=Decimal(str(round(total / 90, 2))),
                model_accuracy=round(random.uniform(0.88, 0.96), 4),
                confidence_interval=0.95,
                training_data_size=days,
                training_period_days=days,
                has_weekly_seasonality=True,
                has_monthly_seasonality=True,
                has_yearly_seasonality=False,
                is_active=True,
            ))

        CashFlowForecast.objects.bulk_create(forecasts)
        self.stdout.write(f'  ✓ Cash flow forecasts: {len(forecasts)} scenarios')

    # ── KPI snapshots ─────────────────────────────────────────────────────────

    def _seed_kpi_snapshots(self, days):
        from finance.models_kpi import KPISnapshot
        if KPISnapshot.objects.count() > 10:
            self.stdout.write(f'  ✓ KPI snapshots: already seeded')
            return

        now = timezone.now()
        base_mrr = 1500000
        base_customers = 50
        snaps = []

        for day_offset in range(days, 0, -1):
            snap_time = now - timedelta(days=day_offset)
            growth = 1 + (days - day_offset) * 0.002
            mrr = base_mrr * growth * random.uniform(0.97, 1.03)
            customers = int(base_customers * growth)
            last_mrr = mrr * random.uniform(0.95, 0.99)
            snaps.append(KPISnapshot(
                timestamp=snap_time,
                mrr_current=Decimal(str(round(mrr, 2))),
                mrr_last_month=Decimal(str(round(last_mrr, 2))),
                mrr_target=Decimal('1800000'),
                mrr_growth_pct=Decimal(str(round((mrr - last_mrr) / last_mrr * 100, 2))),
                active_customers=customers,
                active_customers_last_month=int(customers * random.uniform(0.95, 0.99)),
                churn_rate_30d=Decimal(str(round(random.uniform(1.5, 4.5), 2))),
                new_customers_30d=random.randint(1, 8),
                cash_position=Decimal(str(round(random.uniform(800000, 2000000), 2))),
                cash_position_30d_ago=Decimal(str(round(random.uniform(700000, 1800000), 2))),
                outstanding_receivables={'0_30': float(round(random.uniform(20000, 80000), 2)), '31_60': float(round(random.uniform(10000, 40000), 2)), '60_plus': float(round(random.uniform(5000, 20000), 2))},
                total_receivables=Decimal(str(round(random.uniform(200000, 600000), 2))),
                network_uptime_7d=Decimal(str(round(random.uniform(98.5, 99.9), 2))),
                revenue_at_risk=Decimal(str(round(random.uniform(50000, 200000), 2))),
                high_risk_customers=random.randint(2, 15),
                computed_in_ms=random.randint(50, 500),
            ))

        KPISnapshot.objects.bulk_create(snaps, batch_size=100)
        self.stdout.write(f'  ✓ KPI snapshots: {len(snaps)}')

    # ── weekly summaries ──────────────────────────────────────────────────────

    def _seed_weekly_summaries(self, days):
        from finance.models_kpi import WeeklySummary
        if WeeklySummary.objects.count() > 0:
            self.stdout.write(f'  ✓ Weekly summaries: already seeded')
            return

        now = timezone.now()
        summaries = []
        for week in range(days // 7):
            week_end   = (now - timedelta(weeks=week)).date()
            week_start = week_end - timedelta(days=6)
            rev = round(random.uniform(280000, 420000), 2)
            summaries.append(WeeklySummary(
                week_start=week_start,
                week_end=week_end,
                generated_at=now - timedelta(weeks=week),
                top_wins=[
                    f'{random.randint(5,20)} new customers acquired',
                    f'KES {rev:,.0f} weekly revenue',
                    f'{round(random.uniform(98.5,99.9),1)}% network uptime',
                ],
                top_risks=[
                    f'{random.randint(1,5)} high-risk churn customers',
                    f'Bandwidth invoice due in {random.randint(3,10)} days',
                ],
                budget_status='on_track',
                budget_summary={
                    'total_budget': 2300000,
                    'spent': round(random.uniform(1500000, 2100000), 2),
                    'remaining': round(random.uniform(200000, 800000), 2),
                },
                churn_risk_summary={
                    'high_risk': random.randint(2, 10),
                    'medium_risk': random.randint(5, 20),
                    'revenue_at_risk': float(round(random.uniform(50000, 200000), 2)),
                },
                weekly_revenue=Decimal(str(rev)),
                weekly_new_customers=random.randint(3, 15),
                weekly_churned_customers=random.randint(0, 4),
            ))

        WeeklySummary.objects.bulk_create(summaries)
        self.stdout.write(f'  ✓ Weekly summaries: {len(summaries)}')

    # ── timescale rollout ─────────────────────────────────────────────────────

    def _bump_timescale_rollout(self):
        from core.models import FeatureFlag
        try:
            flag = FeatureFlag.objects.get(name='timescaledb_migration')
            old = flag.rollout_percentage
            if old < 50:
                flag.rollout_percentage = 50
                flag.save()
                self.stdout.write(f'  ✓ TimescaleDB rollout: {old}% → 50%')
            else:
                self.stdout.write(f'  ✓ TimescaleDB rollout: already at {old}%')
        except FeatureFlag.DoesNotExist:
            self.stdout.write(self.style.WARNING('  ⚠ timescaledb_migration flag not found'))

    # ── utils ─────────────────────────────────────────────────────────────────

    @staticmethod
    def _split_amount(total, n):
        amounts = []
        remaining = total
        for _ in range(n - 1):
            amt = random.choice(PACKAGE_PRICES)
            amounts.append(amt)
            remaining -= amt
        amounts.append(max(8, remaining))
        return amounts
