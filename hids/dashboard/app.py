from flask import Flask, render_template, jsonify, request
import psycopg2
import os
from datetime import datetime, timedelta

app = Flask(__name__)

POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'db')
POSTGRES_DB = os.getenv('POSTGRES_DB', 'hids')
POSTGRES_USER = os.getenv('POSTGRES_USER', 'hids')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'hidspass')

def get_db_connection():
    return psycopg2.connect(
        host=POSTGRES_HOST,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api')
def api_info():
    return jsonify({
        'message': 'HIDS Dashboard API',
        'status': 'running',
        'endpoints': [
            '/alerts',
            '/alerts/recent',
            '/hybrid-alerts',
            '/correlated',
            '/stats',
            '/top-sources',
            '/top-destinations'
        ]
    }), 200

@app.route('/alerts')
def alerts():
    """Get all Suricata alerts"""
    limit = int(request.args.get('limit', 100))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp, src_ip, src_port, dest_ip, dest_port, 
               alert_signature, alert_category, alert_severity
        FROM suricata_alerts
        ORDER BY timestamp DESC
        LIMIT %s
    """, (limit,))
    
    alerts = []
    for row in cur.fetchall():
        alerts.append({
            'id': row[0],
            'timestamp': row[1].isoformat(),
            'src_ip': str(row[2]),
            'src_port': row[3],
            'dest_ip': str(row[4]),
            'dest_port': row[5],
            'signature': row[6],
            'category': row[7],
            'severity': row[8]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'alerts': alerts, 'count': len(alerts)}), 200

@app.route('/alerts/recent')
def recent_alerts():
    """Get alerts from last hour"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    one_hour_ago = datetime.now() - timedelta(hours=1)
    
    cur.execute("""
        SELECT id, timestamp, src_ip, dest_ip, alert_signature, alert_severity
        FROM suricata_alerts
        WHERE timestamp > %s
        ORDER BY timestamp DESC
    """, (one_hour_ago,))
    
    alerts = []
    for row in cur.fetchall():
        alerts.append({
            'id': row[0],
            'timestamp': row[1].isoformat(),
            'src_ip': str(row[2]),
            'dest_ip': str(row[3]),
            'signature': row[4],
            'severity': row[5]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'alerts': alerts, 'count': len(alerts)}), 200

@app.route('/stats')
def stats():
    """Get overall statistics"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Total alerts
    cur.execute("SELECT COUNT(*) FROM suricata_alerts")
    total_alerts = cur.fetchone()[0]
    
    # Alerts by severity
    cur.execute("""
        SELECT alert_severity, COUNT(*) 
        FROM suricata_alerts 
        GROUP BY alert_severity
        ORDER BY alert_severity
    """)
    alerts_by_severity = {row[0]: row[1] for row in cur.fetchall()}
    
    # Total connections
    cur.execute("SELECT COUNT(*) FROM zeek_connections")
    total_connections = cur.fetchone()[0]
    
    # Recent activity (last 24h)
    one_day_ago = datetime.now() - timedelta(days=1)
    cur.execute("""
        SELECT COUNT(*) FROM suricata_alerts WHERE timestamp > %s
    """, (one_day_ago,))
    recent_alerts = cur.fetchone()[0]
    
    cur.close()
    conn.close()
    
    return jsonify({
        'total_alerts': total_alerts,
        'total_connections': total_connections,
        'recent_alerts_24h': recent_alerts,
        'alerts_by_severity': alerts_by_severity
    }), 200

@app.route('/top-sources')
def top_sources():
    """Get top source IPs by alert count"""
    limit = int(request.args.get('limit', 10))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT src_ip, COUNT(*) as alert_count
        FROM suricata_alerts
        GROUP BY src_ip
        ORDER BY alert_count DESC
        LIMIT %s
    """, (limit,))
    
    sources = []
    for row in cur.fetchall():
        sources.append({
            'ip': str(row[0]),
            'alert_count': row[1]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'top_sources': sources}), 200

