#!/bin/bash

# TeralinkX V3 - Interactive Service Selection
# Allows users to choose which services to install
# Author: TeralinkX Team

# This function will be sourced by install.sh

show_service_selection_menu() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║           TeralinkX V3 - Service Selection Menu             ║
║                  ISP Management Platform                     ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${PURPLE}Select Installation Profile:${NC}"
    echo
    echo "1. 🚀 Full Installation (Recommended)"
    echo "   └─ All services including HIDS and Monitoring"
    echo
    echo "2. 💼 Enterprise ISP"
    echo "   └─ Core + RADIUS + Monitoring (No HIDS)"
    echo
    echo "3. 🏢 Small Business ISP"
    echo "   └─ Core + RADIUS only"
    echo
    echo "4. 🧪 Development/Testing"
    echo "   └─ Core services only (minimal)"
    echo
    echo "5. 🎯 Custom Selection"
    echo "   └─ Choose individual services"
    echo
    read -p "Enter choice (1-5): " INSTALL_PROFILE
    
    case $INSTALL_PROFILE in
        1)
            profile_full_installation
            ;;
        2)
            profile_enterprise_isp
            ;;
        3)
            profile_small_business
            ;;
        4)
            profile_development
            ;;
        5)
            profile_custom_selection
            ;;
        *)
            error "Invalid choice"
            ;;
    esac
}

profile_full_installation() {
    log "Selected: Full Installation (Recommended)"
    
    # Core Services (Always installed)
    INSTALL_CORE=true
    INSTALL_DATABASE=true
    INSTALL_REDIS=true
    INSTALL_CELERY=true
    
    # Django Apps
    INSTALL_WEB=true
    INSTALL_RADIUS_API=true
    
    # RADIUS Server
    INSTALL_FREERADIUS=true
    
    # Reverse Proxy & SSL
    INSTALL_NGINX=true
    INSTALL_CERTBOT=true
    INSTALL_CLOUDFLARED=true
    
    # HIDS (Recommended)
    INSTALL_HIDS=true
    INSTALL_SURICATA=true
    INSTALL_ZEEK=true
    INSTALL_ML_SERVICE=true
    
    # Monitoring (Recommended)
    INSTALL_MONITORING=true
    INSTALL_PROMETHEUS=true
    INSTALL_GRAFANA=true
    INSTALL_LOKI=true
    
    # Frontend
    INSTALL_FRONTEND=true
    
    show_selected_services
}

profile_enterprise_isp() {
    log "Selected: Enterprise ISP Profile"
    
    # Core Services
    INSTALL_CORE=true
    INSTALL_DATABASE=true
    INSTALL_REDIS=true
    INSTALL_CELERY=true
    
    # Django Apps
    INSTALL_WEB=true
    INSTALL_RADIUS_API=true
    
    # RADIUS Server
    INSTALL_FREERADIUS=true
    
    # Reverse Proxy & SSL
    INSTALL_NGINX=true
    INSTALL_CERTBOT=true
    INSTALL_CLOUDFLARED=true
    
    # HIDS (Optional for Enterprise)
    INSTALL_HIDS=false
    INSTALL_SURICATA=false
    INSTALL_ZEEK=false
    INSTALL_ML_SERVICE=false
    
    # Monitoring (Included)
    INSTALL_MONITORING=true
    INSTALL_PROMETHEUS=true
    INSTALL_GRAFANA=true
    INSTALL_LOKI=true
    
    # Frontend
    INSTALL_FRONTEND=true
    
    show_selected_services
}

profile_small_business() {
    log "Selected: Small Business ISP Profile"
    
    # Core Services
    INSTALL_CORE=true
    INSTALL_DATABASE=true
    INSTALL_REDIS=true
    INSTALL_CELERY=true
    
    # Django Apps
    INSTALL_WEB=true
    INSTALL_RADIUS_API=true
    
    # RADIUS Server
    INSTALL_FREERADIUS=true
    
    # Reverse Proxy & SSL
    INSTALL_NGINX=true
    INSTALL_CERTBOT=true
    INSTALL_CLOUDFLARED=false
    
    # HIDS (Not included)
    INSTALL_HIDS=false
    INSTALL_SURICATA=false
    INSTALL_ZEEK=false
    INSTALL_ML_SERVICE=false
    
    # Monitoring (Not included)
    INSTALL_MONITORING=false
    INSTALL_PROMETHEUS=false
    INSTALL_GRAFANA=false
    INSTALL_LOKI=false
    
    # Frontend
    INSTALL_FRONTEND=true
    
    show_selected_services
}

