from django.core.management.base import BaseCommand
from django.db import transaction
from datetime import timedelta


class Command(BaseCommand):
    help = 'Populate database with initial data'

    def handle(self, *args, **options):
        self.stdout.write('Populating database with initial data...')
        
        try:
            self.populate_locations()
            self.populate_package_types()
            self.stdout.write(self.style.SUCCESS('Successfully populated database!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))

    @transaction.atomic
    def populate_locations(self):
        try:
            from locations.models import Location
            
            locations = [
                {'name': 'Nairobi', 'description': 'Nairobi - Capital City'},
                {'name': 'Mombasa', 'description': 'Mombasa - Coastal City'},
                {'name': 'Kisumu', 'description': 'Kisumu - Lakeside City'},
                {'name': 'Nakuru', 'description': 'Nakuru - Rift Valley'},
                {'name': 'Eldoret', 'description': 'Eldoret - North Rift'},
            ]
            
            for loc_data in locations:
                location, created = Location.objects.get_or_create(
                    name=loc_data['name'],
                    defaults={'description': loc_data.get('description', '')}
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created location: {location.name}'))
                else:
                    self.stdout.write(f'Location already exists: {location.name}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Location population skipped: {str(e)}'))

    @transaction.atomic
    def populate_package_types(self):
        try:
            from packages.models import PackageType
            
            packages = [
                {'name': 'Basic', 'code': 'BASIC', 'speed_limit_mbps': 5, 'price': 1500, 'duration': timedelta(days=30), 'description': 'Basic internet package'},
                {'name': 'Standard', 'code': 'STD', 'speed_limit_mbps': 10, 'price': 2500, 'duration': timedelta(days=30), 'description': 'Standard internet package'},
                {'name': 'Premium', 'code': 'PREM', 'speed_limit_mbps': 20, 'price': 4000, 'duration': timedelta(days=30), 'description': 'Premium internet package'},
                {'name': 'Ultra', 'code': 'ULTRA', 'speed_limit_mbps': 50, 'price': 7500, 'duration': timedelta(days=30), 'description': 'Ultra-fast internet package'},
                {'name': 'Enterprise', 'code': 'ENT', 'speed_limit_mbps': 100, 'price': 15000, 'duration': timedelta(days=30), 'description': 'Enterprise-grade internet'},
            ]
            
            for pkg_data in packages:
                package, created = PackageType.objects.get_or_create(
                    code=pkg_data['code'],
                    defaults={
                        'name': pkg_data['name'],
                        'speed_limit_mbps': pkg_data['speed_limit_mbps'],
                        'price': pkg_data['price'],
                        'duration': pkg_data['duration'],
                        'description': pkg_data['description'],
                        'is_active': True,
                        'is_public': True
                    }
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created package: {package.name}'))
                else:
                    self.stdout.write(f'Package already exists: {package.name}')
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Package population skipped: {str(e)}'))
