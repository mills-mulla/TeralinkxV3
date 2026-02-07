#!/bin/sh
# Install Python PostgreSQL driver
apk add --no-cache python3 py3-pip py3-psycopg2

# Enable SQL module
ln -sf /etc/freeradius/mods-available/sql /etc/freeradius/mods-enabled/sql

# Enable Python voucher module
ln -sf /etc/freeradius/mods-available/python_voucher /etc/freeradius/mods-enabled/python_voucher

# Start FreeRADIUS in foreground
exec freeradius -f -X