profile_development() {
    log "Selected: Development/Testing Profile"
    
    # Core Services
    INSTALL_CORE=true
    INSTALL_DATABASE=true
    INSTALL_REDIS=true
    INSTALL_CELERY=true
    
    # Django Apps
    INSTALL_WEB=true
    INSTALL_RADIUS_API=false
    
    # RADIUS Server
    INSTALL_FREERADIUS=false
    
    # Reverse Proxy & SSL
    INSTALL_NGINX=true
    INSTALL_CERTBOT=false
    INSTALL_CLOUDFLARED=false
    
    # HIDS (Not included)
    INSTALL_HIDS=false
    INSTALL_SURICATA=false
    INSTALL_ZEEK=false
    INSTALL_ML_SERVICE=false
    
    # Monitoring (Not included)
    INSTALL_MONITORING=false
    INSTALL_PROMETHEUS=false
    INSTALL_GRAFANA=false
    INSTALL_LOKI=false
    
    # Frontend
    INSTALL_FRONTEND=true
    
    show_selected_services
}

profile_custom_selection() {
    log "Selected: Custom Service Selection"
    echo
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}Select services to install (y/n for each):${NC}"
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    echo
    
    # Core Services (Always required)
    echo -e "${GREEN}📦 CORE SERVICES (Required):${NC}"
    INSTALL_CORE=true
    INSTALL_DATABASE=true
    INSTALL_REDIS=true
    INSTALL_CELERY=true
    echo "  ✓ PostgreSQL Database"
    echo "  ✓ Redis Cache"
    echo "  ✓ Celery Task Queue"
    echo
    
    # Django Applications
    echo -e "${GREEN}🐍 DJANGO APPLICATIONS:${NC}"
    INSTALL_WEB=true
    echo "  ✓ Main Web Application (Required)"
    
    read -p "  Install RADIUS API? (y/n) [y]: " choice
    INSTALL_RADIUS_API=${choice:-y}
    [[ $INSTALL_RADIUS_API == "y" ]] && INSTALL_RADIUS_API=true || INSTALL_RADIUS_API=false
    echo
    
    # RADIUS Server
    if [[ $INSTALL_RADIUS_API == true ]]; then
        echo -e "${GREEN}📡 RADIUS SERVER:${NC}"
        read -p "  Install FreeRADIUS? (y/n) [y]: " choice
        INSTALL_FREERADIUS=${choice:-y}
        [[ $INSTALL_FREERADIUS == "y" ]] && INSTALL_FREERADIUS=true || INSTALL_FREERADIUS=false
        echo
    else
        INSTALL_FREERADIUS=false
    fi
    
    # Reverse Proxy & SSL
    echo -e "${GREEN}🌐 REVERSE PROXY & SSL:${NC}"
    INSTALL_NGINX=true
    echo "  ✓ Nginx (Required)"
    
    read -p "  Install Certbot (SSL certificates)? (y/n) [y]: " choice
    INSTALL_CERTBOT=${choice:-y}
    [[ $INSTALL_CERTBOT == "y" ]] && INSTALL_CERTBOT=true || INSTALL_CERTBOT=false
    
    read -p "  Install Cloudflared (Cloudflare tunnel)? (y/n) [n]: " choice
    INSTALL_CLOUDFLARED=${choice:-n}
    [[ $INSTALL_CLOUDFLARED == "y" ]] && INSTALL_CLOUDFLARED=true || INSTALL_CLOUDFLARED=false
    echo
    
    # HIDS (Recommended)
    echo -e "${GREEN}🛡️  HIDS - HOST INTRUSION DETECTION (Recommended):${NC}"
    read -p "  Install HIDS services? (y/n) [y]: " choice
    INSTALL_HIDS=${choice:-y}
    [[ $INSTALL_HIDS == "y" ]] && INSTALL_HIDS=true || INSTALL_HIDS=false
    
    if [[ $INSTALL_HIDS == true ]]; then
        read -p "    Install Suricata IDS? (y/n) [y]: " choice
        INSTALL_SURICATA=${choice:-y}
        [[ $INSTALL_SURICATA == "y" ]] && INSTALL_SURICATA=true || INSTALL_SURICATA=false
        
        read -p "    Install Zeek Network Monitor? (y/n) [y]: " choice
        INSTALL_ZEEK=${choice:-y}
        [[ $INSTALL_ZEEK == "y" ]] && INSTALL_ZEEK=true || INSTALL_ZEEK=false
        
        read -p "    Install ML Anomaly Detection? (y/n) [y]: " choice
        INSTALL_ML_SERVICE=${choice:-y}
        [[ $INSTALL_ML_SERVICE == "y" ]] && INSTALL_ML_SERVICE=true || INSTALL_ML_SERVICE=false
    else
        INSTALL_SURICATA=false
        INSTALL_ZEEK=false
        INSTALL_ML_SERVICE=false
    fi
    echo
    
    # Monitoring Stack (Recommended)
    echo -e "${GREEN}📊 MONITORING STACK (Recommended):${NC}"
    read -p "  Install Monitoring services? (y/n) [y]: " choice
    INSTALL_MONITORING=${choice:-y}
    [[ $INSTALL_MONITORING == "y" ]] && INSTALL_MONITORING=true || INSTALL_MONITORING=false
    
    if [[ $INSTALL_MONITORING == true ]]; then
        read -p "    Install Prometheus? (y/n) [y]: " choice
        INSTALL_PROMETHEUS=${choice:-y}
        [[ $INSTALL_PROMETHEUS == "y" ]] && INSTALL_PROMETHEUS=true || INSTALL_PROMETHEUS=false
        
        read -p "    Install Grafana? (y/n) [y]: " choice
        INSTALL_GRAFANA=${choice:-y}
        [[ $INSTALL_GRAFANA == "y" ]] && INSTALL_GRAFANA=true || INSTALL_GRAFANA=false
        
        read -p "    Install Loki (Log aggregation)? (y/n) [y]: " choice
        INSTALL_LOKI=${choice:-y}
        [[ $INSTALL_LOKI == "y" ]] && INSTALL_LOKI=true || INSTALL_LOKI=false
    else
        INSTALL_PROMETHEUS=false
        INSTALL_GRAFANA=false
        INSTALL_LOKI=false
    fi
    echo
    
    # Frontend
    echo -e "${GREEN}🎨 FRONTEND:${NC}"
    read -p "  Build and install frontend? (y/n) [y]: " choice
    INSTALL_FRONTEND=${choice:-y}
    [[ $INSTALL_FRONTEND == "y" ]] && INSTALL_FRONTEND=true || INSTALL_FRONTEND=false
    echo
    
    show_selected_services
}

