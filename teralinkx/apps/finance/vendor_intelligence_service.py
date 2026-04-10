# apps/finance/vendor_intelligence_service.py
"""
Supplier & Vendor Intelligence Service
Tracks vendor performance, costs, and contract management for ISP operations.
"""
from django.db.models import Sum, Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class VendorIntelligenceService:
    """Service for vendor analysis and contract management"""
    
    @staticmethod
    def get_vendor_performance():
        """Analyze performance and costs for all vendors"""
        from finance.models import Expense
        
        # Get vendor spending (last 12 months)
        twelve_months_ago = timezone.now() - timedelta(days=365)
        
        vendors = Expense.objects.filter(
            expense_date__gte=twelve_months_ago.date(),
            approval_status='paid'
        ).values('vendor_name').annotate(
            total_spend=Sum('amount'),
            invoice_count=Count('id'),
            avg_invoice_amount=Avg('amount')
        ).filter(total_spend__gt=0).order_by('-total_spend')
        
        vendor_metrics = []
        
        for vendor in vendors:
            vendor_name = vendor['vendor_name'] or 'Unknown'
            total_spend = vendor['total_spend'] or 0
            invoice_count = vendor['invoice_count']
            avg_invoice = vendor['avg_invoice_amount'] or 0
            
            # Calculate month-over-month trend
            last_month_spend = Expense.objects.filter(
                vendor_name=vendor_name,
                expense_date__gte=(timezone.now() - timedelta(days=30)).date(),
                approval_status='paid'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            prev_month_spend = Expense.objects.filter(
                vendor_name=vendor_name,
                expense_date__gte=(timezone.now() - timedelta(days=60)).date(),
                expense_date__lt=(timezone.now() - timedelta(days=30)).date(),
                approval_status='paid'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            trend_pct = ((last_month_spend - prev_month_spend) / prev_month_spend * 100) if prev_month_spend > 0 else 0
            
            # Check for invoice discrepancies (simplified)
            discrepancy_count = 0  # Would need invoice validation logic
            
            vendor_metrics.append({
                'vendor_name': vendor_name,
                'total_spend_12m': float(total_spend),
                'invoice_count': invoice_count,
                'avg_invoice_amount': float(avg_invoice),
                'last_month_spend': float(last_month_spend),
                'trend_pct': float(trend_pct),
                'discrepancy_count': discrepancy_count,
                'spend_share_pct': 0  # Calculate after getting total
            })
        
        # Calculate spend share
        total_spend = sum(v['total_spend_12m'] for v in vendor_metrics)
        for vendor in vendor_metrics:
            vendor['spend_share_pct'] = (vendor['total_spend_12m'] / total_spend * 100) if total_spend > 0 else 0
        
        return vendor_metrics
    
    @staticmethod
    def get_bandwidth_cost_analysis():
        """
        Analyze bandwidth costs per upstream provider.
        ISP-specific metric for infrastructure costs.
        """
        from finance.models import Expense
        
        # Filter for bandwidth/connectivity expenses
        bandwidth_expenses = Expense.objects.filter(
            category__in=['Bandwidth', 'Connectivity', 'Infrastructure'],
            approval_status='paid',
            expense_date__gte=(timezone.now() - timedelta(days=365)).date()
        ).values('vendor_name').annotate(
            total_cost=Sum('amount'),
            invoice_count=Count('id')
        ).order_by('-total_cost')
        
        analysis = []
        
        for expense in bandwidth_expenses:
            vendor_name = expense['vendor_name'] or 'Unknown'
            total_cost = expense['total_cost'] or 0
            
            # Cost per GB would require bandwidth usage data
            # Placeholder for now
            cost_per_gb = 0
            bandwidth_gb = 0
            
            analysis.append({
                'provider': vendor_name,
                'total_cost_12m': float(total_cost),
                'bandwidth_gb': bandwidth_gb,
                'cost_per_gb': float(cost_per_gb),
                'invoice_count': expense['invoice_count']
            })
        
        return analysis
    
    @staticmethod
    def get_contract_expiry_calendar():
        """
        Track upcoming contract renewals.
        Requires VendorContract model (to be created).
        """
        # Placeholder - would need VendorContract model
        
        return {
            'message': 'Contract tracking requires VendorContract model',
            'structure': {
                'vendor_name': 'string',
                'contract_type': 'string',
                'start_date': 'date',
                'end_date': 'date',
                'monthly_cost': 'decimal',
                'auto_renew': 'boolean',
                'notice_period_days': 'integer'
            },
            'upcoming_renewals': [],
            'recommendation': 'Create VendorContract model to track contract lifecycle'
        }
    
    @staticmethod
    def get_invoice_discrepancy_alerts():
        """
        Flag vendors with consistent invoice discrepancies.
        Requires invoice validation history.
        """
        from finance.models import Expense
        
        # Simplified - would need InvoiceValidation model
        # For now, flag vendors with unusual spending patterns
        
        alerts = []
        vendors = VendorIntelligenceService.get_vendor_performance()
        
        for vendor in vendors:
            # Flag if spending increased >50% month-over-month
            if vendor['trend_pct'] > 50:
                alerts.append({
                    'vendor': vendor['vendor_name'],
                    'alert_type': 'spending_spike',
                    'severity': 'medium',
                    'message': f"Spending increased {vendor['trend_pct']:.1f}% last month",
                    'last_month_spend': vendor['last_month_spend']
                })
            
            # Flag if vendor is >20% of total spend (concentration risk)
            if vendor['spend_share_pct'] > 20:
                alerts.append({
                    'vendor': vendor['vendor_name'],
                    'alert_type': 'concentration_risk',
                    'severity': 'low',
                    'message': f"Vendor represents {vendor['spend_share_pct']:.1f}% of total spend",
                    'spend_share': vendor['spend_share_pct']
                })
        
        return alerts
    
    @staticmethod
    def get_vendor_recommendations():
        """Generate vendor management recommendations"""
        vendors = VendorIntelligenceService.get_vendor_performance()
        alerts = VendorIntelligenceService.get_invoice_discrepancy_alerts()
        
        recommendations = []
        
        # High-spend vendors
        for vendor in vendors[:3]:  # Top 3 vendors
            recommendations.append({
                'vendor': vendor['vendor_name'],
                'type': 'cost_optimization',
                'priority': 'high',
                'recommendation': f"Top vendor with KES {vendor['total_spend_12m']:,.2f} annual spend - negotiate volume discount",
                'estimated_savings': f"5-10% discount could save KES {vendor['total_spend_12m'] * 0.075:,.2f}/year"
            })
        
        # Vendors with spending spikes
        for alert in alerts:
            if alert['alert_type'] == 'spending_spike':
                recommendations.append({
                    'vendor': alert['vendor'],
                    'type': 'spending_review',
                    'priority': 'medium',
                    'recommendation': alert['message'] + ' - review invoices for accuracy',
                    'estimated_savings': 'Potential overcharging detection'
                })
        
        return recommendations
    
    @staticmethod
    def get_dashboard_summary():
        """Get complete vendor intelligence dashboard"""
        vendor_performance = VendorIntelligenceService.get_vendor_performance()
        bandwidth_analysis = VendorIntelligenceService.get_bandwidth_cost_analysis()
        alerts = VendorIntelligenceService.get_invoice_discrepancy_alerts()
        recommendations = VendorIntelligenceService.get_vendor_recommendations()
        
        # Calculate aggregate metrics
        total_spend = sum(v['total_spend_12m'] for v in vendor_performance)
        total_vendors = len(vendor_performance)
        avg_spend_per_vendor = total_spend / total_vendors if total_vendors > 0 else 0
        
        return {
            'summary': {
                'total_vendors': total_vendors,
                'total_spend_12m': float(total_spend),
                'avg_spend_per_vendor': float(avg_spend_per_vendor),
                'alert_count': len(alerts)
            },
            'vendor_performance': vendor_performance,
            'bandwidth_analysis': bandwidth_analysis,
            'alerts': alerts,
            'recommendations': recommendations,
            'timestamp': timezone.now().isoformat()
        }
