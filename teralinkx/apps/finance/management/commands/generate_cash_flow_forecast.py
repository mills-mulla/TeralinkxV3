"""
Generate Cash Flow Forecast
Uses Prophet to forecast revenue, expenses, and net cash flow.
"""
from django.core.management.base import BaseCommand
from finance.cashflow_service import CashFlowForecastService


class Command(BaseCommand):
    help = 'Generate cash flow forecasts using Prophet'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--horizon',
            type=int,
            default=90,
            choices=[30, 90, 180],
            help='Forecast horizon in days (default: 90)'
        )
        parser.add_argument(
            '--type',
            type=str,
            default='all',
            choices=['revenue', 'expense', 'net', 'all'],
            help='Forecast type (default: all)'
        )
    
    def handle(self, *args, **options):
        horizon = options['horizon']
        forecast_type = options['type']
        
        self.stdout.write(self.style.SUCCESS(f'\n=== CASH FLOW FORECASTING ({horizon} days) ===\n'))
        
        service = CashFlowForecastService()
        
        if not service.prophet_available:
            self.stdout.write(self.style.ERROR('✗ Prophet not installed'))
            self.stdout.write(self.style.WARNING('  Install with: pip install prophet'))
            return
        
        self.stdout.write(self.style.SUCCESS('✓ Prophet available\n'))
        
        # Generate forecasts
        if forecast_type in ['revenue', 'all']:
            self._generate_revenue_forecasts(service, horizon)
        
        if forecast_type in ['expense', 'all']:
            self._generate_expense_forecasts(service, horizon)
        
        if forecast_type in ['net', 'all']:
            self._generate_net_forecasts(service, horizon)
        
        # Show alerts
        self._show_alerts()
        
        self.stdout.write(self.style.SUCCESS('\n=== FORECASTING COMPLETE ==='))
    
    def _generate_revenue_forecasts(self, service, horizon):
        """Generate revenue forecasts for all scenarios"""
        self.stdout.write('1. Generating Revenue Forecasts...')
        
        for scenario in ['optimistic', 'base', 'conservative']:
            self.stdout.write(f'   {scenario.capitalize()}...', ending='')
            
            forecast = service.generate_revenue_forecast(horizon, scenario)
            
            if forecast:
                self.stdout.write(self.style.SUCCESS(' ✓'))
                self.stdout.write(
                    f'      Total: KES {forecast.total_forecasted:,.2f} | '
                    f'Daily Avg: KES {forecast.average_daily:,.2f}'
                )
            else:
                self.stdout.write(self.style.ERROR(' ✗ Failed'))
        
        self.stdout.write('')
    
    def _generate_expense_forecasts(self, service, horizon):
        """Generate expense forecasts for all scenarios"""
        self.stdout.write('2. Generating Expense Forecasts...')
        
        for scenario in ['optimistic', 'base', 'conservative']:
            self.stdout.write(f'   {scenario.capitalize()}...', ending='')
            
            forecast = service.generate_expense_forecast(horizon, scenario)
            
            if forecast:
                self.stdout.write(self.style.SUCCESS(' ✓'))
                self.stdout.write(
                    f'      Total: KES {forecast.total_forecasted:,.2f} | '
                    f'Daily Avg: KES {forecast.average_daily:,.2f}'
                )
            else:
                self.stdout.write(self.style.ERROR(' ✗ Failed'))
        
        self.stdout.write('')
    
    def _generate_net_forecasts(self, service, horizon):
        """Generate net cash flow forecasts"""
        self.stdout.write('3. Generating Net Cash Flow Forecasts...')
        
        forecasts = service.generate_net_cash_flow_forecast(horizon)
        
        for scenario, forecast in forecasts.items():
            if forecast:
                self.stdout.write(self.style.SUCCESS(f'   {scenario.capitalize()} ✓'))
                self.stdout.write(
                    f'      Net: KES {forecast.total_forecasted:,.2f} | '
                    f'Daily Avg: KES {forecast.average_daily:,.2f}'
                )
            else:
                self.stdout.write(self.style.ERROR(f'   {scenario.capitalize()} ✗'))
        
        self.stdout.write('')
    
    def _show_alerts(self):
        """Show generated alerts"""
        from finance.models_cashflow import CashFlowAlert
        
        active_alerts = CashFlowAlert.get_active_alerts()
        
        if active_alerts.exists():
            self.stdout.write('4. Alerts Generated:')
            
            for alert in active_alerts[:5]:
                severity_style = {
                    'critical': self.style.ERROR,
                    'warning': self.style.WARNING,
                    'info': self.style.NOTICE,
                }.get(alert.severity, self.style.SUCCESS)
                
                self.stdout.write(severity_style(
                    f'   [{alert.get_severity_display().upper()}] {alert.title}'
                ))
                self.stdout.write(f'      {alert.message}')
            
            if active_alerts.count() > 5:
                self.stdout.write(f'   ... and {active_alerts.count() - 5} more alerts')
        else:
            self.stdout.write(self.style.SUCCESS('4. No alerts generated'))