show_selected_services() {
    clear
    echo -e "${CYAN}"
    cat << "EOF"
╔══════════════════════════════════════════════════════════════╗
║              Selected Services Summary                       ║
╚══════════════════════════════════════════════════════════════╝
EOF
    echo -e "${NC}"
    
    echo -e "${GREEN}✓ CORE SERVICES:${NC}"
    echo "  • PostgreSQL Database"
    echo "  • Redis Cache"
    echo "  • Celery Task Queue"
    echo
    
    echo -e "${GREEN}✓ DJANGO APPLICATIONS:${NC}"
    echo "  • Main Web Application"
    [[ $INSTALL_RADIUS_API == true ]] && echo "  • RADIUS API" || echo "  ✗ RADIUS API"
    echo
    
    if [[ $INSTALL_FREERADIUS == true ]]; then
        echo -e "${GREEN}✓ RADIUS SERVER:${NC}"
        echo "  • FreeRADIUS"
        echo
    fi
    
    echo -e "${GREEN}✓ REVERSE PROXY & SSL:${NC}"
    echo "  • Nginx"
    [[ $INSTALL_CERTBOT == true ]] && echo "  • Certbot (SSL)" || echo "  ✗ Certbot"
    [[ $INSTALL_CLOUDFLARED == true ]] && echo "  • Cloudflared" || echo "  ✗ Cloudflared"
    echo
    
    if [[ $INSTALL_HIDS == true ]]; then
        echo -e "${GREEN}✓ HIDS (Host Intrusion Detection):${NC}"
        [[ $INSTALL_SURICATA == true ]] && echo "  • Suricata IDS" || echo "  ✗ Suricata IDS"
        [[ $INSTALL_ZEEK == true ]] && echo "  • Zeek Network Monitor" || echo "  ✗ Zeek"
        [[ $INSTALL_ML_SERVICE == true ]] && echo "  • ML Anomaly Detection" || echo "  ✗ ML Service"
        echo "  • HIDS Engine"
        echo "  • HIDS Dashboard"
        echo
    fi
    
    if [[ $INSTALL_MONITORING == true ]]; then
        echo -e "${GREEN}✓ MONITORING STACK:${NC}"
        [[ $INSTALL_PROMETHEUS == true ]] && echo "  • Prometheus" || echo "  ✗ Prometheus"
        [[ $INSTALL_GRAFANA == true ]] && echo "  • Grafana" || echo "  ✗ Grafana"
        [[ $INSTALL_LOKI == true ]] && echo "  • Loki + Promtail" || echo "  ✗ Loki"
        echo "  • AlertManager"
        echo "  • Exporters (Node, Redis, PostgreSQL)"
        echo
    fi
    
    if [[ $INSTALL_FRONTEND == true ]]; then
        echo -e "${GREEN}✓ FRONTEND:${NC}"
        echo "  • Vue.js Application"
        echo
    fi
    
    # Calculate estimated resources
    calculate_resource_requirements
    
    echo
    echo -e "${YELLOW}═══════════════════════════════════════════════════════${NC}"
    read -p "Proceed with this configuration? (y/n) [y]: " CONFIRM
    CONFIRM=${CONFIRM:-y}
    
    if [[ $CONFIRM != "y" ]]; then
        log "Installation cancelled by user"
        exit 0
    fi
    
    # Export all variables for use in main install script
    export INSTALL_CORE INSTALL_DATABASE INSTALL_REDIS INSTALL_CELERY
    export INSTALL_WEB INSTALL_RADIUS_API INSTALL_FREERADIUS
    export INSTALL_NGINX INSTALL_CERTBOT INSTALL_CLOUDFLARED
    export INSTALL_HIDS INSTALL_SURICATA INSTALL_ZEEK INSTALL_ML_SERVICE
    export INSTALL_MONITORING INSTALL_PROMETHEUS INSTALL_GRAFANA INSTALL_LOKI
    export INSTALL_FRONTEND
}

