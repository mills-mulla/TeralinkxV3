from flask import Flask, render_template, jsonify, request, send_file
import psycopg2
import os
import subprocess
import json
from datetime import datetime, timedelta
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Prometheus metrics
dashboard_requests = Counter('hids_dashboard_requests_total', 'Total dashboard requests', ['endpoint'])

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
    dashboard_requests.labels(endpoint='index').inc()
    return render_template('index.html')

@app.route('/metrics')
def metrics():
    """Prometheus metrics endpoint"""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

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

# ===============================
# IDS EVALUATION & TESTING SECTION
# ===============================

PCAP_UPLOAD_DIR = '/pcaps'
ALLOWED_EXTENSIONS = {'pcap', 'pcapng'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/evaluation')
def evaluation_dashboard():
    """Evaluation dashboard page"""
    return render_template('evaluation.html')

@app.route('/api/evaluation/upload-pcap', methods=['POST'])
def upload_pcap():
    """Upload PCAP file for evaluation"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Only .pcap and .pcapng allowed'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(PCAP_UPLOAD_DIR, filename)
    file.save(filepath)
    
    return jsonify({
        'success': True,
        'filename': filename,
        'filepath': filepath,
        'size': os.path.getsize(filepath)
    }), 200

@app.route('/api/evaluation/list-pcaps')
def list_pcaps():
    """List available PCAP files"""
    if not os.path.exists(PCAP_UPLOAD_DIR):
        return jsonify({'pcaps': []}), 200
    
    pcaps = []
    for filename in os.listdir(PCAP_UPLOAD_DIR):
        if allowed_file(filename):
            filepath = os.path.join(PCAP_UPLOAD_DIR, filename)
            pcaps.append({
                'filename': filename,
                'size': os.path.getsize(filepath),
                'modified': datetime.fromtimestamp(os.path.getmtime(filepath)).isoformat()
            })
    
    return jsonify({'pcaps': sorted(pcaps, key=lambda x: x['modified'], reverse=True)}), 200

@app.route('/api/evaluation/replay-pcap', methods=['POST'])
def replay_pcap():
    """Replay PCAP file using tcpreplay"""
    data = request.json
    filename = data.get('filename')
    interface = data.get('interface', 'br-c51890515ece')
    speed = data.get('speed', 1)  # 1x, 2x, 10x speed
    
    if not filename:
        return jsonify({'error': 'Filename required'}), 400
    
    filepath = os.path.join(PCAP_UPLOAD_DIR, secure_filename(filename))
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Run tcpreplay in background
        cmd = ['docker', 'exec', 'hids_tcpreplay', 'tcpreplay', 
               '-i', interface, '-x', str(speed), filepath]
        
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        return jsonify({
            'success': True,
            'message': f'Replaying {filename} at {speed}x speed',
            'pid': result.pid
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/evaluation/model-performance')
def model_performance():
    """Get ML model performance metrics"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Get predictions from last evaluation
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            SUM(CASE WHEN prediction = 'anomaly' THEN 1 ELSE 0 END) as anomalies,
            SUM(CASE WHEN prediction = 'normal' THEN 1 ELSE 0 END) as normal,
            AVG(confidence) as avg_confidence
        FROM ml_predictions
        WHERE timestamp > NOW() - INTERVAL '1 hour'
    """)
    
    row = cur.fetchone()
    total = row[0] or 0
    anomalies = row[1] or 0
    normal = row[2] or 0
    avg_confidence = float(row[3]) if row[3] else 0
    
    # Get detection method breakdown
    cur.execute("""
        SELECT 
            metadata->>'detection_method' as method,
            COUNT(*) as count
        FROM correlated_alerts
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY method
    """)
    
    detection_methods = {}
    for row in cur.fetchall():
        if row[0]:
            detection_methods[row[0]] = row[1]
    
    cur.close()
    conn.close()
    
    return jsonify({
        'total_predictions': total,
        'anomalies_detected': anomalies,
        'normal_traffic': normal,
        'anomaly_rate': (anomalies / total * 100) if total > 0 else 0,
        'avg_confidence': round(avg_confidence, 2),
        'detection_methods': detection_methods
    }), 200

@app.route('/api/evaluation/confusion-matrix')
def confusion_matrix():
    """Get confusion matrix data (requires ground truth labels)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    # This assumes you have a ground_truth column in ml_predictions
    cur.execute("""
        SELECT 
            prediction,
            ground_truth,
            COUNT(*) as count
        FROM ml_predictions
        WHERE ground_truth IS NOT NULL
        AND timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY prediction, ground_truth
    """)
    
    matrix = {'TP': 0, 'TN': 0, 'FP': 0, 'FN': 0}
    
    for row in cur.fetchall():
        pred = row[0]
        truth = row[1]
        count = row[2]
        
        if pred == 'anomaly' and truth == 'anomaly':
            matrix['TP'] += count
        elif pred == 'normal' and truth == 'normal':
            matrix['TN'] += count
        elif pred == 'anomaly' and truth == 'normal':
            matrix['FP'] += count
        elif pred == 'normal' and truth == 'anomaly':
            matrix['FN'] += count
    
    total = sum(matrix.values())
    accuracy = ((matrix['TP'] + matrix['TN']) / total * 100) if total > 0 else 0
    precision = (matrix['TP'] / (matrix['TP'] + matrix['FP']) * 100) if (matrix['TP'] + matrix['FP']) > 0 else 0
    recall = (matrix['TP'] / (matrix['TP'] + matrix['FN']) * 100) if (matrix['TP'] + matrix['FN']) > 0 else 0
    f1_score = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
    fpr = (matrix['FP'] / (matrix['FP'] + matrix['TN']) * 100) if (matrix['FP'] + matrix['TN']) > 0 else 0
    
    cur.close()
    conn.close()
    
    return jsonify({
        'confusion_matrix': matrix,
        'metrics': {
            'accuracy': round(accuracy, 2),
            'precision': round(precision, 2),
            'recall': round(recall, 2),
            'f1_score': round(f1_score, 2),
            'false_positive_rate': round(fpr, 2)
        }
    }), 200

@app.route('/api/evaluation/detection-timeline')
def detection_timeline():
    """Get detection timeline for evaluation period"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            DATE_TRUNC('minute', timestamp) as minute,
            COUNT(*) as total,
            SUM(CASE WHEN metadata->>'detection_method' = 'ml_confirmed_by_suricata' THEN 1 ELSE 0 END) as ml_confirmed,
            SUM(CASE WHEN metadata->>'detection_method' = 'ml_primary' THEN 1 ELSE 0 END) as ml_primary,
            SUM(CASE WHEN metadata->>'detection_method' = 'suricata_override' THEN 1 ELSE 0 END) as suricata_override
        FROM correlated_alerts
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY minute
        ORDER BY minute
    """)
    
    timeline = []
    for row in cur.fetchall():
        timeline.append({
            'timestamp': row[0].isoformat(),
            'total': row[1],
            'ml_confirmed': row[2],
            'ml_primary': row[3],
            'suricata_override': row[4]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'timeline': timeline}), 200

