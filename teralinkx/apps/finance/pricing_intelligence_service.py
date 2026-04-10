# apps/finance/pricing_intelligence_service.py
"""
Pricing Intelligence Service
Analyzes package pricing, elasticity, and performance for strategic pricing decisions.
"""
from django.db.models import Count, Sum, Avg, Q, F
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class PricingIntelligenceService:
    """Service for pricing analysis and recommendations"""
    
    @staticmethod
    def get_package_performance():
        """Analyze performance metrics for all packages"""
        from apps.users.models import ClientH
        from finance.models import TransactionQueue, PaymentTransaction
        
        # Get all active packages
        packages = ClientH.objects.values('package_name').annotate(
            customer_count=Count('id'),
            total_revenue=Sum('transactionqueue__price', filter=Q(transactionqueue__status='completed')),
            avg_revenue_per_customer=Avg('transactionqueue__price', filter=Q(transactionqueue__status='completed'))
        ).filter(customer_count__gt=0).order_by('-total_revenue')
        
        package_metrics = []
        
        for package in packages:
            package_name = package['package_name'] or 'Unknown'
            customer_count = package['customer_count']
            total_revenue = package['total_revenue'] or 0
            arpu = package['avg_revenue_per_customer'] or 0
            
            # Calculate churn rate for this package
            churned_count = ClientH.objects.filter(
                package_name=package_name,
                status='inactive',
                updated_at__gte=timezone.now() - timedelta(days=30)
            ).count()
            
            churn_rate = (churned_count / customer_count * 100) if customer_count > 0 else 0
            
            # Calculate revenue per GB (if bandwidth data available)
            # Placeholder - would need actual bandwidth usage data
            revenue_per_gb = 0
            
            package_metrics.append({
                'package_name': package_name,
                'customer_count': customer_count,
                'total_revenue': float(total_revenue),
                'arpu': float(arpu),
                'churn_rate_pct': float(churn_rate),
                'revenue_per_gb': float(revenue_per_gb),
                'market_share_pct': 0  # Calculate after getting total
            })
        
        # Calculate market share
        total_customers = sum(p['customer_count'] for p in package_metrics)
        for package in package_metrics:
            package['market_share_pct'] = (package['customer_count'] / total_customers * 100) if total_customers > 0 else 0
        
        return package_metrics
    
    @staticmethod
    def analyze_price_elasticity(package_name, months=6):
        """
        Analyze price elasticity for a package.
        Requires historical pricing data and churn correlation.
        """
        from apps.users.models import ClientH
        
        # Get historical data points
        # This is simplified - real implementation would need price history table
        
        current_customers = ClientH.objects.filter(
            package_name=package_name
        ).exclude(status='inactive').count()
        
        churned_customers = ClientH.objects.filter(
            package_name=package_name,
            status='inactive',
            updated_at__gte=timezone.now() - timedelta(days=30*months)
        ).count()
        
        total_customers = current_customers + churned_customers
        churn_rate = (churned_customers / total_customers * 100) if total_customers > 0 else 0
        
        # Elasticity calculation (simplified)
        # Real implementation would correlate price changes with churn
        elasticity_score = 0.5  # Placeholder
        
        return {
            'package_name': package_name,
            'current_customers': current_customers,
            'churn_rate_pct': float(churn_rate),
            'elasticity_score': elasticity_score,
            'recommendation': PricingIntelligenceService._get_elasticity_recommendation(
                churn_rate, elasticity_score
            )
        }
    
    @staticmethod
    def _get_elasticity_recommendation(churn_rate, elasticity_score):
        """Generate pricing recommendation based on elasticity"""
        if churn_rate > 10:
            return "High churn detected - consider price reduction or value-add features"
        elif churn_rate < 3 and elasticity_score < 0.3:
            return "Low price sensitivity - opportunity for price increase"
        else:
            return "Pricing appears optimal - monitor for changes"
    
    @staticmethod
    def get_upgrade_downgrade_analysis():
        """Analyze package upgrade and downgrade patterns"""
        from apps.users.models import ClientH
        
        # Track package changes (requires package history tracking)
        # Simplified version - would need PackageChangeHistory model
        
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        # Placeholder data structure
        analysis = {
            'upgrades': {
                'count': 0,
                'revenue_impact': 0,
                'common_paths': []
            },
            'downgrades': {
                'count': 0,
                'revenue_impact': 0,
                'common_paths': []
            },
            'net_revenue_change': 0
        }
        
        return analysis
    
    @staticmethod
    def get_competitive_positioning():
        """
        Get competitive positioning data.
        Requires manual input of competitor pricing.
        """
        # This would typically come from a CompetitorPricing model
        # For now, return structure for manual data entry
        
        return {
            'message': 'Competitive pricing data requires manual input',
            'structure': {
                'competitor_name': 'string',
                'package_name': 'string',
                'price': 'decimal',
                'features': 'list',
                'last_updated': 'datetime'
            },
            'recommendation': 'Create CompetitorPricing model to track market positioning'
        }
    
    @staticmethod
    def get_pricing_recommendations():
        """Generate data-driven pricing recommendations"""
        package_performance = PricingIntelligenceService.get_package_performance()
        
        recommendations = []
        
        for package in package_performance:
            # High churn packages
            if package['churn_rate_pct'] > 8:
                recommendations.append({
                    'package': package['package_name'],
                    'type': 'retention_risk',
                    'priority': 'high',
                    'recommendation': f"Package has {package['churn_rate_pct']:.1f}% churn - review pricing and value proposition",
                    'estimated_impact': f"Reducing churn by 3% could save KES {package['total_revenue'] * 0.03:,.2f}/month"
                })
            
            # Low market share but high ARPU
            if package['market_share_pct'] < 10 and package['arpu'] > 3000:
                recommendations.append({
                    'package': package['package_name'],
                    'type': 'growth_opportunity',
                    'priority': 'medium',
                    'recommendation': f"High ARPU (KES {package['arpu']:,.2f}) but low market share - consider marketing push",
                    'estimated_impact': f"Doubling customers could add KES {package['total_revenue']:,.2f}/month"
                })
            
            # Package consolidation opportunity
            if package['customer_count'] < 20:
                recommendations.append({
                    'package': package['package_name'],
                    'type': 'consolidation',
                    'priority': 'low',
                    'recommendation': f"Only {package['customer_count']} customers - consider consolidating with similar package",
                    'estimated_impact': 'Reduced operational complexity'
                })
        
        return recommendations
    
    @staticmethod
    def get_dashboard_summary():
        """Get complete pricing intelligence dashboard"""
        package_performance = PricingIntelligenceService.get_package_performance()
        recommendations = PricingIntelligenceService.get_pricing_recommendations()
        
        # Calculate aggregate metrics
        total_revenue = sum(p['total_revenue'] for p in package_performance)
        weighted_arpu = sum(p['arpu'] * p['customer_count'] for p in package_performance) / sum(p['customer_count'] for p in package_performance) if package_performance else 0
        weighted_churn = sum(p['churn_rate_pct'] * p['customer_count'] for p in package_performance) / sum(p['customer_count'] for p in package_performance) if package_performance else 0
        
        return {
            'summary': {
                'total_packages': len(package_performance),
                'total_revenue': float(total_revenue),
                'average_arpu': float(weighted_arpu),
                'average_churn_rate': float(weighted_churn)
            },
            'package_performance': package_performance,
            'recommendations': recommendations,
            'timestamp': timezone.now().isoformat()
        }
