#!/usr/bin/env python
"""
Database Seed Script for TeralinkX Finance App
Populates database with sample data for testing and demonstration
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta

# Setup Django
sys.path.insert(0, '/app')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from finance.models import (
    Currency, ExchangeRate, PaymentGateway, PaymentTransaction,
    BalanceTransaction, TransactionQueue, Investment, Department,
    BudgetCategory, Expense, RevenueStream
)
from users.models import ClientH
from packages.models import PackageType

User = get_user_model()

def create_currencies():
    """Create base currencies"""
    print("📦 Creating currencies...")
    currencies = [
        {'code': 'KES', 'is_base_currency': True},
        {'code': 'USD'},
        {'code': 'EUR'},
        {'code': 'GBP'},
    ]
    
    for curr_data in currencies:
        curr, created = Currency.objects.get_or_create(
            code=curr_data['code'],
            defaults={'is_base_currency': curr_data.get('is_base_currency', False)}
        )
        if created:
            print(f"  ✅ Created {curr.code}")
    
    # Create exchange rates
    kes = Currency.objects.get(code='KES')
    usd = Currency.objects.get(code='USD')
    
    ExchangeRate.objects.get_or_create(
        base_currency=usd,
        target_currency=kes,
        defaults={'rate': Decimal('150.00'), 'source': 'manual'}
    )
    print("  ✅ Created exchange rates")

def create_payment_gateway():
    """Create M-Pesa payment gateway"""
    print("📦 Creating payment gateway...")
    kes = Currency.objects.get(code='KES')
    
    gateway, created = PaymentGateway.objects.get_or_create(
        gateway_type='mpesa',
        defaults={
            'name': 'M-Pesa STK Push',
            'default_currency': kes,
            'is_default': True,
            'status': 'active',
            'config': {
                'consumer_key': 'dummy_key',
                'consumer_secret': 'dummy_secret',
                'shortcode': '174379',
                'lipa_na_mpesa_passkey': 'dummy_passkey'
            }
        }
    )
    
    if created:
        gateway.supported_currencies.add(kes)
        print("  ✅ Created M-Pesa gateway")

def create_departments():
    """Create departments with budgets"""
    print("📦 Creating departments...")
    departments_data = [
        {'name': 'Network Operations', 'code': 'NETOPS', 'budget': Decimal('500000.00')},
        {'name': 'Customer Support', 'code': 'SUPPORT', 'budget': Decimal('300000.00')},
        {'name': 'Marketing', 'code': 'MARKETING', 'budget': Decimal('400000.00')},
        {'name': 'IT & Development', 'code': 'IT', 'budget': Decimal('600000.00')},
    ]
    
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        if created:
            print(f"  ✅ Created {dept.name}")

def create_revenue_streams():
    """Create revenue streams"""
    print("📦 Creating revenue streams...")
    streams_data = [
        {
            'name': 'Internet Package Sales',
            'category': 'package_sales',
            'target_revenue': Decimal('1000000.00'),
            'description': 'Revenue from internet package subscriptions'
        },
        {
            'name': 'Balance Top-ups',
            'category': 'voucher_sales',
            'target_revenue': Decimal('500000.00'),
            'description': 'Revenue from account balance purchases'
        },
        {
            'name': 'Premium Services',
            'category': 'premium_services',
            'target_revenue': Decimal('200000.00'),
            'description': 'Revenue from premium features and add-ons'
        },
    ]
    
    for stream_data in streams_data:
        stream, created = RevenueStream.objects.get_or_create(
            name=stream_data['name'],
            defaults=stream_data
        )
        if created:
            print(f"  ✅ Created {stream.name}")

def create_sample_clients():
    """Create sample clients"""
    print("📦 Creating sample clients...")
    
    # Get default location
    from locations.models import Location
    default_location = Location.objects.filter(is_central=True).first() or Location.objects.first()
    
    if not default_location:
        print("  ⚠️ No locations found, skipping client creation")
        return
    
    # Get or create a default user for clients
    default_user, _ = User.objects.get_or_create(
        username='default_client_user',
        defaults={
            'email': 'default@teralinkx.local',
            'is_active': True
        }
    )
    
    clients_data = [
        {'account': 'CLI000001', 'phone_number': '254712345001', 'display_name': 'Test Client 1'},
        {'account': 'CLI000002', 'phone_number': '254712345002', 'display_name': 'Test Client 2'},
        {'account': 'CLI000003', 'phone_number': '254712345003', 'display_name': 'Test Client 3'},
        {'account': 'CLI000004', 'phone_number': '254712345004', 'display_name': 'Test Client 4'},
        {'account': 'CLI000005', 'phone_number': '254712345005', 'display_name': 'Test Client 5'},
    ]
    
    for idx, client_data in enumerate(clients_data, 1):
        # Create unique user for each client
        user, _ = User.objects.get_or_create(
            username=f"client_{client_data['account']}",
            defaults={
                'email': f"client{idx}@teralinkx.local",
                'is_active': True
            }
        )
        
        client, created = ClientH.objects.get_or_create(
            account=client_data['account'],
            defaults={
                'user': user,
                'phone_number': client_data['phone_number'],
                'display_name': client_data['display_name'],
                'account_tier': 'basic',
                'status': 'active',
                'balance': Decimal('1000.00'),
                'credit_limit': Decimal('0.00'),
                'total_spent': Decimal('0.00'),
                'lifetime_data_used': 0,
                'home_location': default_location,
                'failed_login_attempts': 0,
                'two_factor_enabled': False,
                'auto_renew': False,
                'active_voucher': '',
                'last_login': timezone.now(),
                'last_seen': timezone.now(),
                'last_balance_update': timezone.now(),
                'reward_points': 0,
                'reward_tier': 'bronze',
                'total_points_earned': 0,
                'total_points_redeemed': 0
            }
        )
        if created:
            print(f"  ✅ Created {client.account}")

def create_transactions():
    """Create sample transactions"""
    print("📦 Creating sample transactions...")
    kes = Currency.objects.get(code='KES')
    gateway = PaymentGateway.objects.filter(gateway_type='mpesa').first()
    clients = list(ClientH.objects.all()[:5])
    
    # Create completed transactions for the last 30 days
    for i in range(50):
        days_ago = i % 30
        created_date = timezone.now() - timedelta(days=days_ago)
        client = clients[i % len(clients)]
        amount = Decimal(str(500 + (i * 100) % 2000))
        
        # Payment Transaction
        txn, created = PaymentTransaction.objects.get_or_create(
            transaction_id=f"TXN{timezone.now().strftime('%Y%m%d')}{i:04d}",
            defaults={
                'user': client,
                'payment_method': 'mpesa',
                'payment_gateway': gateway,
                'amount': amount,
                'currency': kes,
                'amount_base': amount,
                'initiator': client.phone_number,
                'status': 'completed',
                'result_code': 0,
                'result_desc': 'Success',
                'created_at': created_date
            }
        )
        
        # Transaction Queue
        TransactionQueue.objects.get_or_create(
            checkout_request_id=f"CHK{timezone.now().strftime('%Y%m%d')}{i:04d}",
            defaults={
                'user': client,
                'queue_type': 'payment_processing',
                'method': 'mpesa',
                'initiator': client.phone_number,
                'package_code': f"PKG{(i % 3) + 1:03d}",
                'package': f"Package {(i % 3) + 1}",
                'price': amount,
                'status': 'completed' if i % 10 != 0 else 'pending',
                'account_reference': client.account,
                'created_at': created_date
            }
        )
        
        # Balance Transaction
        BalanceTransaction.objects.get_or_create(
            user=client,
            created_at=created_date,
            defaults={
                'transaction_type': 'topup',
                'credit': amount,
                'debit': Decimal('0.00'),
                'balance_before': client.balance,
                'balance_after': client.balance + amount,
                'description': f'Balance top-up via M-Pesa'
            }
        )
    
    print(f"  ✅ Created 50 sample transactions")

def create_expenses():
    """Create sample expenses"""
    print("📦 Creating sample expenses...")
    kes = Currency.objects.get(code='KES')
    departments = list(Department.objects.all())
    
    expenses_data = [
        {'description': 'Fiber optic cables purchase', 'amount': Decimal('150000.00'), 'category': 'network', 'dept_idx': 0},
        {'description': 'Router and switches maintenance', 'amount': Decimal('75000.00'), 'category': 'maintenance', 'dept_idx': 0},
        {'description': 'Staff salaries - March', 'amount': Decimal('450000.00'), 'category': 'salaries', 'dept_idx': 1},
        {'description': 'Facebook ads campaign', 'amount': Decimal('50000.00'), 'category': 'marketing', 'dept_idx': 2},
        {'description': 'Office rent', 'amount': Decimal('80000.00'), 'category': 'office', 'dept_idx': 3},
        {'description': 'Electricity bill', 'amount': Decimal('35000.00'), 'category': 'utility', 'dept_idx': 0},
        {'description': 'Software licenses', 'amount': Decimal('120000.00'), 'category': 'software', 'dept_idx': 3},
    ]
    
    for exp_data in expenses_data:
        dept = departments[exp_data['dept_idx']] if departments else None
        Expense.objects.get_or_create(
            description=exp_data['description'],
            defaults={
                'expense_date': timezone.now().date() - timedelta(days=15),
                'amount': exp_data['amount'],
                'currency': kes,
                'category': exp_data['category'],
                'department': dept,
                'approval_status': 'paid',
                'vat_rate': Decimal('16.0')
            }
        )
    
    print(f"  ✅ Created {len(expenses_data)} expenses")

def create_investments():
    """Create sample investments"""
    print("📦 Creating sample investments...")
    kes = Currency.objects.get(code='KES')
    
    investments_data = [
        {
            'investor_name': 'Seed Capital Fund',
            'amount': Decimal('5000000.00'),
            'investment_type': 'seed',
            'equity_percentage': Decimal('15.00'),
            'investment_status': 'active'
        },
        {
            'investor_name': 'Angel Investor - John Doe',
            'amount': Decimal('2000000.00'),
            'investment_type': 'angel',
            'equity_percentage': Decimal('8.00'),
            'investment_status': 'active'
        },
    ]
    
    for inv_data in investments_data:
        Investment.objects.get_or_create(
            investor_name=inv_data['investor_name'],
            defaults={
                **inv_data,
                'investment_date': timezone.now().date() - timedelta(days=180),
                'currency': kes
            }
        )
    
    print(f"  ✅ Created {len(investments_data)} investments")

def main():
    """Main seed function"""
    print("\n🌱 Starting database seed...\n")
    
    try:
        create_currencies()
        create_payment_gateway()
        create_departments()
        create_revenue_streams()
        create_sample_clients()
        create_transactions()
        create_expenses()
        create_investments()
        
        print("\n✅ Database seeded successfully!\n")
        print("📊 Summary:")
        print(f"  - Currencies: {Currency.objects.count()}")
        print(f"  - Departments: {Department.objects.count()}")
        print(f"  - Revenue Streams: {RevenueStream.objects.count()}")
        print(f"  - Clients: {ClientH.objects.count()}")
        print(f"  - Payment Transactions: {PaymentTransaction.objects.count()}")
        print(f"  - Transaction Queue: {TransactionQueue.objects.count()}")
        print(f"  - Balance Transactions: {BalanceTransaction.objects.count()}")
        print(f"  - Expenses: {Expense.objects.count()}")
        print(f"  - Investments: {Investment.objects.count()}")
        print()
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
