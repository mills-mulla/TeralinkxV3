from django.core.management.base import BaseCommand
from django.core.cache import cache
from finance.models import PaymentGateway


class Command(BaseCommand):
    help = 'Update payment gateway callback URLs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--gateway-type',
            type=str,
            default='mpesa',
            help='Gateway type to update (default: mpesa)'
        )
        parser.add_argument(
            '--callback-url',
            type=str,
            help='New callback URL'
        )
        parser.add_argument(
            '--webhook-url',
            type=str,
            help='New webhook URL (optional)'
        )
        parser.add_argument(
            '--list',
            action='store_true',
            help='List current gateway configurations'
        )

    def handle(self, *args, **options):
        if options['list']:
            self.list_gateways()
            return

        callback_url = options.get('callback_url')
        if not callback_url:
            self.stdout.write(
                self.style.ERROR('--callback-url is required when not using --list')
            )
            return

        gateway_type = options['gateway_type']
        webhook_url = options.get('webhook_url')

        try:
            gateway = PaymentGateway.objects.get(
                gateway_type=gateway_type,
                status='active',
                is_default=True
            )
            
            old_callback = gateway.callback_url
            old_webhook = gateway.webhook_url
            
            gateway.callback_url = callback_url
            if webhook_url:
                gateway.webhook_url = webhook_url
            
            gateway.save()
            
            # Clear cache
            cache.delete('mpesa_gateway_config')
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully updated {gateway_type} gateway:\n'
                    f'  Callback URL: {old_callback} → {callback_url}\n'
                    f'  Webhook URL: {old_webhook} → {gateway.webhook_url}\n'
                    f'  Cache cleared'
                )
            )
            
        except PaymentGateway.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'No active default gateway found for type: {gateway_type}'
                )
            )

    def list_gateways(self):
        gateways = PaymentGateway.objects.filter(status='active')
        
        if not gateways.exists():
            self.stdout.write(self.style.WARNING('No active gateways found'))
            return
            
        self.stdout.write(self.style.SUCCESS('Active Payment Gateways:'))
        self.stdout.write('-' * 60)
        
        for gateway in gateways:
            default_marker = ' (DEFAULT)' if gateway.is_default else ''
            test_marker = ' (TEST MODE)' if gateway.test_mode else ''
            
            self.stdout.write(
                f'Gateway: {gateway.name} ({gateway.gateway_type}){default_marker}{test_marker}\n'
                f'  Callback URL: {gateway.callback_url}\n'
                f'  Webhook URL: {gateway.webhook_url}\n'
                f'  Status: {gateway.status}\n'
            )