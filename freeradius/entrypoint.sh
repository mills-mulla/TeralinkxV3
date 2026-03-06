#!/bin/sh
# Install Python PostgreSQL driver
apk add --no-cache python3 py3-pip py3-psycopg2 postgresql-client

# Wait for postgres
echo "Waiting for PostgreSQL..."
until PGPASSWORD=radiuspass psql -h postgres -U radius -d radius -c '\q' 2>/dev/null; do
  sleep 1
done

# Check if schema exists, if not import it
TABLE_COUNT=$(PGPASSWORD=radiuspass psql -h postgres -U radius -d radius -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_name='radcheck';")
if [ "$TABLE_COUNT" -eq "0" ]; then
  echo "Importing RADIUS schema..."
  PGPASSWORD=radiuspass psql -h postgres -U radius -d radius < /etc/freeradius/schema.sql
  echo "Schema imported successfully"
else
  echo "Schema already exists, skipping import"
fi

# Enable SQL module
ln -sf /etc/freeradius/mods-available/sql /etc/freeradius/mods-enabled/sql

# Start FreeRADIUS in foreground
exec freeradius -f -X
