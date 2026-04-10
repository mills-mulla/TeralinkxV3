"""
Cash Flow Forecasting Service
Uses Prophet for time series forecasting of revenue, expenses, and cash flow.
"""
from django.db.models import Sum
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class CashFlowForecastService:
    """Service for generating cash flow forecasts using Prophet"""
    
    def __init__(self):
        try:
            from prophet import Prophet
            self.Prophet = Prophet
            self.prophet_available = True
        except ImportError:
            logger.error("Prophet not installed. Install with: pip install prophet")
            self.prophet_available = False
    
    def generate_revenue_forecast(self, horizon_days=90, scenario='base'):
        """
        Generate revenue forecast for specified horizon.
        
        Args:
            horizon_days: Forecast horizon (30, 90, 180)
            scenario: 'optimistic', 'base', 'conservative'
        
        Returns:
            CashFlowForecast object or None
        """
        if not self.prophet_available:
            logger.error("Prophet not available")
            return None
        
        try:
            # Extract historical revenue data
            historical_data = self._get_historical_revenue()
            
            if len(historical_data) < 30:
                logger.warning(f"Insufficient data: {len(historical_data)} days (need 30+)")
                return None
            
            # Train Prophet model
            model = self._train_prophet_model(historical_data, scenario)
            
            # Generate forecast
            forecast_df = self._generate_forecast(model, horizon_days)
            
            # Save to database
            from finance.models_cashflow import CashFlowForecast
            forecast = self._save_forecast(
                forecast_df,
                'revenue',
                scenario,
                horizon_days,
                len(historical_data)
            )
            
            # Check for alerts
            self._check_revenue_alerts(forecast)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating revenue forecast: {e}")
            return None
    
    def generate_expense_forecast(self, horizon_days=90, scenario='base'):
        """Generate expense forecast"""
        if not self.prophet_available:
            return None
        
        try:
            historical_data = self._get_historical_expenses()
            
            if len(historical_data) < 30:
                logger.warning(f"Insufficient expense data: {len(historical_data)} days")
                return None
            
            model = self._train_prophet_model(historical_data, scenario)
            forecast_df = self._generate_forecast(model, horizon_days)
            
            from finance.models_cashflow import CashFlowForecast
            forecast = self._save_forecast(
                forecast_df,
                'expense',
                scenario,
                horizon_days,
                len(historical_data)
            )
            
            self._check_expense_alerts(forecast)
            
            return forecast
            
        except Exception as e:
            logger.error(f"Error generating expense forecast: {e}")
            return None
    
    def generate_net_cash_flow_forecast(self, horizon_days=90):
        """
        Generate net cash flow forecast (revenue - expenses).
        Generates all 3 scenarios.
        """
        forecasts = {}
        
        for scenario in ['optimistic', 'base', 'conservative']:
            revenue_forecast = self.generate_revenue_forecast(horizon_days, scenario)
            expense_forecast = self.generate_expense_forecast(horizon_days, scenario)
            
            if revenue_forecast and expense_forecast:
                net_forecast = self._calculate_net_cash_flow(
                    revenue_forecast,
                    expense_forecast,
                    scenario,
                    horizon_days
                )
                forecasts[scenario] = net_forecast
        
        return forecasts
    
    def _get_historical_revenue(self, days=365):
        """Extract historical revenue data"""
        from finance.models import PaymentTransaction
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get daily revenue
        daily_revenue = PaymentTransaction.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date,
            status='completed'
        ).extra(
            select={'day': 'DATE(created_at)'}
        ).values('day').annotate(
            revenue=Sum('amount_base')
        ).order_by('day')
        
        # Convert to DataFrame
        data = []
        for item in daily_revenue:
            data.append({
                'ds': item['day'],
                'y': float(item['revenue'])
            })
        
        return pd.DataFrame(data)
    
    def _get_historical_expenses(self, days=365):
        """Extract historical expense data"""
        from finance.models import Expense
        
        end_date = timezone.now().date()
        start_date = end_date - timedelta(days=days)
        
        # Get daily expenses
        daily_expenses = Expense.objects.filter(
            expense_date__gte=start_date,
            expense_date__lte=end_date,
            approval_status='paid'
        ).values('expense_date').annotate(
            expense=Sum('amount')
        ).order_by('expense_date')
        
        # Convert to DataFrame
        data = []
        for item in daily_expenses:
            data.append({
                'ds': item['expense_date'],
                'y': float(item['expense'])
            })
        
        return pd.DataFrame(data)
    
    def _train_prophet_model(self, historical_data, scenario='base'):
        """Train Prophet model with scenario adjustments"""
        # Scenario-specific parameters
        if scenario == 'optimistic':
            interval_width = 0.10  # P10 (optimistic)
        elif scenario == 'conservative':
            interval_width = 0.90  # P90 (conservative)
        else:
            interval_width = 0.50  # P50 (base case)
        
        # Initialize Prophet
        model = self.Prophet(
            interval_width=interval_width,
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=True,
            changepoint_prior_scale=0.05
        )
        
        # Add monthly seasonality
        model.add_seasonality(
            name='monthly',
            period=30.5,
            fourier_order=5
        )
        
        # Fit model
        model.fit(historical_data)
        
        return model
    
    def _generate_forecast(self, model, horizon_days):
        """Generate forecast using trained model"""
        # Create future dataframe
        future = model.make_future_dataframe(periods=horizon_days)
        
        # Generate forecast
        forecast = model.predict(future)
        
        # Return only future dates
        return forecast.tail(horizon_days)
    
    def _save_forecast(self, forecast_df, forecast_type, scenario, horizon_days, training_size):
        """Save forecast to database"""
        from finance.models_cashflow import CashFlowForecast
        
        # Deactivate old forecasts
        CashFlowForecast.deactivate_old_forecasts(forecast_type, scenario, horizon_days)
        
        # Prepare forecast data
        forecast_data = []
        total_forecasted = 0
        
        for _, row in forecast_df.iterrows():
            value = max(0, row['yhat'])  # Ensure non-negative
            lower = max(0, row['yhat_lower'])
            upper = max(0, row['yhat_upper'])
            
            forecast_data.append({
                'date': row['ds'].strftime('%Y-%m-%d'),
                'value': float(value),
                'lower_bound': float(lower),
                'upper_bound': float(upper),
            })
            
            total_forecasted += value
        
        average_daily = total_forecasted / len(forecast_data) if forecast_data else 0
        
        # Create forecast
        forecast = CashFlowForecast.objects.create(
            forecast_date=timezone.now().date(),
            forecast_type=forecast_type,
            scenario=scenario,
            period_start=forecast_df.iloc[0]['ds'].date(),
            period_end=forecast_df.iloc[-1]['ds'].date(),
            horizon_days=horizon_days,
            forecast_data=forecast_data,
            total_forecasted=Decimal(str(total_forecasted)),
            average_daily=Decimal(str(average_daily)),
            training_data_size=training_size,
            training_period_days=365,
            is_active=True
        )
        
        return forecast
    
    def _calculate_net_cash_flow(self, revenue_forecast, expense_forecast, scenario, horizon_days):
        """Calculate net cash flow from revenue and expense forecasts"""
        from finance.models_cashflow import CashFlowForecast
        
        # Combine revenue and expense data
        net_data = []
        total_net = 0
        
        for rev_item in revenue_forecast.forecast_data:
            date_str = rev_item['date']
            
            # Find matching expense
            exp_item = next(
                (item for item in expense_forecast.forecast_data if item['date'] == date_str),
                {'value': 0, 'lower_bound': 0, 'upper_bound': 0}
            )
            
            net_value = rev_item['value'] - exp_item['value']
            net_lower = rev_item['lower_bound'] - exp_item['upper_bound']
            net_upper = rev_item['upper_bound'] - exp_item['lower_bound']
            
            net_data.append({
                'date': date_str,
                'value': net_value,
                'lower_bound': net_lower,
                'upper_bound': net_upper,
            })
            
            total_net += net_value
        
        average_daily = total_net / len(net_data) if net_data else 0
        
        # Deactivate old forecasts
        CashFlowForecast.deactivate_old_forecasts('net_cash_flow', scenario, horizon_days)
        
        # Create net cash flow forecast
        forecast = CashFlowForecast.objects.create(
            forecast_date=timezone.now().date(),
            forecast_type='net_cash_flow',
            scenario=scenario,
            period_start=revenue_forecast.period_start,
            period_end=revenue_forecast.period_end,
            horizon_days=horizon_days,
            forecast_data=net_data,
            total_forecasted=Decimal(str(total_net)),
            average_daily=Decimal(str(average_daily)),
            training_data_size=revenue_forecast.training_data_size,
            training_period_days=365,
            is_active=True
        )
        
        # Check for negative cash flow alerts
        self._check_cash_flow_alerts(forecast)
        
        return forecast
    
    def _check_revenue_alerts(self, forecast):
        """Check for revenue decline alerts"""
        from finance.models_cashflow import CashFlowAlert
        
        # Check if revenue is declining
        first_week = sum(item['value'] for item in forecast.forecast_data[:7])
        last_week = sum(item['value'] for item in forecast.forecast_data[-7:])
        
        if last_week < first_week * 0.8:  # 20% decline
            CashFlowAlert.objects.create(
                alert_type='revenue_decline',
                severity='warning',
                forecast=forecast,
                alert_date=timezone.now().date(),
                threshold_value=Decimal(str(first_week)),
                actual_value=Decimal(str(last_week)),
                title='Revenue Decline Forecast',
                message=f'Forecasted revenue declining by {((first_week - last_week) / first_week * 100):.1f}% over {forecast.horizon_days} days',
                recommended_action='Review pricing strategy and customer retention efforts'
            )
    
    def _check_expense_alerts(self, forecast):
        """Check for unusual expense alerts"""
        from finance.models_cashflow import CashFlowAlert
        
        # Check for expense spikes
        average = forecast.average_daily
        
        for item in forecast.forecast_data:
            if item['value'] > float(average) * 2:  # 2x average
                CashFlowAlert.objects.create(
                    alert_type='unusual_expense',
                    severity='info',
                    forecast=forecast,
                    alert_date=timezone.now().date(),
                    threshold_value=average * 2,
                    actual_value=Decimal(str(item['value'])),
                    title='Unusual Expense Forecast',
                    message=f'Forecasted expense spike on {item["date"]}: KES {item["value"]:,.2f}',
                    recommended_action='Review expense forecast and budget allocation'
                )
                break  # Only alert once
    
    def _check_cash_flow_alerts(self, forecast):
        """Check for cash flow alerts"""
        from finance.models_cashflow import CashFlowAlert
        
        # Check for negative cash flow
        negative_days = [item for item in forecast.forecast_data if item['value'] < 0]
        
        if negative_days:
            total_negative = sum(item['value'] for item in negative_days)
            
            CashFlowAlert.objects.create(
                alert_type='negative_cash_flow',
                severity='critical',
                forecast=forecast,
                alert_date=timezone.now().date(),
                threshold_value=Decimal('0'),
                actual_value=Decimal(str(total_negative)),
                title='Negative Cash Flow Forecast',
                message=f'{len(negative_days)} days with negative cash flow forecasted. Total deficit: KES {abs(total_negative):,.2f}',
                recommended_action='Urgent: Review expenses and accelerate revenue collection'
            )
        
        # Check for low cash position (< KES 500K)
        low_threshold = 500000
        low_days = [item for item in forecast.forecast_data if item['value'] < low_threshold]
        
        if low_days and forecast.scenario == 'conservative':
            CashFlowAlert.objects.create(
                alert_type='low_cash_position',
                severity='warning',
                forecast=forecast,
                alert_date=timezone.now().date(),
                threshold_value=Decimal(str(low_threshold)),
                actual_value=Decimal(str(min(item['value'] for item in low_days))),
                title='Low Cash Position Forecast',
                message=f'Cash position may fall below KES {low_threshold:,.0f} in conservative scenario',
                recommended_action='Consider securing additional funding or reducing expenses'
            )
