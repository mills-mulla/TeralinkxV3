#!/usr/bin/env python3
"""
Populate PackageType table with test packages (1-3 KSH) for payment testing
"""
import os
import sys
import django
from datetime import timedelta
from decimal import Decimal

# Add the project directory to Python path
sys.path.append('/home/ghost/Desktop/TeralinkxV3')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')

# Setup Django
django.setup()

from teralinkx.apps.packages.models import PackageType
from teralinkx.apps.locations.models import Location

def create_test_packages():
    """Create test packages with 1-3 KSH prices"""
    
    # Get default location (create if doesn't exist)
    try:
        default_location = Location.objects.filter(is_default=True).first()
        if not default_location:
            default_location = Location.objects.create(
                name="Test Location",
                location_code="TEST001",
                is_default=True,
                is_active=True
            )
            print(f"Created default location: {default_location.name}")
    except Exception as e:
        print(f"Error with location: {e}")
        default_location = None
    
    # Test packages data
    test_packages = [
        {
            'name': 'Test Mini 1KSH',
            'code': 'TEST1KSH',
            'price': Decimal('1.00'),
            'duration': timedelta(minutes=5),
            'data_limit_mb': 10,
            'speed_limit_mbps': 1,
            'device_limit': 1,
            'description': 'Test package - 1 KSH for 5 minutes'
        },
        {
            'name': 'Test Basic 2KSH', 
            'code': 'TEST2KSH',
            'price': Decimal('2.00'),
            'duration': timedelta(minutes=10),
            'data_limit_mb': 25,
            'speed_limit_mbps': 2,
            'device_limit': 1,
            'description': 'Test package - 2 KSH for 10 minutes'
        },
        {
            'name': 'Test Standard 3KSH',
            'code': 'TEST3KSH', 
            'price': Decimal('3.00'),
            'duration': timedelta(minutes=15),
            'data_limit_mb': 50,
            'speed_limit_mbps': 3,
            'device_limit': 2,
            'description': 'Test package - 3 KSH for 15 minutes'
        },
        {
            'name': 'Test Micro 1KSH Alt',
            'code': 'MICRO1',
            'price': Decimal('1.00'),
            'duration': timedelta(minutes=3),
            'data_limit_mb': 5,
            'speed_limit_mbps': 1,
            'device_limit': 1,
            'description': 'Alternative 1 KSH test package'
        },
        {
            'name': 'Test Quick 2KSH Alt',
            'code': 'QUICK2',
            'price': Decimal('2.00'),
            'duration': timedelta(minutes=8),
            'data_limit_mb': 20,
            'speed_limit_mbps': 2,
            'device_limit': 1,
            'description': 'Alternative 2 KSH test package'
        }
    ]
    
    created_count = 0
    updated_count = 0
    
    for pkg_data in test_packages:
        try:
            # Check if package already exists
            existing = PackageType.objects.filter(code=pkg_data['code']).first()
            
            if existing:
                # Update existing package
                for key, value in pkg_data.items():
                    if key != 'code':  # Don't update the code
                        setattr(existing, key, value)
                
                existing.is_active = True
                existing.is_visible = True
                if default_location:
                    existing.location = default_location
                existing.save()
                
                print(f"✅ Updated: {existing.name} - KSH {existing.price}")
                updated_count += 1
            else:
                # Create new package
                package = PackageType.objects.create(
                    name=pkg_data['name'],
                    code=pkg_data['code'],
                    price=pkg_data['price'],
                    duration=pkg_data['duration'],
                    data_limit_mb=pkg_data['data_limit_mb'],
                    speed_limit_mbps=pkg_data['speed_limit_mbps'],
                    device_limit=pkg_data['device_limit'],
                    description=pkg_data['description'],
                    location=default_location,
                    is_active=True,
                    is_visible=True,
                    package_type='internet',
                    billing_cycle='one_time'
                )
                
                print(f"🆕 Created: {package.name} - KSH {package.price}")
                created_count += 1
                
        except Exception as e:
            print(f"❌ Error processing {pkg_data['name']}: {e}")
    
    print(f"\n📊 Summary:")
    print(f"   Created: {created_count} packages")
    print(f"   Updated: {updated_count} packages")
    print(f"   Total test packages: {created_count + updated_count}")
    
    # List all test packages
    print(f"\n📋 All Test Packages (1-3 KSH):")
    test_pkgs = PackageType.objects.filter(
        price__lte=Decimal('3.00'),
        is_active=True
    ).order_by('price', 'name')
    
    for pkg in test_pkgs:
        print(f"   • {pkg.name} ({pkg.code}) - KSH {pkg.price} - {pkg.duration_display}")

if __name__ == '__main__':
    print("🚀 Populating PackageType table with test packages...")
    create_test_packages()
    print("✅ Done!")