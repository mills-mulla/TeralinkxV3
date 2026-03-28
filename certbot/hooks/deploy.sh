#!/bin/sh
# Certbot deploy hook - runs after successful cert renewal
# Triggers: nginx reload + MikroTik cert push via Celery

echo "[certbot-deploy] Certificate renewed for $RENEWED_DOMAINS"

# 1. Reload nginx to pick up new cert
docker exec teralinkx_nginx nginx -s reload
echo "[certbot-deploy] nginx reloaded"

# 2. Trigger MikroTik cert push via Celery
docker exec teralinkx_celery celery -A teralinkx call finance.tasks.push_certificate_to_mikrotik
echo "[certbot-deploy] MikroTik cert push task queued"
