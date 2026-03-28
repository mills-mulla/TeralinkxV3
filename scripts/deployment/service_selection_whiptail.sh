#!/bin/bash

# TeralinkX V3 - Whiptail-based Interactive Service Selection
# Visual menu interface using whiptail

show_service_selection_menu() {
    # Check if whiptail is available
    if ! command -v whiptail &> /dev/null; then
        source "$SCRIPT_DIR/service_selection.sh"
        return
    fi
    
    # Main profile selection
    PROFILE=$(whiptail --title "TeralinkX V3 - Service Selection" \
        --menu "Choose your installation profile:" 20 78 6 \
        "1" "Full Installation - All services (8GB RAM, 50GB Disk)" \
        "2" "Enterprise ISP - Complete ISP + Monitoring (6GB RAM)" \
        "3" "Small Business - Core ISP features only (4GB RAM)" \
        "4" "Development - Minimal testing setup (2GB RAM)" \
        "5" "Custom - Choose specific services" \
        3>&1 1>&2 2>&3)
    
    # Check if cancelled
    if [ $? -ne 0 ]; then
        error "Installation cancelled"
    fi
    
    case $PROFILE in
        1) profile_full_installation ;;
        2) profile_enterprise_isp ;;
        3) profile_small_business ;;
        4) profile_development ;;
        5) profile_custom_whiptail ;;
        *) profile_full_installation ;;
    esac
    
    show_summary_whiptail
}

profile_custom_whiptail() {
    # Core always enabled
    INSTALL_CORE=true
    INSTALL_DATABASE=true
    INSTALL_REDIS=true
    INSTALL_CELERY=true
    INSTALL_WEB=true
    INSTALL_NGINX=true
    
    # RADIUS selection
    if whiptail --title "RADIUS Services" --yesno "Install RADIUS API and FreeRADIUS server?" 10 60; then
        INSTALL_RADIUS_API=true
        INSTALL_FREERADIUS=true
    else
        INSTALL_RADIUS_API=false
        INSTALL_FREERADIUS=false
    fi
    
    # SSL selection
    if whiptail --title "SSL Certificates" --yesno "Install Certbot for SSL certificates?" 10 60; then
        INSTALL_CERTBOT=true
    else
        INSTALL_CERTBOT=false
    fi
    
    if whiptail --title "Cloudflare Tunnel" --yesno "Install Cloudflared tunnel?" 10 60; then
        INSTALL_CLOUDFLARED=true
    else
        INSTALL_CLOUDFLARED=false
    fi
    
    # HIDS selection
    if whiptail --title "HIDS Security" --yesno "Install HIDS (Host Intrusion Detection System)?\n\nIncludes: Suricata, Zeek, ML Detection" 12 60; then
        INSTALL_HIDS=true
        INSTALL_SURICATA=true
        INSTALL_ZEEK=true
        INSTALL_ML_SERVICE=true
    else
        INSTALL_HIDS=false
        INSTALL_SURICATA=false
        INSTALL_ZEEK=false
        INSTALL_ML_SERVICE=false
    fi
    
    # Monitoring selection
    if whiptail --title "Monitoring Stack" --yesno "Install Monitoring services?\n\nIncludes: Prometheus, Grafana, Loki" 12 60; then
        INSTALL_MONITORING=true
        INSTALL_PROMETHEUS=true
        INSTALL_GRAFANA=true
        INSTALL_LOKI=true
    else
        INSTALL_MONITORING=false
        INSTALL_PROMETHEUS=false
        INSTALL_GRAFANA=false
        INSTALL_LOKI=false
    fi
    
    # Frontend
    if whiptail --title "Frontend" --yesno "Build and install Vue.js frontend?" 10 60; then
        INSTALL_FRONTEND=true
    else
        INSTALL_FRONTEND=false
    fi
}

