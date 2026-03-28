#!/bin/bash
set -e

echo "🚀 Starting HIDS Engine..."
echo "Database: ${POSTGRES_HOST:-db}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-hids}"
echo "Redis: ${REDIS_HOST:-redis}:6379"
echo "ML Service: ${ML_SERVICE_URL:-http://hids_ml_service:5001}"

# Extract connection details
DB_HOST=${POSTGRES_HOST:-db}
DB_PORT=${POSTGRES_PORT:-5432}
REDIS_HOST_VAR=${REDIS_HOST:-redis}

# Wait for database
echo "Waiting for database at ${DB_HOST}:${DB_PORT}..."
while ! nc -z "$DB_HOST" "$DB_PORT"; do
  echo "  Database not ready, waiting..."
  sleep 2
done
echo "✅ Database is ready!"

# Wait for Redis
echo "Waiting for Redis at ${REDIS_HOST_VAR}:6379..."
while ! nc -z "$REDIS_HOST_VAR" 6379; do
  echo "  Redis not ready, waiting..."
  sleep 2
done
echo "✅ Redis is ready!"

# Test Redis connection
echo "Testing Redis connection..."
if redis-cli -h "$REDIS_HOST_VAR" ping | grep -q "PONG"; then
  echo "✅ Redis connection successful!"
else
  echo "⚠️  Redis connection test failed, but continuing..."
fi

# Wait for ML service
echo "Waiting for ML service..."
attempt=1
max_attempts=30
while ! nc -z hids_ml_service 5001 2>/dev/null; do
  if [[ $attempt -ge $max_attempts ]]; then
    echo "⚠️  ML service not available after ${max_attempts} attempts"
    echo "   Engine will start but ML predictions will fail"
    break
  fi
  echo "  ML service not ready, waiting... (attempt $attempt/$max_attempts)"
  sleep 2
  ((attempt++))
done

if nc -z hids_ml_service 5001 2>/dev/null; then
  echo "✅ ML service is ready!"
fi

# Initialize database schema
echo "📝 Initializing HIDS database schema..."
python3 << END
import psycopg2
import os
import sys

try:
    conn = psycopg2.connect(
        host=os.getenv('POSTGRES_HOST', 'db'),
        port=os.getenv('POSTGRES_PORT', '5432'),
        database=os.getenv('POSTGRES_DB', 'hids'),
        user=os.getenv('POSTGRES_USER', 'hids'),
        password=os.getenv('POSTGRES_PASSWORD', 'hidspass')
    )
    conn.autocommit = True
    cur = conn.cursor()
    
    # Check if schema exists
    cur.execute("SELECT COUNT(*) FROM information_schema.tables WHERE table_name='suricata_alerts';")
    if cur.fetchone()[0] == 0:
        print('📦 Importing HIDS schema...')
        with open('/app/schema.sql', 'r') as f:
            cur.execute(f.read())
        print('✅ Schema imported successfully!')
    else:
        print('ℹ️  Schema already exists')
    
    cur.close()
    conn.close()
    print('✅ Database schema initialized!')
except Exception as e:
    print(f'❌ Schema initialization failed: {e}')
    print('⚠️  Continuing anyway - schema may need manual setup')
END

echo "🎉 HIDS Engine initialization complete!"
echo "🔍 Starting HIDS engine monitoring..."

exec "$@"
