"""
Churn Prediction API Views
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q
from users.models import ClientH
from finance.models import ChurnPrediction, RetentionTask
from finance.ml_churn_service import predict_churn_ml


class ChurnPredictionListView(APIView):
    """List churn predictions with filtering"""
    
    def get(self, request):
        risk_level = request.query_params.get('risk_level')
        assigned = request.query_params.get('assigned')
        
        predictions = ChurnPrediction.objects.filter(is_active=True)
        
        if risk_level:
            predictions = predictions.filter(risk_level=risk_level)
        
        if assigned == 'true':
            predictions = predictions.filter(retention_tasks__isnull=False)
        elif assigned == 'false':
            predictions = predictions.filter(retention_tasks__isnull=True)
        
        data = []
        for pred in predictions[:100]:
            data.append({
                'id': pred.id,
                'customer': {
                    'id': pred.customer.id,
                    'account': pred.customer.account,
                    'phone': pred.customer.phone_number
                },
                'churn_score': float(pred.churn_score),
                'risk_level': pred.risk_level,
                'prediction_method': pred.prediction_method,
                'top_factors': pred.top_factors,
                'monthly_recurring_revenue': float(pred.monthly_recurring_revenue or 0),
                'prediction_date': pred.prediction_date.isoformat()
            })
        
        return Response({
            'count': len(data),
            'results': data
        })


class GenerateChurnPredictionsView(APIView):
    """Generate churn predictions for all customers"""
    
    def post(self, request):
        from finance.models_churn import ChurnPrediction as CP, RetentionTask as RT
        
        customers = ClientH.objects.exclude(status='inactive')[:100]
        created_count = 0
        
        for customer in customers:
            score, actual_method = predict_churn_ml(customer)
            risk_level = CP.get_risk_level(score)
            CP.objects.filter(customer=customer, is_active=True).update(is_active=False)
            pred = CP.objects.create(
                customer=customer,
                churn_score=score,
                risk_level=risk_level,
                prediction_method=actual_method,
                is_active=True
            )
            # Auto-create retention task for high/critical
            if risk_level in ['high', 'critical']:
                if not RT.objects.filter(customer=customer, status='pending').exists():
                    RT.create_retention_task(pred)
            created_count += 1
        
        return Response({'message': f'Generated {created_count} predictions', 'method': actual_method})


class RetentionTaskListView(APIView):
    """List retention tasks"""
    
    def get(self, request):
        from finance.models_churn import RetentionTask as RT
        task_status = request.query_params.get('status', 'pending')
        
        qs = RT.objects.select_related('customer').order_by('-priority_score')
        if task_status != 'all':
            qs = qs.filter(status=task_status)
        
        data = []
        for task in qs[:100]:
            data.append({
                'id': task.id,
                'customer': {
                    'id': task.customer.id,
                    'account': task.customer.account,
                    'phone': task.customer.phone_number
                },
                'action_type': task.action_type,
                'status': task.status,
                'priority_score': float(task.priority_score),
                'monthly_recurring_revenue': float(task.monthly_recurring_revenue or 0),
                'revenue_at_risk': float(task.revenue_at_risk or 0),
                'outcome': task.outcome,
                'created_at': task.created_at.isoformat()
            })
        
        return Response({'count': len(data), 'results': data})
    
    def post(self, request):
        from finance.models_churn import ChurnPrediction as CP, RetentionTask as RT
        customer_id = request.data.get('customer_id')
        churn_prediction_id = request.data.get('churn_prediction_id')
        try:
            pred = CP.objects.get(id=churn_prediction_id)
            task = RT.create_retention_task(pred)
            return Response({'id': task.id, 'message': 'Task created'})
        except CP.DoesNotExist:
            return Response({'error': 'Prediction not found'}, status=404)
