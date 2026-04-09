# Finance App - Detailed Implementation Guide

## 🎯 Phase 1: Financial Reporting Engine

### 1.1 Enhanced Financial Report Generator

Create: `apps/finance/services/report_generator.py`

```python
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from datetime import timedelta
from finance.models import (
    PaymentTransaction, BalanceTransaction, Expense, 
    Investment, FinancialReport, TransactionQueue
)
from packages.models import DispatchVoucher


class FinancialReportGenerator:
    """Generate comprehensive financial reports for ISP business"""
    
    @staticmethod
    def generate_daily_sales_report(date, save_to_db=True):
        """
        Generate detailed daily sales report
        
        Returns:
            {
                'date': date,
                'revenue': {
                    'total': Decimal,
                    'mpesa': Decimal,
                    'balance': Decimal,
                    'mixed': Decimal,
                },
                'transactions': {
                    'count': int,
                    'average_value': Decimal,
                    'success_rate': float,
                },
                'packages': [
                    {'name': str, 'sales': int, 'revenue': Decimal},
                ],
                'hourly_breakdown': [
                    {'hour': int, 'revenue': Decimal, 'count': int},
                ],
                'payment_methods': [
                    {'method': str, 'count': int, 'revenue': Decimal},
                ],
                'gateway_fees': Decimal,
                'net_revenue': Decimal,
            }
        """
        start_datetime = timezone.make_aware(
            timezone.datetime.combine(date, timezone.datetime.min.time())
        )
        end_datetime = start_datetime + timedelta(days=1)
        
        # Get all completed transactions for the day
        transactions = PaymentTransaction.objects.filter(
            created_at__gte=start_datetime,
            created_at__lt=end_datetime,
            status='completed'
        )
        
        # Revenue breakdown by payment method
        revenue_by_method = transactions.values('payment_method').annotate(
            total=Sum('amount_base'),
            count=Count('id')
        )
        
        revenue_breakdown = {
            'total': transactions.aggregate(Sum('amount_base'))['amount_base__sum'] or Decimal('0'),
            'mpesa': Decimal('0'),
            'balance': Decimal('0'),
            'mixed': Decimal('0'),
        }
        
        for method_data in revenue_by_method:
            method = method_data['payment_method']
            if 'mpesa' in method and 'balance' not in method:
                revenue_breakdown['mpesa'] += method_data['total']
            elif method == 'balance':
                revenue_breakdown['balance'] += method_data['total']
            elif 'mpesa+balance' in method:
                revenue_breakdown['mixed'] += method_data['total']
        
        # Transaction statistics
        transaction_stats = {
            'count': transactions.count(),
            'average_value': transactions.aggregate(Avg('amount_base'))['amount_base__avg'] or Decimal('0'),
            'success_rate': FinancialReportGenerator._calculate_success_rate(date),
        }
        
        # Top packages
        vouchers = DispatchVoucher.objects.filter(
            activated_at__gte=start_datetime,
            activated_at__lt=end_datetime
        ).select_related('package')
        
        package_stats = vouchers.values('package__name').annotate(
            sales=Count('id'),
            revenue=Sum('price_paid')
        ).order_by('-revenue')[:10]
        
        # Hourly breakdown
        hourly_data = []
        for hour in range(24):
            hour_start = start_datetime + timedelta(hours=hour)
            hour_end = hour_start + timedelta(hours=1)
            
            hour_transactions = transactions.filter(
                created_at__gte=hour_start,
                created_at__lt=hour_end
            )
            
            hourly_data.append({
                'hour': hour,
                'revenue': hour_transactions.aggregate(Sum('amount_base'))['amount_base__sum'] or Decimal('0'),
                'count': hour_transactions.count(),
            })
        
        # Payment method breakdown
        payment_methods = []
        for method_data in revenue_by_method:
            payment_methods.append({
                'method': method_data['payment_method'],
                'count': method_data['count'],
                'revenue': method_data['total'],
            })
        
        # Calculate gateway fees (M-Pesa charges ~1.5%)
        mpesa_revenue = revenue_breakdown['mpesa'] + revenue_breakdown['mixed']
        gateway_fees = mpesa_revenue * Decimal('0.015')
        net_revenue = revenue_breakdown['total'] - gateway_fees
        
        report_data = {
            'date': date.isoformat(),
            'revenue': revenue_breakdown,
            'transactions': transaction_stats,
            'packages': list(package_stats),
            'hourly_breakdown': hourly_data,
            'payment_methods': payment_methods,
            'gateway_fees': float(gateway_fees),
            'net_revenue': float(net_revenue),
        }
        
        # Save to database if requested
        if save_to_db:
            FinancialReport.objects.create(
                report_type='daily_sales',
                period_start=date,
                period_end=date,
                summary={
                    'total_revenue': float(revenue_breakdown['total']),
                    'net_revenue': float(net_revenue),
                    'transaction_count': transaction_stats['count'],
                    'average_value': float(transaction_stats['average_value']),
                },
                breakdown=report_data,
                record_count=transaction_stats['count'],
            )
        
        return report_data
    
    @staticmethod
    def _calculate_success_rate(date):
        """Calculate payment success rate for the day"""
        start_datetime = timezone.make_aware(
            timezone.datetime.combine(date, timezone.datetime.min.time())
        )
        end_datetime = start_datetime + timedelta(days=1)
        
        total_attempts = TransactionQueue.objects.filter(
            created_at__gte=start_datetime,
            created_at__lt=end_datetime
        ).count()
        
        successful = TransactionQueue.objects.filter(
            created_at__gte=start_datetime,
            created_at__lt=end_datetime,
            status__in=['completed', 'processed']
        ).count()
        
        if total_attempts == 0:
            return 100.0
        
        return (successful / total_attempts) * 100
    
    @staticmethod
    def generate_monthly_income_statement(month, year):
        """
        Generate comprehensive monthly income statement
        
        Returns:
            {
                'period': {'month': int, 'year': int},
                'revenue': {
                    'package_sales': Decimal,
                    'ads_revenue': Decimal,
                    'other_revenue': Decimal,
                    'total_revenue': Decimal,
                },
                'expenses': {
                    'network_infrastructure': Decimal,
                    'salaries': Decimal,
                    'marketing': Decimal,
                    'utilities': Decimal,
                    'software': Decimal,
                    'other': Decimal,
                    'total_expenses': Decimal,
                },
                'gross_profit': Decimal,
                'operating_expenses': Decimal,
                'net_income': Decimal,
                'profit_margin': float,
            }
        """
        start_date = timezone.datetime(year, month, 1).date()
        if month == 12:
            end_date = timezone.datetime(year + 1, 1, 1).date()
        else:
            end_date = timezone.datetime(year, month + 1, 1).date()
        
        # Revenue calculation
        package_sales = PaymentTransaction.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date,
            status='completed'
        ).aggregate(Sum('amount_base'))['amount_base__sum'] or Decimal('0')
        
        # Ads revenue (if ads app exists)
        ads_revenue = Decimal('0')
        try:
            from ads.models import Advertisement
            ads_revenue = Advertisement.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date,
                status='active'
            ).aggregate(Sum('total_spent'))['total_spent__sum'] or Decimal('0')
        except ImportError:
            pass
        
        total_revenue = package_sales + ads_revenue
        
        # Expenses by category
        expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lt=end_date,
            approval_status__in=['approved', 'paid']
        )
        
        expense_breakdown = {
            'network_infrastructure': expenses.filter(category='network').aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
            'salaries': expenses.filter(category='salaries').aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
            'marketing': expenses.filter(category='marketing').aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
            'utilities': expenses.filter(category='utility').aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
            'software': expenses.filter(category='software').aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
            'other': expenses.filter(category='other').aggregate(Sum('amount'))['amount__sum'] or Decimal('0'),
        }
        
        total_expenses = sum(expense_breakdown.values())
        
        # Calculate profitability
        gross_profit = total_revenue - total_expenses
        net_income = gross_profit  # Simplified (no tax calculation yet)
        profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
        
        return {
            'period': {'month': month, 'year': year},
            'revenue': {
                'package_sales': float(package_sales),
                'ads_revenue': float(ads_revenue),
                'total_revenue': float(total_revenue),
            },
            'expenses': {
                **{k: float(v) for k, v in expense_breakdown.items()},
                'total_expenses': float(total_expenses),
            },
            'gross_profit': float(gross_profit),
            'net_income': float(net_income),
            'profit_margin': float(profit_margin),
        }
    
    @staticmethod
    def generate_cash_flow_statement(start_date, end_date):
        """
        Generate cash flow statement
        
        Returns:
            {
                'period': {'start': date, 'end': date},
                'operating_activities': {
                    'cash_from_customers': Decimal,
                    'cash_to_suppliers': Decimal,
                    'cash_to_employees': Decimal,
                    'net_operating_cash': Decimal,
                },
                'investing_activities': {
                    'equipment_purchases': Decimal,
                    'infrastructure_investments': Decimal,
                    'net_investing_cash': Decimal,
                },
                'financing_activities': {
                    'loans_received': Decimal,
                    'loan_repayments': Decimal,
                    'equity_investments': Decimal,
                    'net_financing_cash': Decimal,
                },
                'net_cash_flow': Decimal,
            }
        """
        # Operating activities
        cash_from_customers = PaymentTransaction.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date,
            status='completed'
        ).aggregate(Sum('amount_base'))['amount_base__sum'] or Decimal('0')
        
        cash_to_suppliers = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lt=end_date,
            approval_status='paid',
            category__in=['network', 'utility', 'software', 'other']
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        cash_to_employees = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lt=end_date,
            approval_status='paid',
            category='salaries'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        net_operating = cash_from_customers - cash_to_suppliers - cash_to_employees
        
        # Investing activities
        equipment_purchases = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lt=end_date,
            approval_status='paid',
            is_capex=True
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        net_investing = -equipment_purchases
        
        # Financing activities
        loans_received = Investment.objects.filter(
            investment_date__gte=start_date,
            investment_date__lt=end_date,
            investment_type='loan',
            investment_status='disbursed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        equity_investments = Investment.objects.filter(
            investment_date__gte=start_date,
            investment_date__lt=end_date,
            investment_type__in=['seed', 'angel', 'vc', 'equity'],
            investment_status='disbursed'
        ).aggregate(Sum('amount'))['amount__sum'] or Decimal('0')
        
        net_financing = loans_received + equity_investments
        
        net_cash_flow = net_operating + net_investing + net_financing
        
        return {
            'period': {
                'start': start_date.isoformat(),
                'end': end_date.isoformat(),
            },
            'operating_activities': {
                'cash_from_customers': float(cash_from_customers),
                'cash_to_suppliers': float(cash_to_suppliers),
                'cash_to_employees': float(cash_to_employees),
                'net_operating_cash': float(net_operating),
            },
            'investing_activities': {
                'equipment_purchases': float(equipment_purchases),
                'net_investing_cash': float(net_investing),
            },
            'financing_activities': {
                'loans_received': float(loans_received),
                'equity_investments': float(equity_investments),
                'net_financing_cash': float(net_financing),
            },
            'net_cash_flow': float(net_cash_flow),
        }
```

