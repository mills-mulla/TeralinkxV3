from prometheus_client import Counter, Gauge, Histogram, start_http_server
import time

# Metrics
hids_alerts_total = Counter('hids_alerts_total', 'Total alerts processed', ['severity', 'type'])
hids_anomalies_total = Counter('hids_anomalies_total', 'Total anomalies detected')
hids_ml_predictions_total = Counter('hids_ml_predictions_total', 'ML predictions', ['prediction'])
hids_processing_time = Histogram('hids_processing_time_seconds', 'Alert processing time')
hids_active_alerts = Gauge('hids_active_alerts', 'Currently active alerts')

def start_metrics_server(port=5003):
    """Start Prometheus metrics server"""
    start_http_server(port)
    print(f"✅ Metrics server started on port {port}")

def record_alert(severity, alert_type):
    """Record an alert"""
    hids_alerts_total.labels(severity=severity, type=alert_type).inc()

def record_anomaly():
    """Record an anomaly"""
    hids_anomalies_total.inc()

def record_ml_prediction(prediction):
    """Record ML prediction"""
    hids_ml_predictions_total.labels(prediction=prediction).inc()