@app.route('/top-destinations')
def top_destinations():
    """Get top destination IPs by alert count"""
    limit = int(request.args.get('limit', 10))
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT dest_ip, COUNT(*) as alert_count
        FROM suricata_alerts
        GROUP BY dest_ip
        ORDER BY alert_count DESC
        LIMIT %s
    """, (limit,))
    
    destinations = []
    for row in cur.fetchall():
        destinations.append({
            'ip': str(row[0]),
            'alert_count': row[1]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'top_destinations': destinations}), 200

@app.route('/correlated')
def correlated_alerts():
    """Get correlated and enriched hybrid alerts"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp, alert_type, severity, src_ip, dest_ip, 
               description, event_count, status, metadata
        FROM correlated_alerts
        ORDER BY timestamp DESC
        LIMIT 100
    """)
    
    alerts = []
    for row in cur.fetchall():
        metadata = row[9] if row[9] else {}
        alerts.append({
            'id': row[0],
            'timestamp': row[1].isoformat(),
            'type': row[2],
            'severity': row[3],
            'src_ip': str(row[4]) if row[4] else None,
            'dest_ip': str(row[5]) if row[5] else None,
            'description': row[6],
            'event_count': row[7],
            'status': row[8],
            'composite_score': metadata.get('composite_score'),
            'ml_prediction': metadata.get('ml_prediction'),
            'ml_confidence': metadata.get('ml_confidence')
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'correlated_alerts': alerts, 'count': len(alerts)}), 200

@app.route('/ml-analytics')
def ml_analytics():
    """Get ML service analytics"""
    try:
        import requests
        response = requests.get('http://hids_ml_service:5001/analytics', timeout=5)
        if response.status_code == 200:
            return jsonify(response.json()), 200
    except Exception as e:
        print(f"ML service error: {e}")
    return jsonify({
        'total_predictions': 0,
        'recent_anomalies': 0,
        'recent_normal': 0,
        'anomaly_rate': 0,
        'avg_confidence': 0,
        'model_type': 'random_forest_supervised',
        'top_malicious_ips': []
    }), 200

@app.route('/attack-timeline')
def attack_timeline():
    """Get attack timeline for last 24 hours"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            DATE_TRUNC('hour', timestamp) as hour,
            COUNT(*) as count,
            alert_severity
        FROM suricata_alerts
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY hour, alert_severity
        ORDER BY hour DESC
    """)
    
    timeline = []
    for row in cur.fetchall():
        timeline.append({
            'hour': row[0].isoformat(),
            'count': row[1],
            'severity': row[2]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'timeline': timeline}), 200

@app.route('/attack-types')
def attack_types():
    """Get distribution of attack types from ML predictions"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT prediction, COUNT(*) as count
        FROM ml_predictions
        WHERE prediction = 'anomaly'
        GROUP BY prediction
    """)
    
    types = []
    for row in cur.fetchall():
        types.append({
            'type': row[0],
            'count': row[1]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'attack_types': types}), 200

@app.route('/hybrid-alerts')
def hybrid_alerts():
    """Get ALL detection alerts (Suricata, ML, and Hybrid)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT id, timestamp, severity, src_ip, dest_ip, description, metadata
        FROM correlated_alerts
        WHERE alert_type IN ('hybrid_detection', 'ml_only_detection')
        ORDER BY timestamp DESC
        LIMIT 100
    """)
    
    alerts = []
    for row in cur.fetchall():
        metadata = row[6] if row[6] else {}
        detection_method = metadata.get('detection_method', 'unknown')
        
        alerts.append({
            'id': row[0],
            'timestamp': row[1].isoformat(),
            'priority': row[2].upper(),
            'src_ip': str(row[3]) if row[3] else None,
            'dest_ip': str(row[4]) if row[4] else None,
            'explanation': row[5],
            'composite_score': metadata.get('composite_score'),
            'signature': metadata.get('signature'),
            'ml_prediction': metadata.get('ml_prediction'),
            'ml_confidence': metadata.get('ml_confidence'),
            'suricata_severity': metadata.get('suricata_severity'),
            'detection_method': detection_method
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'hybrid_alerts': alerts, 'count': len(alerts)}), 200

@app.route('/detection-comparison')
def detection_comparison():
    """Compare Suricata vs ML vs Fusion detections"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get recent alerts with detection method
    cur.execute("""
        SELECT metadata
        FROM correlated_alerts
        WHERE alert_type IN ('hybrid_detection', 'ml_only_detection')
        AND timestamp > NOW() - INTERVAL '24 hours'
    """)
    
    suricata_only = 0
    ml_only = 0
    both = 0
    
    for row in cur.fetchall():
        metadata = row[0] if row[0] else {}
        method = metadata.get('detection_method', 'unknown')
        
        if method == 'both':
            both += 1
        elif method == 'ml_only':
            ml_only += 1
        elif method == 'suricata_only':
            suricata_only += 1
    
    total = suricata_only + ml_only + both
    agreement_rate = (both / total * 100) if total > 0 else 0
    
    cur.close()
    conn.close()
    
    return jsonify({
        'suricata_only': suricata_only,
        'ml_only': ml_only,
        'both': both,
        'agreement_rate': agreement_rate
    }), 200

@app.route('/block-ip', methods=['POST'])
def block_ip():
    """Block an IP address using iptables"""
    data = request.json
    ip = data.get('ip')
    
    if not ip:
        return jsonify({'error': 'IP required'}), 400
    
    try:
        import subprocess
        # Add to iptables DROP rule
        result = subprocess.run(
            ['sudo', 'iptables', '-A', 'INPUT', '-s', ip, '-j', 'DROP'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            # Log to database
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO blocked_ips (ip_address, blocked_at, reason)
                VALUES (%s, NOW(), %s)
            """, (ip, data.get('reason', 'Manual block from dashboard')))
            conn.commit()
            cur.close()
            conn.close()
            
            return jsonify({'success': True, 'message': f'IP {ip} blocked'}), 200
        else:
            return jsonify({'error': result.stderr}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/blocked-ips')
def blocked_ips():
    """Get list of blocked IPs"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT ip_address, blocked_at, reason
        FROM blocked_ips
        ORDER BY blocked_at DESC
        LIMIT 100
    """)
    
    ips = []
    for row in cur.fetchall():
        ips.append({
            'ip': row[0],
            'blocked_at': row[1].isoformat() if row[1] else None,
            'reason': row[2]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'blocked_ips': ips}), 200

@app.route('/top-attackers')
def top_attackers():
    """Get top attacking IPs with geolocation"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT src_ip, COUNT(*) as count
        FROM correlated_alerts
        WHERE timestamp > NOW() - INTERVAL '24 hours'
        GROUP BY src_ip
        ORDER BY count DESC
        LIMIT 10
    """)
    
    attackers = []
    for row in cur.fetchall():
        attackers.append({
            'ip': str(row[0]),
            'count': row[1]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'top_attackers': attackers}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
