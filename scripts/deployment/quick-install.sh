#!/bin/bash

# TeralinkX V3 - Quick Install Script
# Minimal configuration for rapid deployment
# Author: TeralinkX Team

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}"
cat << "EOF"
╔═══════════════════════════════════════╗
║        TeralinkX V3 Quick Install     ║
║         Minimal Configuration        ║
╚═══════════════════════════════════════╝
EOF
echo -e "${NC}"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo -e "${GREEN}🚀 Starting quick installation...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Installing Docker...${NC}"
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
fi

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${YELLOW}Installing Docker Compose...${NC}"
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

cd "$PROJECT_ROOT"

# Quick environment setup
echo -e "${GREEN}⚙️  Setting up environment...${NC}"

# Generate secure secrets
DB_PASSWORD=$(openssl rand -base64 16)
RADIUS_DB_PASSWORD=$(openssl rand -base64 16)
HIDS_DB_PASSWORD=$(openssl rand -base64 16)
ADMIN_PASSWORD=$(openssl rand -base64 12)
SECRET_KEY=$(openssl rand -base64 32)
JWT_SECRET=$(openssl rand -base64 32)
RADIUS_SECRET=$(openssl rand -base64 16)

# Ask about HIDS
read -p "Enable HIDS (Host Intrusion Detection)? (y/n) [n]: " ENABLE_HIDS
ENABLE_HIDS=${ENABLE_HIDS:-n}

# Create main .env
cat > .env << EOF
DOMAIN=localhost
POSTGRES_DB=teralinkx
POSTGRES_USER=teralinkx
POSTGRES_PASSWORD=$DB_PASSWORD
RADIUS_POSTGRES_DB=radius_db
RADIUS_POSTGRES_USER=radius_user
RADIUS_POSTGRES_PASSWORD=$RADIUS_DB_PASSWORD
HIDS_POSTGRES_DB=hids
HIDS_POSTGRES_USER=hids
HIDS_POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
SECRET_KEY=$SECRET_KEY
DEBUG=False
ENABLE_HIDS=$ENABLE_HIDS
EOF

# Create backend .env
cat > teralinkx/.env << EOF
SECRET_KEY=$SECRET_KEY
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,cli.localhost,srv.localhost
DATABASE_URL=postgresql://teralinkx:$DB_PASSWORD@db:5432/teralinkx
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
JWT_SECRET_KEY=$JWT_SECRET
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://cli.localhost
EOF

# Create RADIUS .env
cat > radius_api/.env << EOF
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://radius_user:$RADIUS_DB_PASSWORD@db:5432/radius_db
DB_HOST=db
DB_PORT=5432
RADIUS_POSTGRES_DB=radius_db
RADIUS_POSTGRES_USER=radius_user
RADIUS_POSTGRES_PASSWORD=$RADIUS_DB_PASSWORD
RADIUS_SECRET=$RADIUS_SECRET
RADIUS_API_PORT=8001
EOF

# Create HIDS environment files if enabled
if [[ $ENABLE_HIDS == "y" ]]; then
    echo -e "${GREEN}🛡️  Configuring HIDS services...${NC}"
    
    cat > hids/dashboard/.env << EOF
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=hids
POSTGRES_USER=hids
POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
DASHBOARD_PORT=5002
EOF

    cat > hids/engine/.env << EOF
REDIS_HOST=redis
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=hids
POSTGRES_USER=hids
POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
ML_SERVICE_URL=http://hids_ml_service:5001
ENGINE_PORT=5003
EOF

    cat > hids/ml_service/.env << EOF
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=hids
POSTGRES_USER=hids
POSTGRES_PASSWORD=$HIDS_DB_PASSWORD
MODEL_PATH=/app/models/anomaly_detector.pkl
SCALER_PATH=/app/models/scaler.pkl
ML_SERVICE_PORT=5001
EOF
fi

# Create frontend .env
cat > TeralinkxFR/.env.production << EOF
VITE_API_BASE_URL=http://localhost:8009
VITE_FRONTEND_URL=http://localhost:3000
VITE_APP_NAME=TeralinkX
NODE_ENV=production
EOF

echo -e "${GREEN}🏗️  Building and starting services...${NC}"

# Start core services
docker-compose up -d db redis

# Wait for database
echo -e "${YELLOW}⏳ Waiting for database...${NC}"
sleep 10

# Run migrations
docker-compose run --rm web python manage.py migrate

# Create superuser
echo -e "${GREEN}👤 Creating admin user...${NC}"
docker-compose run --rm web python manage.py shell << EOF
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@localhost', '$ADMIN_PASSWORD')
    print('Admin user created')
EOF

# Collect static files
docker-compose run --rm web python manage.py collectstatic --noinput

# Start all services (excluding HIDS for quick setup unless enabled)
if [[ $ENABLE_HIDS == "y" ]]; then
    echo -e "${GREEN}🛡️  Starting services with HIDS...${NC}"
    docker-compose up -d web celery celery_beat nginx radius_api freeradius ml_service hids_engine hids_dashboard suricata zeek
else
    docker-compose up -d web celery celery_beat nginx radius_api freeradius
fi

# Build frontend if npm is available
if command -v npm &> /dev/null; then
    echo -e "${GREEN}🎨 Building frontend...${NC}"
    cd TeralinkxFR
    npm ci --production=false 2>/dev/null || npm install
    npm run build:production 2>/dev/null || npm run build
    cd ..
fi

echo -e "${GREEN}✅ Quick installation completed!${NC}"
echo
echo -e "${BLUE}=== ACCESS INFORMATION ===${NC}"
echo -e "Frontend: http://localhost (via nginx)"
echo -e "Backend API: http://localhost:8000"
echo -e "Admin Panel: http://localhost:8000/admin"
echo -e "Admin Login: admin / $ADMIN_PASSWORD"
if [[ $ENABLE_HIDS == "y" ]]; then
    echo -e "HIDS Dashboard: http://localhost:5002"
    echo -e "ML Service: http://localhost:5001"
fi
echo
echo -e "${YELLOW}🔐 IMPORTANT: Save these credentials!${NC}"
cat > "$PROJECT_ROOT/credentials.txt" << EOF
TeralinkX V3 Quick Install Credentials
Generated: $(date)

=== ADMIN ACCESS ===
Username: admin
Password: $ADMIN_PASSWORD
Email: admin@localhost

=== DATABASE CREDENTIALS ===
Main Database:
  Name: teralinkx
  User: teralinkx
  Password: $DB_PASSWORD

RADIUS Database:
  Name: radius_db
  User: radius_user
  Password: $RADIUS_DB_PASSWORD
EOF

if [[ $ENABLE_HIDS == "y" ]]; then
    cat >> "$PROJECT_ROOT/credentials.txt" << EOF

HIDS Database:
  Name: hids
  User: hids
  Password: $HIDS_DB_PASSWORD
EOF
fi

cat >> "$PROJECT_ROOT/credentials.txt" << EOF

=== SECURITY KEYS ===
Secret Key: $SECRET_KEY
JWT Secret: $JWT_SECRET
RADIUS Secret: $RADIUS_SECRET

=== IMPORTANT ===
- Change admin password after first login
- Keep this file secure
- Delete this file after saving credentials elsewhere
EOF

echo -e "${GREEN}💾 Credentials saved to: credentials.txt${NC}"
echo
echo -e "${YELLOW}📝 To access with custom domain, run the full installer:${NC}"
echo -e "./scripts/deployment/install.sh"
echo
echo -e "${GREEN}🎉 TeralinkX is ready to use!${NC}"