show_summary_whiptail() {
    local summary="SELECTED SERVICES:\n\n"
    summary+="✓ Core Services (Database, Redis, Celery)\n"
    summary+="✓ Django Web Application\n"
    
    [[ $INSTALL_RADIUS_API == true ]] && summary+="✓ RADIUS API & FreeRADIUS\n" || summary+="✗ RADIUS Services\n"
    [[ $INSTALL_CERTBOT == true ]] && summary+="✓ SSL Certificates (Certbot)\n" || summary+="✗ SSL Certificates\n"
    [[ $INSTALL_CLOUDFLARED == true ]] && summary+="✓ Cloudflare Tunnel\n" || summary+="✗ Cloudflare Tunnel\n"
    [[ $INSTALL_HIDS == true ]] && summary+="✓ HIDS Security Suite\n" || summary+="✗ HIDS Security\n"
    [[ $INSTALL_MONITORING == true ]] && summary+="✓ Monitoring Stack\n" || summary+="✗ Monitoring Stack\n"
    [[ $INSTALL_FRONTEND == true ]] && summary+="✓ Vue.js Frontend\n" || summary+="✗ Frontend\n"
    
    # Calculate resources
    local ram=2
    local disk=10
    [[ $INSTALL_HIDS == true ]] && ((ram+=2)) && ((disk+=10))
    [[ $INSTALL_MONITORING == true ]] && ((ram+=2)) && ((disk+=10))
    
    summary+="\nRESOURCE REQUIREMENTS:\n"
    summary+="• RAM: ${ram}GB minimum\n"
    summary+="• Disk: ${disk}GB minimum\n"
    
    if whiptail --title "Installation Summary" --yesno "$summary\n\nProceed with installation?" 25 70; then
        export INSTALL_CORE INSTALL_DATABASE INSTALL_REDIS INSTALL_CELERY
        export INSTALL_WEB INSTALL_RADIUS_API INSTALL_FREERADIUS
        export INSTALL_NGINX INSTALL_CERTBOT INSTALL_CLOUDFLARED
        export INSTALL_HIDS INSTALL_SURICATA INSTALL_ZEEK INSTALL_ML_SERVICE
        export INSTALL_MONITORING INSTALL_PROMETHEUS INSTALL_GRAFANA INSTALL_LOKI
        export INSTALL_FRONTEND
    else
        error "Installation cancelled"
    fi
}

# Profile functions
profile_full_installation() {
    INSTALL_CORE=true; INSTALL_DATABASE=true; INSTALL_REDIS=true; INSTALL_CELERY=true
    INSTALL_WEB=true; INSTALL_RADIUS_API=true; INSTALL_FREERADIUS=true
    INSTALL_NGINX=true; INSTALL_CERTBOT=true; INSTALL_CLOUDFLARED=true
    INSTALL_HIDS=true; INSTALL_SURICATA=true; INSTALL_ZEEK=true; INSTALL_ML_SERVICE=true
    INSTALL_MONITORING=true; INSTALL_PROMETHEUS=true; INSTALL_GRAFANA=true; INSTALL_LOKI=true
    INSTALL_FRONTEND=true
}

profile_enterprise_isp() {
    INSTALL_CORE=true; INSTALL_DATABASE=true; INSTALL_REDIS=true; INSTALL_CELERY=true
    INSTALL_WEB=true; INSTALL_RADIUS_API=true; INSTALL_FREERADIUS=true
    INSTALL_NGINX=true; INSTALL_CERTBOT=true; INSTALL_CLOUDFLARED=true
    INSTALL_HIDS=false; INSTALL_SURICATA=false; INSTALL_ZEEK=false; INSTALL_ML_SERVICE=false
    INSTALL_MONITORING=true; INSTALL_PROMETHEUS=true; INSTALL_GRAFANA=true; INSTALL_LOKI=true
    INSTALL_FRONTEND=true
}

profile_small_business() {
    INSTALL_CORE=true; INSTALL_DATABASE=true; INSTALL_REDIS=true; INSTALL_CELERY=true
    INSTALL_WEB=true; INSTALL_RADIUS_API=true; INSTALL_FREERADIUS=true
    INSTALL_NGINX=true; INSTALL_CERTBOT=true; INSTALL_CLOUDFLARED=false
    INSTALL_HIDS=false; INSTALL_SURICATA=false; INSTALL_ZEEK=false; INSTALL_ML_SERVICE=false
    INSTALL_MONITORING=false; INSTALL_PROMETHEUS=false; INSTALL_GRAFANA=false; INSTALL_LOKI=false
    INSTALL_FRONTEND=true
}

profile_development() {
    INSTALL_CORE=true; INSTALL_DATABASE=true; INSTALL_REDIS=true; INSTALL_CELERY=true
    INSTALL_WEB=true; INSTALL_RADIUS_API=false; INSTALL_FREERADIUS=false
    INSTALL_NGINX=true; INSTALL_CERTBOT=false; INSTALL_CLOUDFLARED=false
    INSTALL_HIDS=false; INSTALL_SURICATA=false; INSTALL_ZEEK=false; INSTALL_ML_SERVICE=false
    INSTALL_MONITORING=false; INSTALL_PROMETHEUS=false; INSTALL_GRAFANA=false; INSTALL_LOKI=false
    INSTALL_FRONTEND=true
}
