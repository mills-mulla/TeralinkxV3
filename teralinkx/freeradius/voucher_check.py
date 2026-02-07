#!/usr/bin/env python3
"""
FreeRADIUS Python Module for Voucher Expiry Checking
Place in: /etc/freeradius/3.0/mods-config/python/voucher_check.py
"""

import radiusd
import psycopg2
from datetime import datetime, timedelta
import os

# Database connection settings
DB_CONFIG = {
    'host': os.getenv('DB_HOST', '192.168.88.16'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'radius'),
    'user': os.getenv('DB_USER', 'radius'),
    'password': os.getenv('DB_PASSWORD', 'radiuspass')
}


def get_db_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG)


def log(msg):
    """Log to FreeRADIUS"""
    radiusd.radlog(radiusd.L_INFO, f"[VOUCHER] {msg}")


def authorize(p):
    """
    Called during authorization phase
    Check if voucher is expired and activate on first use
    
    Returns:
        radiusd.RLM_MODULE_OK - Allow
        radiusd.RLM_MODULE_REJECT - Reject
        radiusd.RLM_MODULE_NOOP - Skip this module
    """
    
    # Extract username from request
    username = None
    for item in p:
        if item[0] == 'User-Name':
            username = item[1]
            break
    
    if not username:
        log("No username found in request")
        return radiusd.RLM_MODULE_NOOP
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Check if this is a voucher user
        cur.execute("""
            SELECT id, duration_seconds, activated_at, expires_at, is_active
            FROM vouchers
            WHERE username = %s
        """, (username,))
        
        voucher = cur.fetchone()
        
        if not voucher:
            # Not a voucher user, skip this module
            cur.close()
            conn.close()
            return radiusd.RLM_MODULE_NOOP
        
        voucher_id, duration_seconds, activated_at, expires_at, is_active = voucher
        
        # Check if voucher is disabled
        if not is_active:
            log(f"Voucher {username} is disabled")
            cur.close()
            conn.close()
            return radiusd.RLM_MODULE_REJECT
        
        now = datetime.utcnow()
        
        # First time activation
        if not activated_at:
            activated_at = now
            expires_at = now + timedelta(seconds=duration_seconds)
            
            cur.execute("""
                UPDATE vouchers
                SET activated_at = %s, expires_at = %s
                WHERE id = %s
            """, (activated_at, expires_at, voucher_id))
            
            conn.commit()
            log(f"Voucher {username} activated. Expires at {expires_at}")
            
            cur.close()
            conn.close()
            return radiusd.RLM_MODULE_OK
        
        # Check if expired
        if now > expires_at:
            log(f"Voucher {username} expired at {expires_at}")
            
            # Disable the voucher
            cur.execute("""
                UPDATE vouchers
                SET is_active = false
                WHERE id = %s
            """, (voucher_id,))
            conn.commit()
            
            cur.close()
            conn.close()
            return radiusd.RLM_MODULE_REJECT
        
        # Still valid
        remaining = (expires_at - now).total_seconds()
        log(f"Voucher {username} valid. {int(remaining)} seconds remaining")
        
        cur.close()
        conn.close()
        return radiusd.RLM_MODULE_OK
    
    except Exception as e:
        log(f"Error checking voucher: {str(e)}")
        return radiusd.RLM_MODULE_FAIL


def authenticate(p):
    """Called during authentication - not used"""
    return radiusd.RLM_MODULE_NOOP


def preacct(p):
    """Called before accounting - not used"""
    return radiusd.RLM_MODULE_NOOP


def accounting(p):
    """Called during accounting - not used"""
    return radiusd.RLM_MODULE_NOOP


def checksimul(p):
    """Called for simultaneous use check - not used"""
    return radiusd.RLM_MODULE_NOOP


def pre_proxy(p):
    """Called before proxying - not used"""
    return radiusd.RLM_MODULE_NOOP


def post_proxy(p):
    """Called after proxying - not used"""
    return radiusd.RLM_MODULE_NOOP


def post_auth(p):
    """Called after authentication - not used"""
    return radiusd.RLM_MODULE_NOOP


def recv_coa(p):
    """Called on CoA request - not used"""
    return radiusd.RLM_MODULE_NOOP


def send_coa(p):
    """Called on CoA response - not used"""
    return radiusd.RLM_MODULE_NOOP


def detach():
    """Called on module unload"""
    log("Voucher check module unloaded")
    return radiusd.RLM_MODULE_OK


def instantiate(p):
    """Called on module load"""
    log("Voucher check module loaded")
    return radiusd.RLM_MODULE_OK
