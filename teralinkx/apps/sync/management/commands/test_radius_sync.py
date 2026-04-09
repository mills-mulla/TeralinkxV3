# apps/sync/management/commands/test_radius_sync.py
from django.core.management.base import BaseCommand
from sync.radius_sync import RadiusUsageSyncService


class Command(BaseCommand):
    help = 'Manually test RADIUS usage sync'

    def add_arguments(self, parser):
        parser.add_argument(
            '--voucher',
            type=str,
            help='Sync specific voucher code',
        )
        parser.add_argument(
            '--critical',
            action='store_true',
            help='Sync only critical vouchers (>80% data used)',
        )

    def handle(self, *args, **options):
        voucher_code = options.get('voucher')
        critical_only = options.get('critical')

        if voucher_code:
            self.stdout.write(f'Syncing voucher: {voucher_code}')
            result = RadiusUsageSyncService.sync_single_voucher(voucher_code)
            
            if result['success']:
                data = result['data']
                self.stdout.write(self.style.SUCCESS(f'\n✓ Success!'))
                self.stdout.write(f"  Sessions: {data['total_sessions']}")
                self.stdout.write(f"  Downloaded: {data['total_downloaded'] / 1024 / 1024:.2f} MB")
                self.stdout.write(f"  Uploaded: {data['total_uploaded'] / 1024 / 1024:.2f} MB")
                self.stdout.write(f"  Active: {data['active_sessions']}")
            else:
                self.stdout.write(self.style.ERROR(f'✗ Failed: {result["error"]}'))
        
        elif critical_only:
            self.stdout.write('Syncing critical vouchers (>80% data used)...')
            result = RadiusUsageSyncService.sync_critical_vouchers()
            self.stdout.write(self.style.SUCCESS(f'\n✓ Complete!'))
            self.stdout.write(f"  Synced: {result['synced']}")
            self.stdout.write(f"  Failed: {result['failed']}")
            self.stdout.write(f"  Total: {result['total']}")
        
        else:
            self.stdout.write('Syncing all active vouchers...')
            result = RadiusUsageSyncService.sync_active_vouchers()
            self.stdout.write(self.style.SUCCESS(f'\n✓ Complete!'))
            self.stdout.write(f"  Synced: {result['synced']}")
            self.stdout.write(f"  Failed: {result['failed']}")
            self.stdout.write(f"  Total: {result['total']}")
