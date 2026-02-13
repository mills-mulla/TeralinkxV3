from django.core.management.base import BaseCommand
from finance.models import RevenueStream


class Command(BaseCommand):
    help = 'Create sample revenue streams for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample revenue streams...')
        
        streams = [
            {
                'name': 'Advertising Revenue',
                'category': 'ads_revenue',
                'target_revenue': 50000,
                'target_growth_rate': 15.0,
                'description': 'Revenue from banner, video, and native advertisements',
                'display_order': 1
            },
            {
                'name': 'Internet Voucher Sales',
                'category': 'voucher_sales',
                'target_revenue': 200000,
                'target_growth_rate': 10.0,
                'description': 'Revenue from internet voucher purchases',
                'display_order': 2
            },
            {
                'name': 'Data Package Subscriptions',
                'category': 'package_sales',
                'target_revenue': 150000,
                'target_growth_rate': 12.0,
                'description': 'Revenue from monthly data package subscriptions',
                'display_order': 3
            },
            {
                'name': 'Premium Services',
                'category': 'premium_services',
                'target_revenue': 75000,
                'target_growth_rate': 20.0,
                'description': 'VIP packages, priority support, premium features',
                'display_order': 4
            },
            {
                'name': 'Usage Charges',
                'category': 'usage_charges',
                'target_revenue': 100000,
                'target_growth_rate': 8.0,
                'description': 'Pay-as-you-go internet usage charges',
                'display_order': 5
            }
        ]
        
        created_count = 0
        for stream_data in streams:
            stream, created = RevenueStream.objects.get_or_create(
                name=stream_data['name'],
                defaults={
                    'category': stream_data['category'],
                    'is_active': True,
                    'target_revenue': stream_data['target_revenue'],
                    'target_growth_rate': stream_data['target_growth_rate'],
                    'description': stream_data['description'],
                    'display_order': stream_data['display_order']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {stream.name}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Already exists: {stream.name}'))
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Done! Created {created_count} new revenue streams.'))
