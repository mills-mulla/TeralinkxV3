"""
Revenue at Risk API Views
Executive dashboard endpoints for customer retention metrics.
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from finance.revenue_at_risk_service import RevenueAtRiskService
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def revenue_at_risk_summary(request):
    """
    Get complete revenue at risk dashboard summary.
    
    GET /api/finance/revenue-at-risk/
    
    Response:
    {
        "total_revenue_at_risk": 1250000.00,
        "week_over_week_trend": -5.2,
        "top_at_risk_accounts": [...],
        "retention_effectiveness": {...},
        "automated_offers_sent": {...},
        "relocated_customers_count": 3,
        "timestamp": "2025-01-XX..."
    }
    """
    try:
        summary = RevenueAtRiskService.get_dashboard_summary()
        return Response(summary, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching revenue at risk summary: {e}")
        return Response(
            {'error': 'Failed to fetch revenue at risk summary'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def top_at_risk_accounts(request):
    """
    Get top N accounts at risk.
    
    GET /api/finance/revenue-at-risk/top-accounts/?limit=10
    
    Query params:
    - limit: Number of accounts to return (default: 10)
    
    Response:
    [
        {
            "customer_id": 1,
            "account": "CLI000001",
            "phone": "254712345678",
            "mrr": 8500.00,
            "revenue_at_risk": 51000.00,
            "churn_score": 0.82,
            "risk_level": "critical",
            "top_factors": [...],
            "retention_task_status": "completed",
            "retention_action": "auto_discount_20",
            "outcome": "retained"
        }
    ]
    """
    try:
        limit = int(request.GET.get('limit', 10))
        accounts = RevenueAtRiskService.get_top_at_risk_accounts(limit)
        return Response(accounts, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching top at-risk accounts: {e}")
        return Response(
            {'error': 'Failed to fetch top at-risk accounts'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def retention_effectiveness(request):
    """
    Get retention effectiveness metrics.
    
    GET /api/finance/revenue-at-risk/effectiveness/
    
    Response:
    {
        "total_tasks": 45,
        "completed_tasks": 38,
        "retention_rate": 72.7,
        "outcomes": {
            "retained": 24,
            "churned": 9,
            "relocated": 5,
            "pending": 7
        },
        "revenue": {
            "total_at_risk": 2450000.00,
            "retained": 1780000.00,
            "saved_percentage": 72.7
        },
        "action_effectiveness": [...]
    }
    """
    try:
        effectiveness = RevenueAtRiskService.get_retention_effectiveness()
        return Response(effectiveness, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching retention effectiveness: {e}")
        return Response(
            {'error': 'Failed to fetch retention effectiveness'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def relocated_customers(request):
    """
    Get list of relocated customers (excluded from churn).
    
    GET /api/finance/revenue-at-risk/relocated/
    
    Response:
    [
        {
            "customer_id": 5,
            "account": "CLI000005",
            "mrr": 3200.00,
            "relocated_date": "2025-01-15",
            "notes": "Customer moved to Nairobi"
        }
    ]
    """
    try:
        relocated = RevenueAtRiskService.get_relocated_customers()
        return Response(relocated, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching relocated customers: {e}")
        return Response(
            {'error': 'Failed to fetch relocated customers'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def automated_offers_stats(request):
    """
    Get automated offers sent statistics.
    
    GET /api/finance/revenue-at-risk/offers/
    
    Response:
    {
        "total": 28,
        "by_type": [
            {"action_type": "auto_discount_20", "count": 8},
            {"action_type": "sms_discount_10", "count": 12},
            {"action_type": "sms_reengagement", "count": 8}
        ],
        "period": "30 days"
    }
    """
    try:
        offers = RevenueAtRiskService.get_automated_offers_sent()
        return Response(offers, status=status.HTTP_200_OK)
    
    except Exception as e:
        logger.error(f"Error fetching automated offers stats: {e}")
        return Response(
            {'error': 'Failed to fetch automated offers stats'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
