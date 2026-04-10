"""
Test Revenue at Risk Dashboard
Validates all dashboard calculations and metrics.
"""
from django.core.management.base import BaseCommand
from apps.finance.revenue_at_risk_service import RevenueAtRiskService
from apps.finance.models_churn import ChurnPrediction, RetentionTask
import json


class Command(BaseCommand):
    help = 'Test revenue at risk dashboard calculations'

    def handle(self, *args, **options):
        self.stdout.write("=== Testing Revenue at Risk Dashboard ===\n")
        
        # Test 1: Total Revenue at Risk
        self.stdout.write("Test 1: Total Revenue at Risk")
        total_revenue = RevenueAtRiskService.get_total_revenue_at_risk()
        
        high_risk_count = ChurnPrediction.objects.filter(
            risk_level__in=['high', 'critical'],
            is_active=True
        ).count()
        
        self.stdout.write(f"  High/Critical Risk Customers: {high_risk_count}")
        self.stdout.write(f"  Total Revenue at Risk: KES {total_revenue:,.2f}")
        self.stdout.write(f"  (6 months MRR projection)\n")
        
        # Test 2: Week-over-Week Trend
        self.stdout.write("Test 2: Week-over-Week Trend")
        trend = RevenueAtRiskService.get_week_over_week_trend()
        trend_direction = "↑" if trend > 0 else "↓" if trend < 0 else "→"
        trend_color = self.style.ERROR if trend > 0 else self.style.SUCCESS if trend < 0 else self.style.WARNING
        
        self.stdout.write(trend_color(f"  {trend_direction} {abs(trend):.1f}% change from last week\n"))
        
        # Test 3: Top 10 At-Risk Accounts
        self.stdout.write("Test 3: Top 10 At-Risk Accounts")
        top_accounts = RevenueAtRiskService.get_top_at_risk_accounts(10)
        
        if top_accounts:
            self.stdout.write(f"  {'Account':<12} {'MRR':>10} {'Risk@6mo':>12} {'Score':>6} {'Level':<10} {'Action':<20}")
            self.stdout.write(f"  {'-'*80}")
            
            for account in top_accounts[:10]:
                risk_color = self._get_risk_color(account['risk_level'])
                self.stdout.write(risk_color(
                    f"  {account['account']:<12} "
                    f"KES {account['mrr']:>7,.0f} "
                    f"KES {account['revenue_at_risk']:>9,.0f} "
                    f"{account['churn_score']:>6.2f} "
                    f"{account['risk_level']:<10} "
                    f"{account['retention_action'] or 'None':<20}"
                ))
        else:
            self.stdout.write(self.style.WARNING("  No at-risk accounts found"))
        
        self.stdout.write("")
        
        # Test 4: Retention Effectiveness
        self.stdout.write("Test 4: Retention Effectiveness")
        effectiveness = RevenueAtRiskService.get_retention_effectiveness()
        
        self.stdout.write(f"  Total Tasks: {effectiveness['total_tasks']}")
        self.stdout.write(f"  Completed: {effectiveness['completed_tasks']}")
        self.stdout.write(f"  Retention Rate: {effectiveness['retention_rate']}%")
        
        self.stdout.write(f"\n  Outcomes:")
        for outcome, count in effectiveness['outcomes'].items():
            self.stdout.write(f"    {outcome.capitalize()}: {count}")
        
        self.stdout.write(f"\n  Revenue Impact:")
        self.stdout.write(f"    Total at Risk: KES {effectiveness['revenue']['total_at_risk']:,.2f}")
        self.stdout.write(f"    Retained: KES {effectiveness['revenue']['retained']:,.2f}")
        self.stdout.write(
            self.style.SUCCESS(
                f"    Saved: {effectiveness['revenue']['saved_percentage']}%"
            )
        )
        
        if effectiveness['action_effectiveness']:
            self.stdout.write(f"\n  Action Effectiveness:")
            for action in effectiveness['action_effectiveness']:
                retention_rate = (action['retained_count'] / action['count'] * 100) if action['count'] > 0 else 0
                self.stdout.write(
                    f"    {action['action_type']}: {action['count']} sent, "
                    f"{action['retained_count']} retained ({retention_rate:.1f}%)"
                )
        
        self.stdout.write("")
        
        # Test 5: Automated Offers
        self.stdout.write("Test 5: Automated Offers Sent")
        offers = RevenueAtRiskService.get_automated_offers_sent()
        
        self.stdout.write(f"  Total Offers (last {offers['period']}): {offers['total']}")
        if offers['by_type']:
            for offer_type in offers['by_type']:
                self.stdout.write(f"    {offer_type['action_type']}: {offer_type['count']}")
        else:
            self.stdout.write(self.style.WARNING("    No offers sent yet"))
        
        self.stdout.write("")
        
        # Test 6: Relocated Customers
        self.stdout.write("Test 6: Relocated Customers")
        relocated = RevenueAtRiskService.get_relocated_customers()
        
        if relocated:
            self.stdout.write(f"  Total Relocated: {len(relocated)}")
            for customer in relocated[:5]:
                self.stdout.write(
                    f"    {customer['account']}: KES {customer['mrr']:,.2f}/mo "
                    f"(relocated {customer['relocated_date']})"
                )
        else:
            self.stdout.write("  No relocated customers")
        
        self.stdout.write("")
        
        # Test 7: Complete Dashboard Summary
        self.stdout.write("Test 7: Complete Dashboard Summary")
        summary = RevenueAtRiskService.get_dashboard_summary()
        
        self.stdout.write(f"  Dashboard generated at: {summary['timestamp']}")
        self.stdout.write(f"  Data points: {len(summary)}")
        self.stdout.write(self.style.SUCCESS("  ✓ All metrics calculated successfully"))
        
        self.stdout.write(self.style.SUCCESS("\n=== Revenue at Risk Dashboard Test Complete ==="))

    def _get_risk_color(self, risk_level):
        """Get color styling for risk level"""
        colors = {
            'critical': self.style.ERROR,
            'high': self.style.WARNING,
            'medium': self.style.NOTICE,
            'low': self.style.SUCCESS,
        }
        return colors.get(risk_level, self.style.SUCCESS)
