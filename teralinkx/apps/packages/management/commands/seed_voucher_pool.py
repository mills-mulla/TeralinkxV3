# apps/packages/management/commands/seed_voucher_pool.py
"""
Management command to pre-populate the AvailableVoucher fallback pool.

Usage:
    python manage.py seed_voucher_pool                    # default: 10 per package per location
    python manage.py seed_voucher_pool --count 20         # custom count
    python manage.py seed_voucher_pool --package 1HR      # specific package code
    python manage.py seed_voucher_pool --dry-run          # preview without creating
"""
import uuid
from django.core.management.base import BaseCommand
from django.utils import timezone
from packages.models import PackageType, AvailableVoucher
from locations.models import Location


class Command(BaseCommand):
    help = 'Seed the AvailableVoucher fallback pool for all active packages'

    def add_arguments(self, parser):
        parser.add_argument('--count',   type=int, default=10,  help='Vouchers per package per location')
        parser.add_argument('--package', type=str, default=None, help='Specific package code (default: all active)')
        parser.add_argument('--dry-run', action='store_true',    help='Preview without creating')

    def handle(self, *args, **options):
        count    = options['count']
        pkg_code = options['package']
        dry_run  = options['dry_run']

        packages = PackageType.objects.filter(is_active=True)
        if pkg_code:
            packages = packages.filter(code=pkg_code)

        locations = Location.objects.filter(is_active=True)

        if not packages.exists():
            self.stdout.write(self.style.ERROR('No active packages found'))
            return

        if not locations.exists():
            self.stdout.write(self.style.ERROR('No active locations found'))
            return

        batch_id = f"seed_{timezone.now().strftime('%Y%m%d_%H%M%S')}"
        total_created = 0

        for package in packages:
            for location in locations:
                # Count existing unused vouchers for this package+location
                existing = AvailableVoucher.objects.filter(
                    package=package,
                    location=location,
                    is_used=False
                ).count()

                needed = max(0, count - existing)

                if needed == 0:
                    self.stdout.write(
                        f'  {package.code} @ {location.name}: already has {existing} — skipping'
                    )
                    continue

                self.stdout.write(
                    f'  {package.code} @ {location.name}: {existing} existing, creating {needed}'
                )

                if not dry_run:
                    vouchers = [
                        AvailableVoucher(
                            voucher_code=f'FB-{uuid.uuid4().hex[:10].upper()}',
                            voucher_type='pre_generated',
                            package=package,
                            location=location,
                            batch_id=batch_id,
                            valid_until=timezone.now() + timezone.timedelta(days=30),
                        )
                        for _ in range(needed)
                    ]
                    AvailableVoucher.objects.bulk_create(vouchers, ignore_conflicts=True)
                    total_created += needed

        if dry_run:
            self.stdout.write(self.style.WARNING('Dry run — nothing created'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {total_created} fallback vouchers (batch: {batch_id})'))
