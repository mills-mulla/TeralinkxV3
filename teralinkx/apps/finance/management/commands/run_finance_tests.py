# apps/finance/management/commands/run_finance_tests.py
"""
Run Finance App Tests with Coverage
Executes test suite and generates coverage report.
"""
from django.core.management.base import BaseCommand
from django.test.utils import get_runner
from django.conf import settings
import sys


class Command(BaseCommand):
    help = 'Run finance app tests with coverage reporting'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--coverage',
            action='store_true',
            help='Generate coverage report'
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Verbose output'
        )
        parser.add_argument(
            '--failfast',
            action='store_true',
            help='Stop on first failure'
        )
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Finance App Test Suite ===\n'))
        
        # Configure test runner
        TestRunner = get_runner(settings)
        test_runner = TestRunner(
            verbosity=2 if options['verbose'] else 1,
            interactive=False,
            failfast=options['failfast']
        )
        
        # Run tests
        test_labels = ['finance.tests']
        
        if options['coverage']:
            self.stdout.write('Running tests with coverage...\n')
            try:
                import coverage
                cov = coverage.Coverage()
                cov.start()
                
                failures = test_runner.run_tests(test_labels)
                
                cov.stop()
                cov.save()
                
                self.stdout.write('\n' + '='*70)
                self.stdout.write(self.style.SUCCESS('Coverage Report:'))
                self.stdout.write('='*70 + '\n')
                
                cov.report()
                
                # Generate HTML report
                cov.html_report(directory='htmlcov')
                self.stdout.write(
                    self.style.SUCCESS(
                        '\nHTML coverage report generated in htmlcov/index.html'
                    )
                )
                
            except ImportError:
                self.stdout.write(
                    self.style.WARNING(
                        'Coverage.py not installed. Install with: pip install coverage'
                    )
                )
                failures = test_runner.run_tests(test_labels)
        else:
            failures = test_runner.run_tests(test_labels)
        
        # Summary
        self.stdout.write('\n' + '='*70)
        if failures:
            self.stdout.write(
                self.style.ERROR(f'Tests failed: {failures} failure(s)')
            )
            sys.exit(1)
        else:
            self.stdout.write(
                self.style.SUCCESS('All tests passed! ✓')
            )
            sys.exit(0)