calculate_resource_requirements() {
    local min_ram=2
    local min_disk=5
    local estimated_services=5
    
    # Calculate based on selected services
    [[ $INSTALL_DATABASE == true ]] && ((min_ram+=1)) && ((min_disk+=2))
    [[ $INSTALL_REDIS == true ]] && ((min_ram+=1))
    [[ $INSTALL_WEB == true ]] && ((min_ram+=1)) && ((min_disk+=1))
    [[ $INSTALL_RADIUS_API == true ]] && ((min_ram+=1))
    [[ $INSTALL_FREERADIUS == true ]] && ((min_ram+=1))
    
    if [[ $INSTALL_HIDS == true ]]; then
        ((min_ram+=2))
        ((min_disk+=3))
        ((estimated_services+=4))
    fi
    
    if [[ $INSTALL_MONITORING == true ]]; then
        ((min_ram+=2))
        ((min_disk+=2))
        ((estimated_services+=5))
    fi
    
    echo -e "${BLUE}📊 ESTIMATED RESOURCE REQUIREMENTS:${NC}"
    echo "  • Minimum RAM: ${min_ram}GB"
    echo "  • Minimum Disk: ${min_disk}GB"
    echo "  • Services to deploy: ~${estimated_services}"
    echo "  • Estimated deployment time: 5-15 minutes"
}

# Export function for use in install.sh
export -f show_service_selection_menu
export -f profile_full_installation
export -f profile_enterprise_isp
export -f profile_small_business
export -f profile_development
export -f profile_custom_selection
export -f show_selected_services
export -f calculate_resource_requirements
