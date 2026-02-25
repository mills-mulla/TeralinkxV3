"""
Management command to check database connection health
Usage: python manage.py check_db_connections
"""
from django.core.management.base import BaseCommand
from django.db import connections
from django.conf import settings


class Command(BaseCommand):
    help = 'Check database connection health and statistics'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Database Connection Health Check ===\n'))
        
        for alias in connections:
            conn = connections[alias]
            db_settings = settings.DATABASES[alias]
            
            self.stdout.write(f"Database: {alias}")
            self.stdout.write(f"  Engine: {db_settings.get('ENGINE', 'N/A')}")
            self.stdout.write(f"  Host: {db_settings.get('HOST', 'N/A')}")
            self.stdout.write(f"  Name: {db_settings.get('NAME', 'N/A')}")
            self.stdout.write(f"  CONN_MAX_AGE: {db_settings.get('CONN_MAX_AGE', 'N/A')}s")
            
            # Check connection
            try:
                conn.ensure_connection()
                self.stdout.write(self.style.SUCCESS(f"  Status: ✓ Connected"))
                
                # Get connection info
                if hasattr(conn, 'connection') and conn.connection:
                    self.stdout.write(f"  Connection alive: Yes")
                else:
                    self.stdout.write(f"  Connection alive: No (will reconnect on next query)")
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Status: ✗ Error - {e}"))
            
            self.stdout.write("")
        
        # PostgreSQL specific stats
        self.stdout.write(self.style.SUCCESS('=== PostgreSQL Connection Stats ==='))
        try:
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        count(*) as total_connections,
                        count(*) FILTER (WHERE state = 'active') as active,
                        count(*) FILTER (WHERE state = 'idle') as idle,
                        count(*) FILTER (WHERE state = 'idle in transaction') as idle_in_transaction
                    FROM pg_stat_activity 
                    WHERE datname = current_database()
                """)
                row = cursor.fetchone()
                self.stdout.write(f"Total connections: {row[0]}")
                self.stdout.write(f"Active: {row[1]}")
                self.stdout.write(f"Idle: {row[2]}")
                self.stdout.write(f"Idle in transaction: {row[3]}")
                
                # Check for long-running queries
                cursor.execute("""
                    SELECT pid, usename, state, query_start, 
                           now() - query_start as duration, 
                           left(query, 50) as query
                    FROM pg_stat_activity 
                    WHERE datname = current_database() 
                      AND state = 'active'
                      AND now() - query_start > interval '10 seconds'
                    ORDER BY duration DESC
                    LIMIT 5
                """)
                long_queries = cursor.fetchall()
                if long_queries:
                    self.stdout.write(self.style.WARNING("\nLong-running queries (>10s):"))
                    for q in long_queries:
                        self.stdout.write(f"  PID {q[0]}: {q[4]} - {q[5]}")
                else:
                    self.stdout.write(self.style.SUCCESS("\nNo long-running queries"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error getting PostgreSQL stats: {e}"))
