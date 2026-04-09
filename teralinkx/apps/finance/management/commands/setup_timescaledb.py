"""
TimescaleDB Setup Management Command
Installs TimescaleDB extension and creates hypertables
"""
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Setup TimescaleDB extension and create hypertables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Only check if TimescaleDB is installed',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('\n=== TIMESCALEDB SETUP ===\n'))
        
        # Check if TimescaleDB is available
        if not self.check_timescaledb_available():
            self.stdout.write(self.style.ERROR(
                'TimescaleDB extension not available. '
                'Install timescaledb-postgresql package first.'
            ))
            return
        
        if options['check_only']:
            self.stdout.write(self.style.SUCCESS('✓ TimescaleDB is available'))
            return
        
        # Install extension
        if not self.install_extension():
            return
        
        # Create hypertables
        self.create_hypertables()
        
        self.stdout.write(self.style.SUCCESS('\n✓ TimescaleDB setup complete'))

    def check_timescaledb_available(self):
        """Check if TimescaleDB extension is available"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) 
                FROM pg_available_extensions 
                WHERE name = 'timescaledb'
            """)
            return cursor.fetchone()[0] > 0

    def install_extension(self):
        """Install TimescaleDB extension"""
        self.stdout.write('Installing TimescaleDB extension...')
        
        try:
            with connection.cursor() as cursor:
                # Check if already installed
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM pg_extension 
                    WHERE extname = 'timescaledb'
                """)
                
                if cursor.fetchone()[0] > 0:
                    self.stdout.write(self.style.WARNING('  ⚠ TimescaleDB already installed'))
                    return True
                
                # Install extension
                cursor.execute('CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE')
                self.stdout.write(self.style.SUCCESS('  ✓ TimescaleDB extension installed'))
                return True
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'  ✗ Failed to install TimescaleDB: {e}'))
            return False

    def create_hypertables(self):
        """Create hypertables for time-series data"""
        self.stdout.write('\nCreating hypertables...')
        
        hypertables = [
            {
                'table': 'finance_paymenttransaction',
                'time_column': 'created_at',
                'chunk_interval': '7 days',
                'description': 'Payment transactions'
            },
            {
                'table': 'finance_transactionqueue',
                'time_column': 'created_at',
                'chunk_interval': '7 days',
                'description': 'Transaction queue'
            },
        ]
        
        for config in hypertables:
            self.create_hypertable(
                config['table'],
                config['time_column'],
                config['chunk_interval'],
                config['description']
            )

    def create_hypertable(self, table_name, time_column, chunk_interval, description):
        """Create a single hypertable"""
        try:
            with connection.cursor() as cursor:
                # Check if already a hypertable
                cursor.execute("""
                    SELECT COUNT(*) 
                    FROM timescaledb_information.hypertables 
                    WHERE hypertable_name = %s
                """, [table_name.split('_')[1]])  # Remove app prefix
                
                if cursor.fetchone()[0] > 0:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠ {description} already a hypertable')
                    )
                    return
                
                # Drop primary key constraint temporarily
                cursor.execute(f"""
                    ALTER TABLE {table_name} DROP CONSTRAINT {table_name}_pkey CASCADE;
                """)
                
                # Add composite primary key with time column
                cursor.execute(f"""
                    ALTER TABLE {table_name} ADD PRIMARY KEY (id, {time_column});
                """)
                
                # Create hypertable
                cursor.execute(f"""
                    SELECT create_hypertable(
                        '{table_name}',
                        '{time_column}',
                        chunk_time_interval => INTERVAL '{chunk_interval}',
                        migrate_data => TRUE,
                        if_not_exists => TRUE
                    )
                """)
                
                self.stdout.write(
                    self.style.SUCCESS(f'  ✓ Created hypertable: {description}')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'  ✗ Failed to create hypertable {description}: {e}')
            )

    def get_hypertable_info(self):
        """Get information about existing hypertables"""
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    hypertable_name,
                    num_chunks,
                    compression_enabled,
                    total_bytes
                FROM timescaledb_information.hypertables
                ORDER BY hypertable_name
            """)
            
            results = cursor.fetchall()
            
            if results:
                self.stdout.write('\nExisting hypertables:')
                for row in results:
                    self.stdout.write(
                        f'  - {row[0]}: {row[1]} chunks, '
                        f'compression={row[2]}, size={row[3]} bytes'
                    )
            else:
                self.stdout.write('\nNo hypertables found')
