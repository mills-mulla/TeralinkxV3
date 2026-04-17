# apps/finance/management/commands/optimize_timescaledb.py
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = 'Complete TimescaleDB rollout to 100% and add compression + continuous aggregates'

    def handle(self, *args, **options):
        self._ramp_to_100()
        self._enable_compression()
        self._add_continuous_aggregates()
        self._add_retention_policy()
        self.stdout.write(self.style.SUCCESS('\n✅ TimescaleDB optimization complete'))

    def _ramp_to_100(self):
        """Ramp feature flag to 100%"""
        from core.models import FeatureFlag
        flag, _ = FeatureFlag.objects.get_or_create(
            name='use_timescaledb_payments',
            defaults={'enabled': True, 'rollout_percentage': 100}
        )
        flag.enabled = True
        flag.rollout_percentage = 100
        flag.save()
        self.stdout.write('📈 Feature flag: 100% rollout enabled')

    def _enable_compression(self):
        """Enable compression on hypertables — reduces storage 90%+"""
        with connection.cursor() as c:
            # TransactionQueue — compress after 7 days
            try:
                c.execute("""
                    ALTER TABLE finance_transactionqueue
                    SET (timescaledb.compress,
                         timescaledb.compress_orderby = 'created_at DESC',
                         timescaledb.compress_segmentby = 'status')
                """)
                c.execute("""
                    SELECT add_compression_policy('finance_transactionqueue',
                        INTERVAL '7 days', if_not_exists => TRUE)
                """)
                self.stdout.write('🗜️  TransactionQueue: compression enabled (7-day policy)')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  TransactionQueue compression: {e}'))

            # PaymentTransaction — compress after 7 days
            try:
                c.execute("""
                    ALTER TABLE finance_paymenttransaction
                    SET (timescaledb.compress,
                         timescaledb.compress_orderby = 'created_at DESC',
                         timescaledb.compress_segmentby = 'status')
                """)
                c.execute("""
                    SELECT add_compression_policy('finance_paymenttransaction',
                        INTERVAL '7 days', if_not_exists => TRUE)
                """)
                self.stdout.write('🗜️  PaymentTransaction: compression enabled (7-day policy)')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  PaymentTransaction compression: {e}'))

    def _add_continuous_aggregates(self):
        """Add continuous aggregates for fast KPI queries"""
        with connection.cursor() as c:
            # Daily revenue aggregate — replaces slow SUM queries on KPI dashboard
            try:
                c.execute("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS daily_revenue
                    WITH (timescaledb.continuous) AS
                    SELECT
                        time_bucket('1 day', created_at) AS day,
                        SUM(price) AS total_revenue,
                        COUNT(*) AS transaction_count,
                        AVG(price) AS avg_transaction
                    FROM finance_transactionqueue
                    WHERE status IN ('completed', 'processed')
                    GROUP BY day
                    WITH NO DATA
                """)
                c.execute("""
                    SELECT add_continuous_aggregate_policy('daily_revenue',
                        start_offset => INTERVAL '30 days',
                        end_offset   => INTERVAL '1 hour',
                        schedule_interval => INTERVAL '1 hour',
                        if_not_exists => TRUE)
                """)
                # Backfill historical data
                c.execute("""
                    CALL refresh_continuous_aggregate('daily_revenue',
                        NOW() - INTERVAL '45 days', NOW())
                """)
                self.stdout.write('📊 daily_revenue aggregate: created + backfilled')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  daily_revenue: {e}'))

            # Hourly transaction aggregate — for real-time monitoring
            try:
                c.execute("""
                    CREATE MATERIALIZED VIEW IF NOT EXISTS hourly_transactions
                    WITH (timescaledb.continuous) AS
                    SELECT
                        time_bucket('1 hour', created_at) AS hour,
                        status,
                        COUNT(*) AS count,
                        SUM(price) AS revenue
                    FROM finance_transactionqueue
                    GROUP BY hour, status
                    WITH NO DATA
                """)
                c.execute("""
                    SELECT add_continuous_aggregate_policy('hourly_transactions',
                        start_offset => INTERVAL '7 days',
                        end_offset   => INTERVAL '1 minute',
                        schedule_interval => INTERVAL '5 minutes',
                        if_not_exists => TRUE)
                """)
                c.execute("""
                    CALL refresh_continuous_aggregate('hourly_transactions',
                        NOW() - INTERVAL '7 days', NOW())
                """)
                self.stdout.write('📊 hourly_transactions aggregate: created + backfilled')
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  hourly_transactions: {e}'))

    def _add_retention_policy(self):
        """Keep raw data for 10 years (financial audit compliance)"""
        with connection.cursor() as c:
            for table in ['finance_transactionqueue', 'finance_paymenttransaction']:
                try:
                    c.execute(f"""
                        SELECT add_retention_policy('{table}',
                            INTERVAL '10 years', if_not_exists => TRUE)
                    """)
                    self.stdout.write(f'🗑️  {table}: 10-year retention policy added')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  {table} retention: {e}'))
