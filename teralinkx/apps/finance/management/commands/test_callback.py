from django.core.management.base import BaseCommand
import requests
import json
from finance.payment_gateway import MpesaGatewayHelper


class Command(BaseCommand):
    help = 'Test payment callback endpoint'

    def add_arguments(self, parser):
        parser.add_argument(
            '--url',
            type=str,
            help='Custom callback URL to test (default: from gateway config)'
        )
        parser.add_argument(
            '--test-data',
            action='store_true',
            help='Send test M-Pesa callback data'
        )

    def handle(self, *args, **options):
        # Get callback URL
        if options.get('url'):
            callback_url = options['url']
        else:
            config = MpesaGatewayHelper.get_gateway_config()
            callback_url = config['callback_url']

        self.stdout.write(f'Testing callback URL: {callback_url}')

        # Test basic connectivity
        try:
            response = requests.post(
                callback_url,
                json={'test': 'connectivity'},
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            self.stdout.write(
                f'Response Status: {response.status_code}'
            )
            self.stdout.write(
                f'Response Body: {response.text[:200]}...'
            )
            
            if response.status_code == 400:
                self.stdout.write(
                    self.style.SUCCESS(
                        '✅ Endpoint is accessible (400 expected for test data)'
                    )
                )
            elif response.status_code == 200:
                self.stdout.write(
                    self.style.SUCCESS('✅ Endpoint is accessible and responding')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️ Unexpected response code: {response.status_code}'
                    )
                )

        except requests.exceptions.RequestException as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Connection failed: {e}')
            )
            return

        # Test with M-Pesa-like data if requested
        if options.get('test_data'):
            self.stdout.write('\nTesting with M-Pesa-like callback data...')
            
            test_callback_data = {
                "Body": {
                    "stkCallback": {
                        "MerchantRequestID": "test-merchant-123",
                        "CheckoutRequestID": "test-checkout-456",
                        "ResultCode": 0,
                        "ResultDesc": "The service request is processed successfully.",
                        "CallbackMetadata": {
                            "Item": [
                                {"Name": "Amount", "Value": 100},
                                {"Name": "MpesaReceiptNumber", "Value": "TEST123456"},
                                {"Name": "Balance", "Value": 0},
                                {"Name": "TransactionDate", "Value": "20261227232000"},
                                {"Name": "PhoneNumber", "Value": "254714787999"}
                            ]
                        }
                    }
                }
            }
            
            try:
                response = requests.post(
                    callback_url,
                    json=test_callback_data,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                self.stdout.write(
                    f'M-Pesa Test Response: {response.status_code}'
                )
                self.stdout.write(
                    f'Response: {response.text[:200]}...'
                )
                
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(
                            '✅ M-Pesa callback format accepted'
                        )
                    )
                elif response.status_code == 404:
                    self.stdout.write(
                        self.style.ERROR(
                            '❌ Transaction not found (expected for test data)'
                        )
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(
                            f'⚠️ Unexpected M-Pesa response: {response.status_code}'
                        )
                    )
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ M-Pesa test failed: {e}')
                )