@app.route('/api/evaluation/attack-breakdown')
def attack_breakdown():
    """Get breakdown of detected attack types"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            metadata->>'signature' as attack_type,
            COUNT(*) as count,
            AVG((metadata->>'composite_score')::float) as avg_score
        FROM correlated_alerts
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        AND metadata->>'signature' IS NOT NULL
        GROUP BY attack_type
        ORDER BY count DESC
        LIMIT 20
    """)
    
    attacks = []
    for row in cur.fetchall():
        attacks.append({
            'type': row[0],
            'count': row[1],
            'avg_score': round(float(row[2]), 2) if row[2] else 0
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'attacks': attacks}), 200

@app.route('/api/evaluation/ml-confidence-distribution')
def ml_confidence_distribution():
    """Get ML confidence score distribution"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            CASE 
                WHEN confidence >= 0.9 THEN '90-100%'
                WHEN confidence >= 0.8 THEN '80-90%'
                WHEN confidence >= 0.7 THEN '70-80%'
                WHEN confidence >= 0.6 THEN '60-70%'
                ELSE '<60%'
            END as confidence_range,
            COUNT(*) as count
        FROM ml_predictions
        WHERE timestamp > NOW() - INTERVAL '1 hour'
        GROUP BY confidence_range
        ORDER BY confidence_range DESC
    """)
    
    distribution = {}
    for row in cur.fetchall():
        distribution[row[0]] = row[1]
    
    cur.close()
    conn.close()
    
    return jsonify({'distribution': distribution}), 200

@app.route('/api/evaluation/zero-day-detections')
def zero_day_detections():
    """Get ML-only detections (potential zero-days)"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
        SELECT 
            id,
            timestamp,
            src_ip,
            dest_ip,
            description,
            metadata
        FROM correlated_alerts
        WHERE metadata->>'detection_method' = 'ml_primary'
        AND timestamp > NOW() - INTERVAL '1 hour'
        ORDER BY timestamp DESC
        LIMIT 50
    """)
    
    detections = []
    for row in cur.fetchall():
        metadata = row[5] if row[5] else {}
        detections.append({
            'id': row[0],
            'timestamp': row[1].isoformat(),
            'src_ip': str(row[2]),
            'dest_ip': str(row[3]),
            'description': row[4],
            'ml_confidence': metadata.get('ml_confidence'),
            'composite_score': metadata.get('composite_score')
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'zero_day_detections': detections, 'count': len(detections)}), 200

@app.route('/api/evaluation/export-results', methods=['POST'])
def export_results():
    """Export evaluation results as JSON"""
    data = request.json
    start_time = data.get('start_time')
    end_time = data.get('end_time')
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    query = """
        SELECT 
            timestamp,
            src_ip,
            dest_ip,
            alert_type,
            severity,
            description,
            metadata
        FROM correlated_alerts
        WHERE 1=1
    """
    
    params = []
    if start_time:
        query += " AND timestamp >= %s"
        params.append(start_time)
    if end_time:
        query += " AND timestamp <= %s"
        params.append(end_time)
    
    query += " ORDER BY timestamp"
    
    cur.execute(query, params)
    
    results = []
    for row in cur.fetchall():
        results.append({
            'timestamp': row[0].isoformat(),
            'src_ip': str(row[1]),
            'dest_ip': str(row[2]),
            'alert_type': row[3],
            'severity': row[4],
            'description': row[5],
            'metadata': row[6]
        })
    
    cur.close()
    conn.close()
    
    return jsonify({'results': results, 'count': len(results)}), 200

@app.route('/api/evaluation/clear-test-data', methods=['POST'])
def clear_test_data():
    """Clear test data from database"""
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM ml_predictions WHERE timestamp > NOW() - INTERVAL '1 hour'")
        cur.execute("DELETE FROM correlated_alerts WHERE timestamp > NOW() - INTERVAL '1 hour'")
        cur.execute("DELETE FROM suricata_alerts WHERE timestamp > NOW() - INTERVAL '1 hour'")
        cur.execute("DELETE FROM zeek_connections WHERE timestamp > NOW() - INTERVAL '1 hour'")
        
        conn.commit()
        
        return jsonify({'success': True, 'message': 'Test data cleared'}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
