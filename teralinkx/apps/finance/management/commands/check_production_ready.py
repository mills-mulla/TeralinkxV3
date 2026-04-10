# apps/finance/management/commands/check_production_ready.py
"""
Production Readiness Check
Validates system is ready for production deployment.
"""
from django.core.management.base import BaseCommand
from django.conf import settings
from apps.finance.health_checks import HealthCheckService
import sys


class Command(BaseCommand):
    help = 'Check if finance app is production ready'
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('Finance App Production Readiness Check'))
        self.stdout.write(self.style.SUCCESS('='*70 + '\n'))
        
        checks_passed = 0
        checks_failed = 0
        checks_warning = 0
        
        # 1. Check Dependencies
        self.stdout.write(self.style.WARNING('1. Checking Dependencies...'))
        deps_ok = self.check_dependencies()
        if deps_ok:
            checks_passed += 1
        else:
            checks_failed += 1
        
        # 2. Check Database
        self.stdout.write(self.style.WARNING('\n2. Checking Database...'))
        db_check = HealthCheckService.check_database()
        if db_check['status'] == 'healthy':
            self.stdout.write(self.style.SUCCESS(f"  ✓ {db_check['message']}"))
            checks_passed += 1
        else:
            self.stdout.write(self.style.ERROR(f"  ✗ {db_check['message']}"))
            checks_failed += 1
        
        # 3. Check Redis
        self.stdout.write(self.style.WARNING('\n3. Checking Redis...'))
        redis_check = HealthCheckService.check_redis()
        if redis_check['status'] == 'healthy':
            self.stdout.write(self.style.SUCCESS(f"  ✓ {redis_check['message']}"))
            checks_passed += 1
        else:
            self.stdout.write(self.style.ERROR(f"  ✗ {redis_check['message']}"))
            checks_failed += 1
        
        # 4. Check Celery
        self.stdout.write(self.style.WARNING('\n4. Checking Celery...'))
        celery_check = HealthCheckService.check_celery()
        if celery_check['status'] == 'healthy':
            self.stdout.write(self.style.SUCCESS(f"  ✓ {celery_check['message']}"))
            checks_passed += 1
        elif celery_check['status'] == 'unhealthy':
            self.stdout.write(self.style.ERROR(f"  ✗ {celery_check['message']}"))
            self.stdout.write(self.style.WARNING("    Start Celery workers with: celery -A teralinkx worker -l info"))
            checks_warning += 1
        
        # 5. Check TimescaleDB
        self.stdout.write(self.style.WARNING('\n5. Checking TimescaleDB...'))
        ts_check = HealthCheckService.check_timescaledb()
        if ts_check['status'] == 'healthy':
            self.stdout.write(self.style.SUCCESS(f"  ✓ {ts_check['message']}"))
            checks_passed += 1
        elif ts_check['status'] == 'warning':
            self.stdout.write(self.style.WARNING(f"  ⚠ {ts_check['message']}"))
            checks_warning += 1
        
        # 6. Check Payment Gateway
        self.stdout.write(self.style.WARNING('\n6. Checking Payment Gateway...'))
        pg_check = HealthCheckService.check_payment_gateway()
        if pg_check['status'] == 'healthy':
            self.stdout.write(self.style.SUCCESS(f"  ✓ {pg_check['message']}"))
            checks_passed += 1
        else:
            self.stdout.write(self.style.WARNING(f"  ⚠ {pg_check['message']}"))
            checks_warning += 1
        
        # 7. Check Settings
        self.stdout.write(self.style.WARNING('\n7. Checking Django Settings...'))
        settings_ok = self.check_settings()
        if settings_ok:
            checks_passed += 1
        else:
            checks_failed += 1
        
        # 8. Check URLs
        self.stdout.write(self.style.WARNING('\n8. Checking URL Configuration...'))
        urls_ok = self.check_urls()
        if urls_ok:
            checks_passed += 1
        else:
            checks_warning += 1
        
        # Summary
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('Summary:'))
        self.stdout.write('='*70)
        self.stdout.write(f"  Passed:  {checks_passed}")
        self.stdout.write(f"  Warnings: {checks_warning}")
        self.stdout.write(f"  Failed:  {checks_failed}")
        self.stdout.write('='*70 + '\n')
        
        if checks_failed > 0:
            self.stdout.write(
                self.style.ERROR(
                    '✗ NOT PRODUCTION READY - Fix failed checks before deploying'
                )
            )
            sys.exit(1)
        elif checks_warning > 0:
            self.stdout.write(
                self.style.WARNING(
                    '⚠ PRODUCTION READY WITH WARNINGS - Review warnings before deploying'
                )
            )
            sys.exit(0)
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    '✓ PRODUCTION READY - All checks passed!'
                )
            )
            sys.exit(0)
    
    def check_dependencies(self):
        """Check required dependencies are installed"""
        required_packages = [
            ('reportlab', 'PDF export'),
            ('pptx', 'PowerPoint export'),
            ('celery', 'Task queue'),
            ('redis', 'Caching'),
        ]
        
        all_ok = True
        for package, purpose in required_packages:
            try:
                __import__(package)
                self.stdout.write(self.style.SUCCESS(f"  ✓ {package} installed ({purpose})"))
            except ImportError:
                self.stdout.write(self.style.ERROR(f"  ✗ {package} missing ({purpose})"))
                self.stdout.write(f"    Install with: pip install {package}")
                all_ok = False
        
        return all_ok
    
    def check_settings(self):
        """Check Django settings for production"""
        all_ok = True
        
        # Check DEBUG
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING("  ⚠ DEBUG=True (should be False in production)"))
            all_ok = False
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ DEBUG=False"))
        
        # Check SECRET_KEY
        if settings.SECRET_KEY == 'django-insecure-default-key':
            self.stdout.write(self.style.ERROR("  ✗ Using default SECRET_KEY"))
            all_ok = False
        else:
            self.stdout.write(self.style.SUCCESS("  ✓ SECRET_KEY configured"))
        
        # Check ALLOWED_HOSTS
        if not settings.ALLOWED_HOSTS or settings.ALLOWED_HOSTS == ['*']:
            self.stdout.write(self.style.WARNING("  ⚠ ALLOWED_HOSTS not properly configured"))
        else:
            self.stdout.write(self.style.SUCCESS(f"  ✓ ALLOWED_HOSTS configured: {settings.ALLOWED_HOSTS}"))
        
        return all_ok
    
    def check_urls(self):
        """Check URL configuration"""
        from django.urls import get_resolver
        
        resolver = get_resolver()
        url_patterns = [p.pattern._route for p in resolver.url_patterns if hasattr(p.pattern, '_route')]
        
        required_urls = [
            'health/',
            'finance/api/pricing/',
            'finance/api/vendors/',
            'finance/api/board-report/'
        ]
        
        all_ok = True
        for url in required_urls:
            if any(url in pattern for pattern in url_patterns):
                self.stdout.write(self.style.SUCCESS(f"  ✓ {url} configured"))
            else:
                self.stdout.write(self.style.WARNING(f"  ⚠ {url} not found"))
                all_ok = False
        
        return all_ok
