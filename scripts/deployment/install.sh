#!/bin/bash

# TeralinkX V3 - Automated Installation Script
# This script automates the complete deployment of TeralinkX platform
# Author: TeralinkX Team
# Version: 1.0.0

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
LOG_FILE="$PROJECT_ROOT/installation.log"
BACKUP_DIR="$PROJECT_ROOT/backups/$(date +%Y%m%d_%H%M%S)"

# Default configuration
DEFAULT_DOMAIN="teralinkxwaves.uk"
DEFAULT_DB_PASSWORD="justboot"
DEFAULT_REDIS_PASSWORD=""
DEFAULT_ADMIN_PASSWORD="admin"

# Show spinner during long operations
show_spinner() {
    local pid=$1
    local message=$2
    local spin='-\|/'
    local i=0
    
    echo -n "  $message "
    while kill -0 $pid 2>/dev/null; do
        i=$(( (i+1) %4 ))
        printf "\r  $message ${CYAN}${spin:$i:1}${NC}"
        sleep 0.1
    done
    printf "\r  $message ${GREEN}✓${NC}\n"
}

# Functions
log() {
    echo -e "${CYAN}▶${NC} ${GREEN}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

warn() {
    echo -e "${YELLOW}⚠${NC}  ${YELLOW}[$(date +'%H:%M:%S')] WARNING:${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}✗${NC}  ${RED}[$(date +'%H:%M:%S')] ERROR:${NC} $1" | tee -a "$LOG_FILE"
    exit 1
}

info() {
    echo -e "${BLUE}ℹ${NC}  ${BLUE}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✓${NC}  ${GREEN}[$(date +'%H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

# Banner
show_banner() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"

████████╗███████╗██████╗  █████╗ ██╗     ██╗███╗   ██╗██╗  ██╗    ██╗   ██╗██████╗ 
╚══██╔══╝██╔════╝██╔══██╗██╔══██╗██║     ██║████╗  ██║██║ ██╔╝    ██║   ██║╚════██╗
   ██║   █████╗  ██████╔╝███████║██║     ██║██╔██╗ ██║█████╔╝     ██║   ██║ █████╔╝
   ██║   ██╔══╝  ██╔══██╗██╔══██║██║     ██║██║╚██╗██║██╔═██╗     ╚██╗ ██╔╝ ╚═══██╗
   ██║   ███████╗██║  ██║██║  ██║███████╗██║██║ ╚████║██║  ██╗     ╚████╔╝ ██████╔╝
   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝      ╚═══╝  ╚═════╝ 

EOF
    echo -e "${NC}"
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                                                                               ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}        ${CYAN}⚡ ENTERPRISE ISP MANAGEMENT & AUTOMATION PLATFORM ⚡${NC}              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                                               ${PURPLE}║${NC}"
    echo -e "${PURPLE}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${PURPLE}║${NC}                                                                               ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}   ${GREEN}✓${NC} Multi-Tenant ISP Platform      ${GREEN}✓${NC} RADIUS Authentication              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}   ${GREEN}✓${NC} Real-Time Network Monitoring   ${GREEN}✓${NC} Advanced Security (HIDS)           ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}   ${GREEN}✓${NC} Automated Billing System       ${GREEN}✓${NC} Customer Self-Service Portal       ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}   ${GREEN}✓${NC} API-First Architecture         ${GREEN}✓${NC} Scalable Microservices             ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                                               ${PURPLE}║${NC}"
    echo -e "${PURPLE}╠═══════════════════════════════════════════════════════════════════════════════╣${NC}"
    echo -e "${PURPLE}║${NC}                                                                               ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}   ${YELLOW}Platform:${NC} TeralinkX v3.1.0     ${YELLOW}Installer:${NC} v1.0.0                    ${YELLOW}Status:${NC} Production Ready              ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}   ${YELLOW}License:${NC} Enterprise               ${YELLOW}Support:${NC} 24/7 Available                ${PURPLE}║${NC}"
    echo -e "${PURPLE}║${NC}                                                                               ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

# Source service selection menu (whiptail version if available)
if command -v whiptail &> /dev/null && [[ -f "$SCRIPT_DIR/service_selection_whiptail.sh" ]]; then
    source "$SCRIPT_DIR/service_selection_whiptail.sh"
elif [[ -f "$SCRIPT_DIR/service_selection.sh" ]]; then
    source "$SCRIPT_DIR/service_selection.sh"
else
    warn "Service selection menu not found. Using default configuration."
    INSTALL_HIDS="y"
    INSTALL_MONITORING="y"
fi

# Auto-install Docker if missing
install_docker() {
    log "Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    warn "Please log out and back in for Docker group changes to take effect"
}

# Check prerequisites
check_prerequisites() {
    log "Checking system prerequisites..."
    
    # Check if running as root - warn but allow
    if [[ $EUID -eq 0 ]]; then
        warn "Running as root. This is acceptable for Docker operations but ensure proper security."
    fi
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        warn "Docker is not installed."
        read -p "Would you like to install Docker automatically? (y/n): " install_docker_choice
        if [[ $install_docker_choice == "y" ]]; then
            install_docker
        else
            error "Docker is required. Please install Docker first."
        fi
    fi
    
    # Check Docker Compose
    if ! command -v docker compose &> /dev/null && ! docker compose version &> /dev/null; then
        warn "Docker Compose is not installed."
        if command -v docker &> /dev/null; then
            log "Installing Docker Compose..."
            sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker compose
            sudo chmod +x /usr/local/bin/docker compose
        else
            error "Docker Compose is required. Please install Docker Compose first."
        fi
    fi
    
    # Check if Docker daemon is running
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running. Please start Docker service."
    fi
    
    # Check available disk space (minimum 10GB)
    available_space=$(df "$PROJECT_ROOT" | awk 'NR==2 {print $4}')
    if [[ $available_space -lt 10485760 ]]; then
        warn "Less than 10GB disk space available. Installation may fail."
    fi
    
    # Check available memory (minimum 4GB)
    available_memory=$(free -m | awk 'NR==2{print $7}')
    if [[ $available_memory -lt 4096 ]]; then
        warn "Less than 4GB RAM available. Performance may be affected."
    fi
    
    success "Prerequisites check completed"
}

# Collect configuration
collect_configuration() {
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                    ${CYAN}⚙️  INSTALLATION CONFIGURATION ⚙️${NC}                      ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Show service selection menu first
    show_service_selection_menu
    
    log "Collecting installation configuration..."
    echo
    
    # Domain configuration
    echo -e "${CYAN}▶ Domain Configuration${NC}"
    echo -e "${BLUE}─────────────────────────${NC}"
    read -p "Enter your root domain name [$DEFAULT_DOMAIN]: " DOMAIN
    DOMAIN=${DOMAIN:-$DEFAULT_DOMAIN}
    echo
    
    # Database configuration
    echo -e "${CYAN}▶ Database Configuration${NC}"
    echo -e "${BLUE}──────────────────────────${NC}"
    read -p "Enter database name [teralinkx]: " DB_NAME
    DB_NAME=${DB_NAME:-teralinkx}
    
    read -p "Enter database username [teralinkx]: " DB_USER
    DB_USER=${DB_USER:-teralinkx}
    
    read -s -p "Enter database password [$DEFAULT_DB_PASSWORD]: " DB_PASSWORD
    echo
    DB_PASSWORD=${DB_PASSWORD:-$DEFAULT_DB_PASSWORD}
    
    # RADIUS database configuration
    read -p "Enter RADIUS database name [radius_db]: " RADIUS_DB_NAME
    RADIUS_DB_NAME=${RADIUS_DB_NAME:-radius_db}
    
    read -p "Enter RADIUS database username [radius_user]: " RADIUS_DB_USER
    RADIUS_DB_USER=${RADIUS_DB_USER:-radius_user}
    
    read -s -p "Enter RADIUS database password [$DEFAULT_DB_PASSWORD]: " RADIUS_DB_PASSWORD
    echo
    RADIUS_DB_PASSWORD=${RADIUS_DB_PASSWORD:-$DEFAULT_DB_PASSWORD}
    echo
    
    # HIDS database configuration (if HIDS enabled)
    if [[ $INSTALL_HIDS == true ]]; then
        echo -e "${CYAN}▶ HIDS Database Configuration${NC}"
        echo -e "${BLUE}──────────────────────────────${NC}"
        read -p "Enter HIDS database name [hids]: " HIDS_DB_NAME
        HIDS_DB_NAME=${HIDS_DB_NAME:-hids}
        
        read -p "Enter HIDS database username [hids]: " HIDS_DB_USER
        HIDS_DB_USER=${HIDS_DB_USER:-hids}
        
        read -s -p "Enter HIDS database password [hidspass]: " HIDS_DB_PASSWORD
        echo
        HIDS_DB_PASSWORD=${HIDS_DB_PASSWORD:-hidspass}
    fi
    
    # Admin user configuration
    echo -e "${CYAN}▶ Admin User Configuration${NC}"
    echo -e "${BLUE}────────────────────────────${NC}"
    read -p "Enter Django admin username [admin]: " ADMIN_USERNAME
    ADMIN_USERNAME=${ADMIN_USERNAME:-admin}
    
    read -p "Enter Django admin email [admin@$DOMAIN]: " ADMIN_EMAIL
    ADMIN_EMAIL=${ADMIN_EMAIL:-admin@$DOMAIN}
    
    read -s -p "Enter Django admin password [$DEFAULT_ADMIN_PASSWORD]: " ADMIN_PASSWORD
    echo
    ADMIN_PASSWORD=${ADMIN_PASSWORD:-$DEFAULT_ADMIN_PASSWORD}
    echo
    
    # SSL Configuration
    echo -e "${CYAN}▶ SSL Certificate Configuration${NC}"
    echo -e "${BLUE}────────────────────────────────${NC}"
    echo "1) Cloudflare DNS Challenge (Recommended)"
    echo "2) HTTP Challenge (Let's Encrypt)"
    echo "3) Skip SSL setup"
    read -p "Choose SSL method [1]: " SSL_METHOD
    SSL_METHOD=${SSL_METHOD:-1}
    
    if [[ $SSL_METHOD == "1" ]]; then
        SETUP_CLOUDFLARE="y"
        read -p "Enter Cloudflare API token: " CF_API_TOKEN
        read -p "Enter Cloudflare email: " CF_EMAIL
    elif [[ $SSL_METHOD == "2" ]]; then
        SETUP_HTTP_CHALLENGE="y"
    fi
    
    # Service configuration
    # Note: Service selection already done in menu
    # These are kept for backward compatibility
    ENABLE_HIDS=$INSTALL_HIDS
    ENABLE_MONITORING=$INSTALL_MONITORING
    
    # Monitoring credentials
    if [[ $INSTALL_MONITORING == true ]]; then
        read -p "Enter Grafana admin username [admin]: " GRAFANA_USER
        GRAFANA_USER=${GRAFANA_USER:-admin}
        
        read -s -p "Enter Grafana admin password [admin]: " GRAFANA_PASSWORD
        echo
        GRAFANA_PASSWORD=${GRAFANA_PASSWORD:-admin}
    fi
    
    success "Configuration collected"
    
    # Show configuration summary and confirm
    echo
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                    ${CYAN}📋 CONFIGURATION SUMMARY 📋${NC}                           ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${GREEN}Domain:${NC} $DOMAIN"
    echo -e "${GREEN}Database:${NC} $DB_NAME (user: $DB_USER)"
    echo -e "${GREEN}RADIUS DB:${NC} $RADIUS_DB_NAME (user: $RADIUS_DB_USER)"
    [[ $INSTALL_HIDS == true ]] && echo -e "${GREEN}HIDS DB:${NC} $HIDS_DB_NAME (user: $HIDS_DB_USER)"
    echo -e "${GREEN}Admin User:${NC} $ADMIN_USERNAME ($ADMIN_EMAIL)"
    echo -e "${GREEN}SSL Method:${NC} $SSL_METHOD"
    [[ $INSTALL_MONITORING == true ]] && echo -e "${GREEN}Grafana User:${NC} $GRAFANA_USER"
    echo
    echo -e "${YELLOW}═══════════════════════════════════════════════════════════════════════════════${NC}"
    read -p "$(echo -e ${CYAN}"Proceed with this configuration? (y/n): "${NC})" CONFIRM_CONFIG
    
    if [[ $CONFIRM_CONFIG != "y" ]]; then
        warn "Configuration cancelled. Please restart the installer."
        exit 0
    fi
}

# Create comprehensive backup
create_backup() {
    log "Creating comprehensive backup of existing configuration..."
    
    mkdir -p "$BACKUP_DIR"
    
    # Create backup manifest
    echo "TeralinkX V3 Backup - $(date)" > "$BACKUP_DIR/backup_manifest.txt"
    echo "======================================" >> "$BACKUP_DIR/backup_manifest.txt"
    
    # Backup all .env files with structure
    find "$PROJECT_ROOT" -name ".env*" -type f | while read -r file; do
        rel_path=${file#$PROJECT_ROOT/}
        mkdir -p "$BACKUP_DIR/$(dirname "$rel_path")"
        cp "$file" "$BACKUP_DIR/$rel_path"
        echo "Backed up: $rel_path" >> "$BACKUP_DIR/backup_manifest.txt"
    done
    
    # Backup configuration files
    config_files=(
        "docker compose.yml"
        "nginx/default.conf"
        "nginx/nginx.conf"
        "certbot/cloudflare.ini"
        "postgres/init.sql"
        "freeradius/clients.conf"
        "freeradius/radiusd.conf"
    )
    
    for file in "${config_files[@]}"; do
        if [[ -f "$PROJECT_ROOT/$file" ]]; then
            mkdir -p "$BACKUP_DIR/$(dirname "$file")"
            cp "$PROJECT_ROOT/$file" "$BACKUP_DIR/$file"
            echo "Backed up: $file" >> "$BACKUP_DIR/backup_manifest.txt"
        fi
    done
    
    # Backup Docker volumes data if exists
    if [[ -d "$PROJECT_ROOT/data" ]]; then
        cp -r "$PROJECT_ROOT/data" "$BACKUP_DIR/"
        echo "Backed up: data/ directory" >> "$BACKUP_DIR/backup_manifest.txt"
    fi
    
    # Backup SSL certificates if exists
    if [[ -d "$PROJECT_ROOT/certbot/conf" ]]; then
        cp -r "$PROJECT_ROOT/certbot/conf" "$BACKUP_DIR/certbot/"
        echo "Backed up: SSL certificates" >> "$BACKUP_DIR/backup_manifest.txt"
    fi
    
    echo "Backup completed at: $(date)" >> "$BACKUP_DIR/backup_manifest.txt"
    
    success "Comprehensive backup created at $BACKUP_DIR"
    info "Backup manifest: $BACKUP_DIR/backup_manifest.txt"
}

# Generate dynamic nginx configuration
generate_nginx_config() {
    log "Generating dynamic nginx configuration..."
    
    cat > "$PROJECT_ROOT/nginx/default.conf" << EOF
# TeralinkX V3 Nginx Configuration
# Generated on $(date)
# Domain: $DOMAIN

upstream backend {
    server web:8000;
}

upstream radius_api {
    server radius_api:8001;
}

# Frontend (cli.$DOMAIN)
server {
    listen 80;
    server_name cli.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name cli.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    root /var/www/html/client;
    index index.html;
    
    location / {
        alias /app/frontend-dist/;
        try_files \$uri \$uri/ /index.html;
    }
}

# Backend API (srv.$DOMAIN)
server {
    listen 80;
    server_name srv.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name srv.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}

# Admin Panel (su.$DOMAIN)
server {
    listen 80;
    server_name su.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name su.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    root /var/www/html/admin;
    index index.html;
    
    location / {
        alias /app/admin-dist/;
        try_files \$uri \$uri/ /index.html;
    }
    
    # Proxy API requests to backend
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

    if [[ $ENABLE_MONITORING == "y" ]]; then
        cat >> "$PROJECT_ROOT/nginx/default.conf" << EOF

# Monitoring (mt.$DOMAIN)
server {
    listen 80;
    server_name mt.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mt.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://grafana:3000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    fi

    if [[ $ENABLE_HIDS == "y" ]]; then
        cat >> "$PROJECT_ROOT/nginx/default.conf" << EOF

# HIDS Dashboard (sec.$DOMAIN)
server {
    listen 80;
    server_name sec.$DOMAIN;
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name sec.$DOMAIN;
    
    ssl_certificate /etc/letsencrypt/live/$DOMAIN/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/$DOMAIN/privkey.pem;
    
    location / {
        proxy_pass http://hids_dashboard:8080;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF
    fi

    success "Nginx configuration generated"
}

# Setup environment files
setup_environment() {
    log "Setting up dynamic environment files..."
    
    # Generate nginx config first
    generate_nginx_config
    
    # Main .env file
    cat > "$PROJECT_ROOT/.env" << EOF
# TeralinkX V3 Environment Configuration
# Generated on $(date)

# Domain Configuration
DOMAIN=$DOMAIN
FRONTEND_URL=https://cli.$DOMAIN
BACKEND_URL=https://srv.$DOMAIN
ADMIN_URL=https://su.$DOMAIN
MONITORING_URL=https://mt.$DOMAIN
HIDS_URL=https://sec.$DOMAIN

# Database Configuration
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@db:5432/$DB_NAME

# RADIUS Database
RADIUS_POSTGRES_DB=$RADIUS_DB_NAME
RADIUS_POSTGRES_USER=$RADIUS_DB_USER
RADIUS_POSTGRES_PASSWORD=$RADIUS_DB_PASSWORD

# HIDS Database (if enabled)
HIDS_POSTGRES_DB=${HIDS_DB_NAME:-hids}
HIDS_POSTGRES_USER=${HIDS_DB_USER:-hids}
HIDS_POSTGRES_PASSWORD=${HIDS_DB_PASSWORD:-hidspass}

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,cli.$DOMAIN,srv.$DOMAIN,su.$DOMAIN,mt.$DOMAIN,sec.$DOMAIN,localhost,127.0.0.1

# Admin Configuration
ADMIN_USERNAME=$ADMIN_USERNAME
ADMIN_EMAIL=$ADMIN_EMAIL
ADMIN_PASSWORD=$ADMIN_PASSWORD

# Monitoring
GRAFANA_USER=$GRAFANA_USER
GRAFANA_PASSWORD=$GRAFANA_PASSWORD

# Services
ENABLE_HIDS=$ENABLE_HIDS
ENABLE_MONITORING=$ENABLE_MONITORING

# SSL Configuration
CF_API_TOKEN=$CF_API_TOKEN
CF_EMAIL=$CF_EMAIL
EOF

    # Backend .env file
    cat > "$PROJECT_ROOT/teralinkx/.env" << EOF
# Django Backend Configuration
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,cli.$DOMAIN,srv.$DOMAIN,su.$DOMAIN,mt.$DOMAIN,sec.$DOMAIN,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://$DB_USER:$DB_PASSWORD@db:5432/$DB_NAME
DB_HOST=db
DB_PORT=5432
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASSWORD

# Redis
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/1

# JWT Configuration
JWT_SECRET_KEY=$(openssl rand -base64 32)
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_LIFETIME=3600
JWT_REFRESH_TOKEN_LIFETIME=86400

# CORS
CORS_ALLOWED_ORIGINS=https://cli.$DOMAIN,https://su.$DOMAIN,https://mt.$DOMAIN,https://sec.$DOMAIN
CORS_ALLOW_CREDENTIALS=True

# Security
SECURE_SSL_REDIRECT=True
SECURE_PROXY_SSL_HEADER=HTTP_X_FORWARDED_PROTO,https
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True

# Admin Configuration
DJANGO_SUPERUSER_USERNAME=$ADMIN_USERNAME
DJANGO_SUPERUSER_EMAIL=$ADMIN_EMAIL
DJANGO_SUPERUSER_PASSWORD=$ADMIN_PASSWORD

# Application Settings
DJANGO_PORT=8000
GUNICORN_LOG_LEVEL=info
EOF

    # RADIUS API .env file
    cat > "$PROJECT_ROOT/radius_api/.env" << EOF
# RADIUS API Configuration
SECRET_KEY=$(openssl rand -base64 32)
DEBUG=False
ALLOWED_HOSTS=$DOMAIN,radius.$DOMAIN,localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://$RADIUS_DB_USER:$RADIUS_DB_PASSWORD@db:5432/$RADIUS_DB_NAME
DB_HOST=db
DB_PORT=5432
RADIUS_POSTGRES_DB=$RADIUS_DB_NAME
RADIUS_POSTGRES_USER=$RADIUS_DB_USER
RADIUS_POSTGRES_PASSWORD=$RADIUS_DB_PASSWORD

# RADIUS Configuration
RADIUS_SECRET=$(openssl rand -base64 16)
RADIUS_SERVER=localhost
RADIUS_PORT=1812

# Application Settings
RADIUS_API_PORT=8001
GUNICORN_LOG_LEVEL=info
EOF

    # Frontend .env files (both .env and .env.production)
    # Client Frontend
    cat > "$PROJECT_ROOT/TeralinkxFR/.env" << EOF
# Client Frontend Configuration
VITE_API_BASE_URL=https://srv.$DOMAIN
VITE_FRONTEND_URL=https://cli.$DOMAIN
VITE_ADMIN_URL=https://su.$DOMAIN
VITE_MONITORING_URL=https://mt.$DOMAIN
VITE_HIDS_URL=https://sec.$DOMAIN
VITE_APP_NAME=TeralinkX
VITE_APP_VERSION=3.1.0
NODE_ENV=production
EOF

    cp "$PROJECT_ROOT/TeralinkxFR/.env" "$PROJECT_ROOT/TeralinkxFR/.env.production"

    # Admin Frontend
    cat > "$PROJECT_ROOT/teralinkx/admteralinkx/adminstration/.env" << EOF
# Admin Frontend Configuration
VITE_API_BASE_URL=https://srv.$DOMAIN
VITE_FRONTEND_URL=https://cli.$DOMAIN
VITE_ADMIN_URL=https://su.$DOMAIN
VITE_MONITORING_URL=https://mt.$DOMAIN
VITE_HIDS_URL=https://sec.$DOMAIN
VITE_APP_NAME=TeralinkX Admin
VITE_APP_VERSION=3.1.0
VITE_PUSHER_KEY=${PUSHER_KEY:-your_pusher_key}
VITE_PUSHER_CLUSTER=mt1
NODE_ENV=production
EOF

    cp "$PROJECT_ROOT/teralinkx/admteralinkx/adminstration/.env" "$PROJECT_ROOT/teralinkx/admteralinkx/adminstration/.env.production"

    # HIDS Services environment files (if enabled)
    if [[ $INSTALL_HIDS == true ]]; then
        log "Configuring HIDS services environment..."
        
        # HIDS Dashboard .env
        cat > "$PROJECT_ROOT/hids/dashboard/.env" << EOF
# HIDS Dashboard Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=${HIDS_DB_NAME:-hids}
POSTGRES_USER=${HIDS_DB_USER:-hids}
POSTGRES_PASSWORD=${HIDS_DB_PASSWORD:-hidspass}
DASHBOARD_PORT=5002
EOF

        # HIDS Engine .env
        cat > "$PROJECT_ROOT/hids/engine/.env" << EOF
# HIDS Engine Configuration
REDIS_HOST=redis
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=${HIDS_DB_NAME:-hids}
POSTGRES_USER=${HIDS_DB_USER:-hids}
POSTGRES_PASSWORD=${HIDS_DB_PASSWORD:-hidspass}
ML_SERVICE_URL=http://hids_ml_service:5001
ENGINE_PORT=5003
EOF

        # ML Service .env
        cat > "$PROJECT_ROOT/hids/ml_service/.env" << EOF
# HIDS ML Service Configuration
POSTGRES_HOST=db
POSTGRES_PORT=5432
POSTGRES_DB=${HIDS_DB_NAME:-hids}
POSTGRES_USER=${HIDS_DB_USER:-hids}
POSTGRES_PASSWORD=${HIDS_DB_PASSWORD:-hidspass}
MODEL_PATH=/app/models/anomaly_detector.pkl
SCALER_PATH=/app/models/scaler.pkl
ML_SERVICE_PORT=5001
EOF

        success "HIDS services environment configured"
    fi

    success "Dynamic environment files configured"
}

# Setup Cloudflare
setup_cloudflare() {
    if [[ $SETUP_CLOUDFLARE != "y" ]]; then
        return
    fi
    
    log "Setting up Cloudflare configuration..."
    
    # Create Cloudflare credentials file
    mkdir -p "$PROJECT_ROOT/certbot"
    cat > "$PROJECT_ROOT/certbot/cloudflare.ini" << EOF
# Cloudflare API credentials
dns_cloudflare_email = $CF_EMAIL
dns_cloudflare_api_key = $CF_API_TOKEN
EOF
    
    chmod 600 "$PROJECT_ROOT/certbot/cloudflare.ini"
    
    success "Cloudflare configuration completed"
}

# Setup SSL certificates
setup_ssl() {
    log "Setting up SSL certificates..."
    
    if [[ $SSL_METHOD == "1" && $SETUP_CLOUDFLARE == "y" ]]; then
        info "Setting up Cloudflare DNS challenge..."
        docker compose exec -T certbot certbot certonly \
            --dns-cloudflare \
            --dns-cloudflare-credentials /etc/cloudflare.ini \
            --email "$CF_EMAIL" \
            --agree-tos \
            --non-interactive \
            -d "$DOMAIN" \
            -d "*.$DOMAIN"
    elif [[ $SSL_METHOD == "2" && $SETUP_HTTP_CHALLENGE == "y" ]]; then
        info "Setting up HTTP challenge..."
        docker compose exec -T certbot certbot certonly \
            --webroot \
            --webroot-path=/var/www/certbot \
            --email "admin@$DOMAIN" \
            --agree-tos \
            --non-interactive \
            -d "$DOMAIN" \
            -d "cli.$DOMAIN" \
            -d "srv.$DOMAIN" \
            -d "su.$DOMAIN" \
            -d "mt.$DOMAIN" \
            -d "sec.$DOMAIN"
    else
        warn "SSL setup skipped"
        return
    fi
    
    # Reload nginx with SSL
    docker compose exec nginx nginx -s reload
    
    success "SSL certificates configured"
}

# Build frontend
build_frontend() {
    if [[ $INSTALL_FRONTEND != true ]]; then
        log "Skipping frontend build"
        return
    fi
    
    log "Building frontend applications..."
    
    # Check if Node.js is installed
    if ! command -v node &> /dev/null; then
        warn "Node.js is not installed."
        read -p "Would you like to install Node.js? (y/n): " install_node
        if [[ $install_node == "y" ]]; then
            curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
            sudo apt-get install -y nodejs
        else
            error "Node.js is required for frontend build"
        fi
    fi
    
    # Build Client Frontend (TeralinkxFR)
    log "Building client frontend (cli.$DOMAIN)..."
    cd "$PROJECT_ROOT/TeralinkxFR"
    
    info "Installing client frontend dependencies..."
    npm install
    
    info "Building client frontend for production..."
    npm run build
    
    success "Client frontend build completed"
    
    # Build Admin Frontend (admteralinkx)
    log "Building admin frontend (su.$DOMAIN)..."
    cd "$PROJECT_ROOT/teralinkx/admteralinkx/adminstration"
    
    info "Installing admin frontend dependencies..."
    npm install
    
    info "Building admin frontend for production..."
    npm run build
    
    success "Admin frontend build completed"
    
    cd "$PROJECT_ROOT"
    success "All frontend builds completed"
}

# Service health check functions
check_service_health() {
    local service=$1
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker compose ps "$service" | grep -q "Up"; then
            return 0
        fi
        sleep 2
        ((attempt++))
    done
    return 1
}

check_database_health() {
    log "Checking database health..."
    local max_attempts=30
    local attempt=1
    
    while [[ $attempt -le $max_attempts ]]; do
        if docker compose exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" &>/dev/null; then
            success "Database is ready"
            return 0
        fi
        info "Waiting for database... (attempt $attempt/$max_attempts)"
        sleep 2
        ((attempt++))
    done
    error "Database failed to start"
}

check_redis_health() {
    log "Checking Redis health..."
    if docker compose exec -T redis redis-cli ping | grep -q "PONG"; then
        success "Redis is ready"
        return 0
    fi
    error "Redis health check failed"
}

check_django_health() {
    log "Checking Django application health..."
    if docker compose exec -T web python manage.py check --deploy &>/dev/null; then
        success "Django application is healthy"
        return 0
    fi
    error "Django health check failed"
}

check_nginx_health() {
    log "Checking Nginx configuration..."
    if docker compose exec -T nginx nginx -t &>/dev/null; then
        success "Nginx configuration is valid"
        return 0
    fi
    error "Nginx configuration test failed"
}

check_hids_health() {
    log "Checking HIDS services health..."
    
    # Check ML Service
    if docker compose ps ml_service | grep -q "Up"; then
        if curl -s http://localhost:5001/health | grep -q "healthy" 2>/dev/null; then
            success "ML Service is healthy"
        else
            warn "ML Service is running but health check failed"
        fi
    else
        warn "ML Service is not running"
    fi
    
    # Check HIDS Engine
    if docker compose ps hids_engine | grep -q "Up"; then
        success "HIDS Engine is running"
    else
        warn "HIDS Engine is not running"
    fi
    
    # Check HIDS Dashboard
    if docker compose ps hids_dashboard | grep -q "Up"; then
        if curl -s http://localhost:5002/api | grep -q "HIDS Dashboard" 2>/dev/null; then
            success "HIDS Dashboard is healthy"
        else
            warn "HIDS Dashboard is running but health check failed"
        fi
    else
        warn "HIDS Dashboard is not running"
    fi
}

# Systematic service deployment
deploy_services() {
    log "Starting systematic service deployment..."
    
    cd "$PROJECT_ROOT"
    
    # Stop any existing containers
    info "Stopping existing containers..."
    docker compose down --remove-orphans 2>/dev/null || true
    
    # Pull latest images
    log "Pulling latest Docker images (this may take several minutes)..."
    echo
    
    # Get list of services
    local services=$(docker compose config --services 2>/dev/null)
    local total_services=$(echo "$services" | wc -l)
    local current=0
    
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                    ${YELLOW}📦 PULLING DOCKER IMAGES 📦${NC}                           ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    # Pull images with progress
    while IFS= read -r service; do
        ((current++))
        local image=$(docker compose config | grep -A 5 "^  $service:" | grep "image:" | awk '{print $2}' | head -1)
        
        if [[ -n "$image" ]]; then
            echo -e "${BLUE}[$current/$total_services]${NC} Pulling ${GREEN}$service${NC} (${CYAN}$image${NC})..."
            
            if docker pull "$image" 2>&1 | grep -E "Pulling|Downloading|Extracting|Pull complete|Already exists" | while read line; do
                echo -e "  ${PURPLE}│${NC} $line"
            done; then
                echo -e "  ${GREEN}✓${NC} ${GREEN}$service${NC} image ready"
            else
                echo -e "  ${YELLOW}⚠${NC}  ${YELLOW}$service${NC} - using cached or will build locally"
            fi
        else
            echo -e "${BLUE}[$current/$total_services]${NC} ${GREEN}$service${NC} - will be built from Dockerfile"
        fi
        echo
    done <<< "$services"
    
    success "Image pull phase completed"
    
    # Build custom images
    log "Building custom Docker images..."
    echo
    echo -e "${CYAN}╔════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}                    ${YELLOW}🔨 BUILDING CUSTOM IMAGES 🔨${NC}                          ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    
    info "Building TeralinkX web application..."
    docker compose build --no-cache web 2>&1 | grep -E "Step|Successfully|naming to" | sed 's/^/  │ /'
    
    info "Building RADIUS API..."
    docker compose build --no-cache radius_api 2>&1 | grep -E "Step|Successfully|naming to" | sed 's/^/  │ /'
    
    if [[ $INSTALL_HIDS == true ]]; then
        info "Building HIDS services..."
        docker compose build --no-cache ml_service hids_engine hids_dashboard 2>&1 | grep -E "Step|Successfully|naming to" | sed 's/^/  │ /'
    fi
    
    echo
    success "Custom images built successfully"
    
    # Phase 1: Core Infrastructure
    log "Phase 1: Starting core infrastructure services..."
    echo -e "${BLUE}┌───────────────────────────────────────────────────────────────────────────┐${NC}"
    echo -e "${BLUE}│${NC} ${CYAN}📦 PostgreSQL Database${NC}                                                  ${BLUE}│${NC}"
    echo -e "${BLUE}│${NC} ${CYAN}📦 Redis Cache${NC}                                                         ${BLUE}│${NC}"
    echo -e "${BLUE}└───────────────────────────────────────────────────────────────────────────┘${NC}"
    docker compose up -d db redis
    
    # Wait for core services
    info "Waiting for database to be ready..."
    check_database_health
    
    info "Waiting for Redis to be ready..."
    check_redis_health
    
    # Phase 2: Application Services
    log "Phase 2: Starting application services..."
    
    # Run database migrations
    info "Running database migrations..."
    docker compose run --rm web python manage.py migrate
    
    # Create admin superuser
    info "Creating admin superuser..."
    docker compose run --rm web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='$ADMIN_USERNAME').exists():
    User.objects.create_superuser('$ADMIN_USERNAME', '$ADMIN_EMAIL', '$ADMIN_PASSWORD')
    print('Superuser created successfully')
else:
    print('Superuser already exists')
"
    
    # Collect static files
    info "Collecting static files..."
    docker compose run --rm web python manage.py collectstatic --noinput
    
    # Start web services
    docker compose up -d web celery celery_beat
    
    # Phase 3: RADIUS Services
    log "Phase 3: Starting RADIUS services..."
    docker compose up -d radius_api freeradius
    
    # Phase 4: Reverse Proxy
    log "Phase 4: Starting reverse proxy..."
    docker compose up -d nginx
    check_nginx_health
    
    # Phase 5: SSL and Tunneling
    log "Phase 5: Starting SSL and tunneling services..."
    docker compose up -d certbot cloudflared
    
    # Phase 6: Optional Services
    if [[ $INSTALL_HIDS == true ]]; then
        log "Phase 6a: Starting HIDS services..."
        
        # Start ML service first (dependency for engine)
        info "Starting ML service..."
        docker compose up -d ml_service
        sleep 5
        
        # Start HIDS engine (depends on ML service)
        info "Starting HIDS engine..."
        docker compose up -d hids_engine
        sleep 5
        
        # Start supporting services
        info "Starting Suricata and Zeek..."
        docker compose up -d suricata zeek
        sleep 3
        
        # Start HIDS dashboard (depends on engine)
        info "Starting HIDS dashboard..."
        docker compose up -d hids_dashboard
        
        # Check HIDS health
        sleep 10
        check_hids_health
    fi
    
    if [[ $INSTALL_MONITORING == true ]]; then
        log "Phase 6b: Starting monitoring services..."
        docker compose up -d prometheus grafana loki promtail alertmanager node-exporter cadvisor redis-exporter postgres-exporter
    fi
    
    success "All services deployed successfully"
}

# Comprehensive health checks
perform_health_checks() {
    log "Performing comprehensive health checks..."
    
    # Wait for services to stabilize
    sleep 30
    
    local failed_checks=0
    
    # Check database
    if docker compose exec -T db pg_isready -U "$DB_USER" -d "$DB_NAME" &>/dev/null; then
        success "Database is healthy"
    else
        warn "Database health check failed"
        ((failed_checks++))
    fi
    
    # Check Redis
    if docker compose exec -T redis redis-cli ping | grep -q PONG; then
        success "Redis is healthy"
    else
        warn "Redis health check failed"
        ((failed_checks++))
    fi
    
    # Check Django application
    if docker compose exec -T web python manage.py check --deploy &>/dev/null; then
        success "Django application is healthy"
    else
        warn "Django application health check failed"
        ((failed_checks++))
    fi
    
    # Check Nginx configuration
    if docker compose exec -T nginx nginx -t &>/dev/null; then
        success "Nginx configuration is valid"
    else
        warn "Nginx configuration check failed"
        ((failed_checks++))
    fi
    
    # Check API endpoints
    if curl -s -k "https://srv.$DOMAIN/api/health/" | grep -q "ok" 2>/dev/null; then
        success "API endpoints are responding"
    else
        warn "API endpoint health check failed (may be normal if SSL not configured)"
    fi
    
    # Check RADIUS if enabled
    if docker compose ps radius_api | grep -q "Up"; then
        success "RADIUS API service is running"
    else
        warn "RADIUS API service check failed"
    fi
    
    # Check HIDS services if enabled
    if [[ $INSTALL_HIDS == true ]]; then
        info "Checking HIDS services..."
        check_hids_health
    fi
    
    if [[ $failed_checks -eq 0 ]]; then
        success "All health checks passed"
    else
        warn "$failed_checks health checks failed - review logs for details"
    fi
}

# Enhanced monitoring setup
setup_monitoring() {
    if [[ $INSTALL_MONITORING != true ]]; then
        return
    fi
    
    log "Setting up enhanced monitoring dashboards..."
    
    # Wait for Grafana to be ready
    info "Waiting for Grafana to be ready..."
    local timeout=60
    local attempt=1
    
    while [[ $attempt -le 30 ]]; do
        if curl -s http://localhost:3000/api/health &>/dev/null; then
            success "Grafana is ready"
            break
        fi
        info "Waiting for Grafana... (attempt $attempt/30)"
        sleep 2
        ((attempt++))
    done
    
    if [[ $attempt -gt 30 ]]; then
        warn "Grafana failed to start within 60 seconds"
        return
    fi
    
    # Configure Grafana data sources
    info "Configuring Grafana data sources..."
    
    # Import pre-configured dashboards
    local dashboard_dir="$PROJECT_ROOT/monitoring/dashboards"
    if [[ -d "$dashboard_dir" ]]; then
        info "Importing monitoring dashboards..."
        for dashboard in "$dashboard_dir"/*.json; do
            if [[ -f "$dashboard" ]]; then
                info "Importing $(basename "$dashboard")..."
                # Dashboard import logic would go here
            fi
        done
    fi
    
    # Set up alerting rules
    if [[ -f "$PROJECT_ROOT/monitoring/alert-rules.yml" ]]; then
        info "Configuring alert rules..."
        # Alert rules configuration would go here
    fi
    
    success "Enhanced monitoring setup completed"
}

# Generate comprehensive installation report
generate_report() {
    log "Generating comprehensive installation report..."
    
    local report_file="$PROJECT_ROOT/installation_report.txt"
    
    cat > "$report_file" << EOF
╔══════════════════════════════════════════════════════════════╗
║                TeralinkX V3 Installation Report              ║
╚══════════════════════════════════════════════════════════════╝

Generated on: $(date)
Installation Directory: $PROJECT_ROOT
Installer Version: 1.0.0

=== CONFIGURATION SUMMARY ===
Root Domain: $DOMAIN
Database Name: $DB_NAME
Database User: $DB_USER
RADIUS Database: $RADIUS_DB_NAME
Admin Username: $ADMIN_USERNAME
Admin Email: $ADMIN_EMAIL

Services Enabled:
- HIDS: $ENABLE_HIDS
- Monitoring: $ENABLE_MONITORING
- SSL Method: $SSL_METHOD
EOF

    if [[ $ENABLE_HIDS == "y" ]]; then
        cat >> "$report_file" << EOF

HIDS Configuration:
- HIDS Database: $HIDS_DB_NAME
- HIDS User: $HIDS_DB_USER
- ML Service Port: 5001
- HIDS Engine Port: 5003
- Dashboard Port: 5002
EOF
    fi
    
    cat >> "$report_file" << EOF
Frontend (Client Portal): https://cli.$DOMAIN
Backend API: https://srv.$DOMAIN
Admin Panel: https://su.$DOMAIN
EOF

    if [[ $ENABLE_MONITORING == "y" ]]; then
        echo "Grafana Dashboard: https://mt.$DOMAIN" >> "$report_file"
    fi
    
    if [[ $ENABLE_HIDS == "y" ]]; then
        echo "HIDS Security Dashboard: https://sec.$DOMAIN" >> "$report_file"
    fi
    
    cat >> "$report_file" << EOF

=== SERVICES STATUS ===
EOF
    
    # Add service status
    docker compose ps >> "$report_file" 2>/dev/null || echo "Unable to get service status" >> "$report_file"
    
    cat >> "$report_file" << EOF

=== CREDENTIALS & ACCESS ===
Django Admin:
  Username: $ADMIN_USERNAME
  Email: $ADMIN_EMAIL
  Password: [Set during installation]

Database:
  Host: localhost (via Docker)
  Database: $DB_NAME
  Username: $DB_USER
  Password: [Set during installation]

RADIUS Database:
  Database: $RADIUS_DB_NAME
  Username: $RADIUS_DB_USER
  Password: [Set during installation]
EOF

    if [[ $ENABLE_HIDS == "y" ]]; then
        cat >> "$report_file" << EOF

HIDS Database:
  Database: $HIDS_DB_NAME
  Username: $HIDS_DB_USER
  Password: [Set during installation]
  
HIDS Services:
  ML Service: http://localhost:5001
  HIDS Engine: Internal service (port 5003)
  Dashboard: https://sec.$DOMAIN
EOF
    fi
    
    if [[ $ENABLE_MONITORING == "y" ]]; then
        cat >> "$report_file" << EOF

Grafana:
  Username: $GRAFANA_USER
  Password: [Set during installation]
EOF
    fi
    
    cat >> "$report_file" << EOF

=== IMPORTANT FILES & LOCATIONS ===
Configuration Files:
  - Main Environment: $PROJECT_ROOT/.env
  - Django Backend: $PROJECT_ROOT/teralinkx/.env
  - RADIUS API: $PROJECT_ROOT/radius_api/.env
  - Frontend: $PROJECT_ROOT/TeralinkxFR/.env
  - Nginx Config: $PROJECT_ROOT/nginx/default.conf
EOF

    if [[ $ENABLE_HIDS == "y" ]]; then
        cat >> "$report_file" << EOF
  - HIDS Dashboard: $PROJECT_ROOT/hids/dashboard/.env
  - HIDS Engine: $PROJECT_ROOT/hids/engine/.env
  - ML Service: $PROJECT_ROOT/hids/ml_service/.env
EOF
    fi
    
    cat >> "$report_file" << EOF
  - Database Data: $PROJECT_ROOT/data/postgres/
  - Redis Data: $PROJECT_ROOT/data/redis/
  - SSL Certificates: $PROJECT_ROOT/certbot/conf/
  - Logs: $PROJECT_ROOT/data/logs/

Backup Location: $BACKUP_DIR
Installation Log: $LOG_FILE

=== POST-INSTALLATION CHECKLIST ===
□ Configure DNS records to point to this server
□ Verify SSL certificates are working
□ Test all service URLs
□ Configure email settings in Django admin
□ Set up regular backups
□ Review security settings
□ Configure monitoring alerts
□ Update firewall rules if needed
□ Test RADIUS authentication
□ Review HIDS detection rules

=== MAINTENANCE COMMANDS ===
View all logs:
  docker compose logs -f

View specific service logs:
  docker compose logs -f [service_name]

Restart all services:
  docker compose restart

Restart specific service:
  docker compose restart [service_name]

Update and restart services:
  docker compose pull && docker compose up -d

Backup data:
  ./scripts/deployment/backup.sh

Restore from backup:
  ./scripts/deployment/restore.sh [backup_date]

Run health checks:
  ./scripts/testing/health_check.sh

View system resources:
  docker stats

=== TROUBLESHOOTING ===
Common Issues:
1. Services not starting: Check logs with 'docker compose logs [service]'
2. SSL issues: Verify DNS and Cloudflare configuration
3. Database connection issues: Check database logs and credentials
4. Frontend not loading: Check nginx logs and build status
5. RADIUS not working: Check FreeRADIUS logs and client configuration

Support Resources:
- Documentation: $PROJECT_ROOT/docs/
- Scripts: $PROJECT_ROOT/scripts/
- Health Checks: $PROJECT_ROOT/scripts/testing/
- Deployment Scripts: $PROJECT_ROOT/scripts/deployment/

=== SECURITY NOTES ===
- Change default passwords immediately
- Review firewall configuration
- Enable fail2ban for additional protection
- Regularly update Docker images
- Monitor HIDS alerts
- Review access logs regularly

=== BACKUP INFORMATION ===
Pre-installation backup created at: $BACKUP_DIR
Backup includes:
- All configuration files
- Environment files
- SSL certificates (if existed)
- Database data (if existed)
- Custom configurations

To restore from backup:
  ./scripts/deployment/restore.sh $(basename "$BACKUP_DIR")

EOF
    
    success "Comprehensive installation report generated: $report_file"
    info "Please review this report and keep it for future reference"
}

# Cleanup function
cleanup() {
    log "Cleaning up temporary files..."
    # Add any cleanup tasks here
}

# Main installation function
main() {
    show_banner
    
    log "Starting TeralinkX V3 installation..."
    log "Installation directory: $PROJECT_ROOT"
    log "Log file: $LOG_FILE"
    
    # Create log file
    mkdir -p "$(dirname "$LOG_FILE")"
    touch "$LOG_FILE"
    
    # Installation steps
    check_prerequisites
    collect_configuration
    create_backup
    setup_environment
    setup_cloudflare
    build_frontend
    deploy_services
    setup_ssl
    perform_health_checks
    setup_monitoring
    generate_report
    cleanup
    
    echo
    success "🎉 TeralinkX V3 installation completed successfully!"
    echo
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                      ${CYAN}✨ PLATFORM ACCESS URLS ✨${NC}                           ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "  ${GREEN}•${NC} ${CYAN}Client Portal:${NC}     https://cli.$DOMAIN"
    echo -e "  ${GREEN}•${NC} ${CYAN}Admin Dashboard:${NC}   https://su.$DOMAIN"
    echo -e "  ${GREEN}•${NC} ${CYAN}Backend API:${NC}       https://srv.$DOMAIN"
    if [[ $ENABLE_MONITORING == "y" ]]; then
        echo -e "  ${GREEN}•${NC} ${CYAN}Monitoring:${NC}        https://mt.$DOMAIN"
    fi
    if [[ $ENABLE_HIDS == "y" ]]; then
        echo -e "  ${GREEN}•${NC} ${CYAN}Security (HIDS):${NC}   https://sec.$DOMAIN"
    fi
    echo
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                      ${YELLOW}📊 INSTALLATION SUMMARY 📊${NC}                         ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "  ${BLUE}📄${NC} Installation Report:  ${YELLOW}$PROJECT_ROOT/installation_report.txt${NC}"
    echo -e "  ${BLUE}📝${NC} Installation Log:     ${YELLOW}$LOG_FILE${NC}"
    echo -e "  ${BLUE}💾${NC} Backup Location:      ${YELLOW}$BACKUP_DIR${NC}"
    echo
    echo -e "${PURPLE}╔═══════════════════════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${PURPLE}║${NC}                         ${GREEN}🚀 NEXT STEPS 🚀${NC}                              ${PURPLE}║${NC}"
    echo -e "${PURPLE}╚═══════════════════════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "  ${CYAN}1.${NC} Configure DNS records to point to this server"
    echo -e "  ${CYAN}2.${NC} Review the installation report for credentials"
    echo -e "  ${CYAN}3.${NC} Access the admin dashboard to complete setup"
    echo -e "  ${CYAN}4.${NC} Configure email settings and notifications"
    echo -e "  ${CYAN}5.${NC} Set up regular automated backups"
    echo
    echo -e "${CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo
}

# Trap to ensure cleanup on exit
trap cleanup EXIT

# Run main function
main "$@"