---

## 🎯 Phase 2: ISP Business Intelligence

### 2.1 Customer Analytics Service

Create: `apps/finance/services/customer_analytics.py`

```python
from decimal import Decimal
from django.utils import timezone
from django.db.models import Sum, Count, Avg, F, Q
from datetime import timedelta
from users.models import ClientH
from packages.models import DispatchVoucher
from finance.models import PaymentTransaction, TransactionQueue


class ISPCustomerAnalytics:
    """Advanced customer analytics for ISP business"""
    
    @staticmethod
    def calculate_arpu(period='monthly', start_date=None, end_date=None):
        """
        Calculate Average Revenue Per User
        
        Args:
            period: 'daily', 'weekly', 'monthly', 'quarterly', 'annual'
            start_date: Optional start date
            end_date: Optional end date
        
        Returns:
            {
                'arpu': Decimal,
                'total_revenue': Decimal,
                'active_users': int,
                'period': str,
            }
        """
        if not start_date or not end_date:
            end_date = timezone.now()
            if period == 'daily':
                start_date = end_date - timedelta(days=1)
            elif period == 'weekly':
                start_date = end_date - timedelta(weeks=1)
            elif period == 'monthly':
                start_date = end_date - timedelta(days=30)
            elif period == 'quarterly':
                start_date = end_date - timedelta(days=90)
            elif period == 'annual':
                start_date = end_date - timedelta(days=365)
        
        # Get total revenue
        total_revenue = PaymentTransaction.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date,
            status='completed'
        ).aggregate(Sum('amount_base'))['amount_base__sum'] or Decimal('0')
        
        # Get active users (users who made at least one purchase)
        active_users = PaymentTransaction.objects.filter(
            created_at__gte=start_date,
            created_at__lt=end_date,
            status='completed'
        ).values('user').distinct().count()
        
        arpu = (total_revenue / active_users) if active_users > 0 else Decimal('0')
        
        return {
            'arpu': float(arpu),
            'total_revenue': float(total_revenue),
            'active_users': active_users,
            'period': period,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat(),
        }
    
    @staticmethod
    def calculate_clv(customer_segment=None, months_lookback=12):
        """
        Calculate Customer Lifetime Value
        
        Args:
            customer_segment: 'high_value', 'regular', 'low_value', or None for all
            months_lookback: Number of months to analyze
        
        Returns:
            {
                'clv': Decimal,
                'avg_purchase_value': Decimal,
                'purchase_frequency': float,
                'customer_lifespan_months': int,
                'segment': str,
            }
        """
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30 * months_lookback)
        
        # Get customers based on segment
        if customer_segment:
            customers = ISPCustomerAnalytics._get_customer_segment(customer_segment)
        else:
            customers = ClientH.objects.filter(status='active')
        
        customer_ids = customers.values_list('id', flat=True)
        
        # Calculate average purchase value
        avg_purchase_value = PaymentTransaction.objects.filter(
            user_id__in=customer_ids,
            created_at__gte=start_date,
            status='completed'
        ).aggregate(Avg('amount_base'))['amount_base__avg'] or Decimal('0')
        
        # Calculate purchase frequency (purchases per month)
        total_purchases = PaymentTransaction.objects.filter(
            user_id__in=customer_ids,
            created_at__gte=start_date,
            status='completed'
        ).count()
        
        purchase_frequency = (total_purchases / len(customer_ids) / months_lookback) if customer_ids else 0
        
        # Estimate customer lifespan (average months a customer stays)
        customer_lifespan = ISPCustomerAnalytics._estimate_customer_lifespan(customer_ids)
        
        # CLV = Average Purchase Value × Purchase Frequency × Customer Lifespan
        clv = avg_purchase_value * Decimal(str(purchase_frequency)) * Decimal(str(customer_lifespan))
        
        return {
            'clv': float(clv),
            'avg_purchase_value': float(avg_purchase_value),
            'purchase_frequency': purchase_frequency,
            'customer_lifespan_months': customer_lifespan,
            'segment': customer_segment or 'all',
            'customer_count': len(customer_ids),
        }
    
    @staticmethod
    def _estimate_customer_lifespan(customer_ids):
        """Estimate average customer lifespan in months"""
        # Get customers with first and last purchase dates
        customers_with_history = PaymentTransaction.objects.filter(
            user_id__in=customer_ids,
            status='completed'
        ).values('user').annotate(
            first_purchase=Min('created_at'),
            last_purchase=Max('created_at')
        )
        
        total_lifespan_days = 0
        count = 0
        
        for customer in customers_with_history:
            lifespan = (customer['last_purchase'] - customer['first_purchase']).days
            if lifespan > 0:
                total_lifespan_days += lifespan
                count += 1
        
        if count == 0:
            return 12  # Default to 12 months
        
        avg_lifespan_days = total_lifespan_days / count
        return int(avg_lifespan_days / 30)  # Convert to months
    
    @staticmethod
    def calculate_churn_rate(period='monthly'):
        """
        Calculate customer churn rate
        
        Returns:
            {
                'churn_rate': float,
                'churned_customers': int,
                'total_customers': int,
                'period': str,
            }
        """
        end_date = timezone.now()
        
        if period == 'monthly':
            start_date = end_date - timedelta(days=30)
            lookback_date = start_date - timedelta(days=30)
        elif period == 'quarterly':
            start_date = end_date - timedelta(days=90)
            lookback_date = start_date - timedelta(days=90)
        else:
            start_date = end_date - timedelta(days=365)
            lookback_date = start_date - timedelta(days=365)
        
        # Customers active at start of period
        customers_at_start = ClientH.objects.filter(
            created_at__lt=start_date,
            status='active'
        ).count()
        
        # Customers who were active but haven't made a purchase in the period
        churned_customers = ClientH.objects.filter(
            created_at__lt=start_date,
            status='active'
        ).exclude(
            id__in=PaymentTransaction.objects.filter(
                created_at__gte=start_date,
                created_at__lt=end_date,
                status='completed'
            ).values_list('user_id', flat=True)
        ).count()
        
        churn_rate = (churned_customers / customers_at_start * 100) if customers_at_start > 0 else 0
        
        return {
            'churn_rate': churn_rate,
            'churned_customers': churned_customers,
            'total_customers': customers_at_start,
            'period': period,
        }
    
    @staticmethod
    def segment_customers():
        """
        Segment customers into categories
        
        Returns:
            {
                'high_value': {'count': int, 'avg_revenue': Decimal},
                'regular': {'count': int, 'avg_revenue': Decimal},
                'low_value': {'count': int, 'avg_revenue': Decimal},
                'at_risk': {'count': int, 'avg_revenue': Decimal},
                'new': {'count': int, 'avg_revenue': Decimal},
            }
        """
        # Calculate revenue per customer (last 3 months)
        three_months_ago = timezone.now() - timedelta(days=90)
        
        customer_revenue = PaymentTransaction.objects.filter(
            created_at__gte=three_months_ago,
            status='completed'
        ).values('user').annotate(
            total_revenue=Sum('amount_base')
        ).order_by('-total_revenue')
        
        total_customers = customer_revenue.count()
        
        # High-value: Top 20%
        high_value_count = int(total_customers * 0.2)
        high_value = customer_revenue[:high_value_count]
        
        # Regular: Middle 60%
        regular_start = high_value_count
        regular_end = int(total_customers * 0.8)
        regular = customer_revenue[regular_start:regular_end]
        
        # Low-value: Bottom 20%
        low_value = customer_revenue[regular_end:]
        
        # At-risk: No purchase in last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        at_risk = ClientH.objects.filter(
            status='active'
        ).exclude(
            id__in=PaymentTransaction.objects.filter(
                created_at__gte=thirty_days_ago,
                status='completed'
            ).values_list('user_id', flat=True)
        )
        
        # New: Created in last 90 days
        new_customers = ClientH.objects.filter(
            created_at__gte=three_months_ago,
            status='active'
        )
        
        return {
            'high_value': {
                'count': len(high_value),
                'avg_revenue': float(sum(c['total_revenue'] for c in high_value) / len(high_value)) if high_value else 0,
            },
            'regular': {
                'count': len(regular),
                'avg_revenue': float(sum(c['total_revenue'] for c in regular) / len(regular)) if regular else 0,
            },
            'low_value': {
                'count': len(low_value),
                'avg_revenue': float(sum(c['total_revenue'] for c in low_value) / len(low_value)) if low_value else 0,
            },
            'at_risk': {
                'count': at_risk.count(),
                'avg_revenue': 0,  # They haven't purchased recently
            },
            'new': {
                'count': new_customers.count(),
                'avg_revenue': float(
                    PaymentTransaction.objects.filter(
                        user__in=new_customers,
                        status='completed'
                    ).aggregate(Avg('amount_base'))['amount_base__avg'] or 0
                ),
            },
        }
    
    @staticmethod
    def _get_customer_segment(segment):
        """Get customers for a specific segment"""
        segments = ISPCustomerAnalytics.segment_customers()
        
        if segment == 'high_value':
            # Get top 20% by revenue
            three_months_ago = timezone.now() - timedelta(days=90)
            customer_revenue = PaymentTransaction.objects.filter(
                created_at__gte=three_months_ago,
                status='completed'
            ).values('user').annotate(
                total_revenue=Sum('amount_base')
            ).order_by('-total_revenue')
            
            high_value_count = int(customer_revenue.count() * 0.2)
            user_ids = [c['user'] for c in customer_revenue[:high_value_count]]
            return ClientH.objects.filter(id__in=user_ids)
        
        # Add other segment logic as needed
        return ClientH.objects.filter(status='active')
```

---

## 📊 Implementation Priority Matrix

| Feature | Business Impact | Complexity | Priority | Est. Days |
|---------|----------------|------------|----------|-----------|
| Daily Sales Report | Critical | Low | 1 | 2 |
| ARPU Calculation | High | Low | 2 | 1 |
| Monthly Income Statement | Critical | Medium | 3 | 3 |
| Package Performance | High | Low | 4 | 2 |
| CLV Calculation | High | Medium | 5 | 2 |
| Churn Rate Tracking | High | Medium | 6 | 2 |
| Cash Flow Statement | Medium | Medium | 7 | 3 |
| Customer Segmentation | High | Medium | 8 | 3 |
| Expense Automation | Medium | Low | 9 | 2 |
| Budget Forecasting | Medium | High | 10 | 4 |

**Total Estimated Time**: ~24 days for full implementation

---

## 🔧 Next Steps

1. **Review this plan** with the team
2. **Prioritize features** based on business needs
3. **Start with Phase 1** - Financial reporting
4. **Implement incrementally** - One feature at a time
5. **Test thoroughly** - Each feature before moving to next
6. **Document APIs** - As you build them
7. **Create dashboards** - Visualize the data

---

**Ready to start implementation?** Let me know which phase you'd like to tackle first!
