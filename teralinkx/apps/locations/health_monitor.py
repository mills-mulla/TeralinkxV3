"""
Production-grade health monitoring and alerting system
Monitors location health, network connectivity, and system performance
"""

import asyncio
import logging
import psutil
import time
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

from django.utils import timezone
from django.db import connection
from django.core.cache import cache
from django.conf import settings
from django.core.mail import send_mail

from .models import Location, NodeIdentity, LocationHealthMetrics, LocationMesh
from .sync_services import get_sync_service

logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class HealthStatus(Enum):
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    CRITICAL = "critical"


@dataclass
class HealthAlert:
    """Health monitoring alert"""
    alert_id: str
    severity: AlertSeverity
    title: str
    message: str
    location: Location
    metric_name: str
    current_value: float
    threshold_value: float
    timestamp: timezone.datetime
    is_resolved: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'alert_id': self.alert_id,
            'severity': self.severity.value,
            'title': self.title,
            'message': self.message,
            'location_id': self.location.id,
            'location_name': self.location.name,
            'metric_name': self.metric_name,
            'current_value': self.current_value,
            'threshold_value': self.threshold_value,
            'timestamp': self.timestamp.isoformat(),
            'is_resolved': self.is_resolved
        }


class SystemMetricsCollector:
    """Collect system performance metrics"""
    
    def __init__(self):
        self.node_identity = NodeIdentity.get_current_node()
    
    def collect_system_metrics(self) -> Dict[str, float]:
        """Collect current system metrics"""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_percent = disk.percent
            disk_free_gb = disk.free / (1024**3)
            
            # Network metrics
            network_io = psutil.net_io_counters()
            network_bytes_sent = network_io.bytes_sent
            network_bytes_recv = network_io.bytes_recv
            
            return {
                'cpu_usage_percentage': cpu_percent,
                'cpu_count': cpu_count,
                'load_average': load_avg,
                'memory_usage_percentage': memory_percent,
                'memory_available_gb': memory_available_gb,
                'disk_usage_percentage': disk_percent,
                'disk_free_gb': disk_free_gb,
                'network_bytes_sent': network_bytes_sent,
                'network_bytes_recv': network_bytes_recv,
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return {}
    
    def collect_database_metrics(self) -> Dict[str, float]:
        """Collect database performance metrics"""
        try:
            start_time = time.time()
            
            # Test query performance
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                cursor.fetchone()
            
            query_time_ms = (time.time() - start_time) * 1000
            
            # Connection count (approximate)
            db_connections = len(connection.queries) if settings.DEBUG else 0
            
            return {
                'db_query_avg_time_ms': query_time_ms,
                'db_connection_count': db_connections,
            }
            
        except Exception as e:
            logger.error(f"Failed to collect database metrics: {e}")
            return {}
    
    def collect_application_metrics(self) -> Dict[str, float]:
        """Collect application-specific metrics"""
        try:
            from users.models import UserSession
            from sync.models import DataChangeLog
            
            # Active sessions
            active_sessions = UserSession.objects.filter(
                is_active=True,
                last_activity__gte=timezone.now() - timedelta(minutes=30)
            ).count()
            
            # Pending sync items
            pending_sync = DataChangeLog.objects.filter(
                is_synced=False,
                created_at__gte=timezone.now() - timedelta(hours=1)
            ).count()
            
            # Error rate (from cache)
            error_count = cache.get('error_count_last_hour', 0)
            total_requests = cache.get('request_count_last_hour', 1)
            error_rate = (error_count / total_requests) * 100
            
            # Sync lag
            sync_lag = self._calculate_sync_lag()
            
            return {
                'active_sessions': active_sessions,
                'pending_transactions': pending_sync,
                'error_rate_percentage': error_rate,
                'sync_lag_seconds': sync_lag,
            }
            
        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")
            return {}
    
    def _calculate_sync_lag(self) -> float:
        """Calculate sync lag in seconds"""
        try:
            from sync.models import LocationSyncLog
            
            latest_sync = LocationSyncLog.objects.filter(
                location=self.node_identity.location,
                status='success'
            ).order_by('-completed_at').first()
            
            if latest_sync and latest_sync.completed_at:
                lag = (timezone.now() - latest_sync.completed_at).total_seconds()
                return max(0, lag)
            
            return 0
            
        except Exception:
            return 0


class NetworkConnectivityMonitor:
    """Monitor network connectivity to other locations"""
    
    def __init__(self):
        self.node_identity = NodeIdentity.get_current_node()
    
    async def check_central_connectivity(self) -> Tuple[bool, float]:
        """Check connectivity to central server"""
        if self.node_identity.role == 'central':
            return True, 0.0
        
        if not self.node_identity.central_api_url:
            return False, float('inf')
        
        try:
            import aiohttp
            import time
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.node_identity.central_api_url}/health/",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    latency = (time.time() - start_time) * 1000  # ms
                    return response.status == 200, latency
                    
        except Exception as e:
            logger.warning(f"Central connectivity check failed: {e}")
            return False, float('inf')
    
    async def check_peer_connectivity(self) -> Dict[int, Tuple[bool, float]]:
        """Check connectivity to peer locations"""
        if not self.node_identity.location:
            return {}
        
        peer_connections = LocationMesh.objects.filter(
            location=self.node_identity.location
        )
        
        results = {}
        
        for peer_conn in peer_connections:
            try:
                is_connected, latency = await self._ping_peer(peer_conn.peer_location)
                results[peer_conn.peer_location.id] = (is_connected, latency)
                
                # Update mesh connection status
                peer_conn.update_connection_status(is_connected, latency)
                
            except Exception as e:
                logger.warning(f"Peer connectivity check failed for {peer_conn.peer_location.name}: {e}")
                results[peer_conn.peer_location.id] = (False, float('inf'))
        
        return results
    
    async def _ping_peer(self, peer_location: Location) -> Tuple[bool, float]:
        """Ping a peer location"""
        try:
            import aiohttp
            import time
            
            # Construct peer API URL (assuming same structure)
            peer_url = f"https://{peer_location.node_id}.teralinkxwaves.uk"
            
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{peer_url}/health/",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    latency = (time.time() - start_time) * 1000  # ms
                    return response.status == 200, latency
                    
        except Exception:
            return False, float('inf')


class HealthThresholdManager:
    """Manage health monitoring thresholds"""
    
    DEFAULT_THRESHOLDS = {
        'cpu_usage_percentage': {'warning': 80, 'critical': 95},
        'memory_usage_percentage': {'warning': 85, 'critical': 95},
        'disk_usage_percentage': {'warning': 85, 'critical': 95},
        'network_latency_ms': {'warning': 500, 'critical': 2000},
        'error_rate_percentage': {'warning': 5, 'critical': 15},
        'sync_lag_seconds': {'warning': 300, 'critical': 900},  # 5 min, 15 min
        'db_query_avg_time_ms': {'warning': 100, 'critical': 500},
        'active_sessions': {'warning': 80, 'critical': 95},  # % of max capacity
    }
    
    def __init__(self):
        self.thresholds = self._load_thresholds()
    
    def _load_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Load thresholds from cache or use defaults"""
        cached_thresholds = cache.get('health_thresholds')
        if cached_thresholds:
            return cached_thresholds
        
        return self.DEFAULT_THRESHOLDS.copy()
    
    def update_threshold(self, metric_name: str, level: str, value: float):
        """Update a specific threshold"""
        if metric_name not in self.thresholds:
            self.thresholds[metric_name] = {}
        
        self.thresholds[metric_name][level] = value
        cache.set('health_thresholds', self.thresholds, timeout=86400)
    
    def check_threshold(self, metric_name: str, value: float) -> Optional[AlertSeverity]:
        """Check if a metric value exceeds thresholds"""
        if metric_name not in self.thresholds:
            return None
        
        thresholds = self.thresholds[metric_name]
        
        if 'critical' in thresholds and value >= thresholds['critical']:
            return AlertSeverity.CRITICAL
        elif 'warning' in thresholds and value >= thresholds['warning']:
            return AlertSeverity.WARNING
        
        return None


class HealthMonitoringService:
    """Main health monitoring service"""
    
    def __init__(self):
        self.metrics_collector = SystemMetricsCollector()
        self.connectivity_monitor = NetworkConnectivityMonitor()
        self.threshold_manager = HealthThresholdManager()
        self.node_identity = NodeIdentity.get_current_node()
        self.active_alerts = {}  # alert_id -> HealthAlert
    
    async def start_monitoring(self):
        """Start the health monitoring service"""
        logger.info(f"Starting health monitoring for node {self.node_identity.node_id}")
        
        # Start monitoring tasks
        asyncio.create_task(self._system_metrics_monitor())
        asyncio.create_task(self._connectivity_monitor())
        asyncio.create_task(self._alert_processor())
        asyncio.create_task(self._health_reporter())
    
    async def _system_metrics_monitor(self):
        """Monitor system metrics continuously"""
        while True:
            try:
                # Collect all metrics
                system_metrics = self.metrics_collector.collect_system_metrics()
                db_metrics = self.metrics_collector.collect_database_metrics()
                app_metrics = self.metrics_collector.collect_application_metrics()
                
                all_metrics = {**system_metrics, **db_metrics, **app_metrics}
                
                # Record metrics
                if self.node_identity.location:
                    LocationHealthMetrics.record_metrics(
                        self.node_identity.location,
                        all_metrics
                    )
                
                # Check thresholds and generate alerts
                await self._check_metric_thresholds(all_metrics)
                
                # Update node health status
                await self._update_node_health_status(all_metrics)
                
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"System metrics monitoring error: {e}")
                await asyncio.sleep(60)
    
    async def _connectivity_monitor(self):
        """Monitor network connectivity"""
        while True:
            try:
                # Check central connectivity
                central_connected, central_latency = await self.connectivity_monitor.check_central_connectivity()
                
                # Update node identity
                self.node_identity.update_central_contact(success=central_connected)
                
                if not central_connected:
                    await self._generate_alert(
                        'central_connectivity',
                        AlertSeverity.CRITICAL,
                        "Central Server Unreachable",
                        f"Cannot reach central server at {self.node_identity.central_api_url}",
                        'network_latency_ms',
                        float('inf'),
                        2000
                    )
                
                # Check peer connectivity
                peer_results = await self.connectivity_monitor.check_peer_connectivity()
                
                for peer_id, (connected, latency) in peer_results.items():
                    if not connected:
                        peer_location = Location.objects.get(id=peer_id)
                        await self._generate_alert(
                            f'peer_connectivity_{peer_id}',
                            AlertSeverity.WARNING,
                            f"Peer Location Unreachable",
                            f"Cannot reach peer location {peer_location.name}",
                            'network_latency_ms',
                            latency,
                            2000
                        )
                
                await asyncio.sleep(120)  # Check every 2 minutes
                
            except Exception as e:
                logger.error(f"Connectivity monitoring error: {e}")
                await asyncio.sleep(120)
    
    async def _check_metric_thresholds(self, metrics: Dict[str, float]):
        """Check metrics against thresholds and generate alerts"""
        for metric_name, value in metrics.items():
            severity = self.threshold_manager.check_threshold(metric_name, value)
            
            if severity:
                threshold_value = self.threshold_manager.thresholds[metric_name][severity.value]
                
                await self._generate_alert(
                    f'{metric_name}_threshold',
                    severity,
                    f"{metric_name.replace('_', ' ').title()} Alert",
                    f"{metric_name} is {value:.2f}, exceeding {severity.value} threshold of {threshold_value}",
                    metric_name,
                    value,
                    threshold_value
                )
    
    async def _generate_alert(
        self,
        alert_id: str,
        severity: AlertSeverity,
        title: str,
        message: str,
        metric_name: str,
        current_value: float,
        threshold_value: float
    ):
        """Generate a health alert"""
        
        # Check if alert already exists and is not resolved
        if alert_id in self.active_alerts and not self.active_alerts[alert_id].is_resolved:
            return
        
        alert = HealthAlert(
            alert_id=alert_id,
            severity=severity,
            title=title,
            message=message,
            location=self.node_identity.location or Location.objects.filter(is_central=True).first(),
            metric_name=metric_name,
            current_value=current_value,
            threshold_value=threshold_value,
            timestamp=timezone.now()
        )
        
        self.active_alerts[alert_id] = alert
        
        # Send alert
        await self._send_alert(alert)
        
        logger.warning(f"Health alert generated: {alert.title} - {alert.message}")
    
    async def _send_alert(self, alert: HealthAlert):
        """Send alert via configured channels"""
        try:
            # Email alert
            if hasattr(settings, 'HEALTH_ALERT_EMAIL') and settings.HEALTH_ALERT_EMAIL:
                await self._send_email_alert(alert)
            
            # Slack alert (if configured)
            if hasattr(settings, 'SLACK_WEBHOOK_URL') and settings.SLACK_WEBHOOK_URL:
                await self._send_slack_alert(alert)
            
            # Store alert in database
            await self._store_alert(alert)
            
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    async def _send_email_alert(self, alert: HealthAlert):
        """Send email alert"""
        try:
            subject = f"[{alert.severity.value.upper()}] {alert.title}"
            message = f"""Health Alert Details:

Location: {alert.location.name}
Severity: {alert.severity.value.upper()}
Metric: {alert.metric_name}
Current Value: {alert.current_value}
Threshold: {alert.threshold_value}
Time: {alert.timestamp}

Message: {alert.message}

Node: {self.node_identity.node_id}
"""
            
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [settings.HEALTH_ALERT_EMAIL],
                fail_silently=False
            )
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")\n    \n    async def _send_slack_alert(self, alert: HealthAlert):\n        \"\"\"Send Slack alert\"\"\"\n        try:\n            import aiohttp\n            \n            color = {\n                AlertSeverity.INFO: \"good\",\n                AlertSeverity.WARNING: \"warning\", \n                AlertSeverity.CRITICAL: \"danger\",\n                AlertSeverity.EMERGENCY: \"danger\"\n            }.get(alert.severity, \"warning\")\n            \n            payload = {\n                \"attachments\": [{\n                    \"color\": color,\n                    \"title\": alert.title,\n                    \"text\": alert.message,\n                    \"fields\": [\n                        {\"title\": \"Location\", \"value\": alert.location.name, \"short\": True},\n                        {\"title\": \"Severity\", \"value\": alert.severity.value.upper(), \"short\": True},\n                        {\"title\": \"Metric\", \"value\": alert.metric_name, \"short\": True},\n                        {\"title\": \"Value\", \"value\": f\"{alert.current_value:.2f}\", \"short\": True},\n                    ],\n                    \"timestamp\": alert.timestamp.timestamp()\n                }]\n            }\n            \n            async with aiohttp.ClientSession() as session:\n                async with session.post(\n                    settings.SLACK_WEBHOOK_URL,\n                    json=payload\n                ) as response:\n                    if response.status != 200:\n                        logger.error(f\"Slack alert failed: {response.status}\")\n                        \n        except Exception as e:\n            logger.error(f\"Failed to send Slack alert: {e}\")\n    \n    async def _store_alert(self, alert: HealthAlert):\n        \"\"\"Store alert in database for history\"\"\"\n        try:\n            # Store in cache for immediate access\n            cache_key = f\"health_alert:{alert.alert_id}\"\n            cache.set(cache_key, alert.to_dict(), timeout=86400)\n            \n            # Could also store in database table if needed\n            \n        except Exception as e:\n            logger.error(f\"Failed to store alert: {e}\")\n    \n    async def _update_node_health_status(self, metrics: Dict[str, float]):\n        \"\"\"Update overall node health status\"\"\"\n        try:\n            # Calculate overall health score\n            health_score = self._calculate_health_score(metrics)\n            \n            # Determine health status\n            if health_score >= 90:\n                status = HealthStatus.EXCELLENT\n            elif health_score >= 75:\n                status = HealthStatus.GOOD\n            elif health_score >= 50:\n                status = HealthStatus.FAIR\n            elif health_score >= 25:\n                status = HealthStatus.POOR\n            else:\n                status = HealthStatus.CRITICAL\n            \n            # Update node identity\n            if hasattr(self.node_identity, 'health_status'):\n                self.node_identity.health_status = status.value\n                self.node_identity.save()\n            \n            # Update location health\n            if self.node_identity.location:\n                self.node_identity.location.update_health_status()\n                \n        except Exception as e:\n            logger.error(f\"Failed to update health status: {e}\")\n    \n    def _calculate_health_score(self, metrics: Dict[str, float]) -> float:\n        \"\"\"Calculate overall health score (0-100)\"\"\"\n        try:\n            scores = []\n            weights = {\n                'cpu_usage_percentage': 0.2,\n                'memory_usage_percentage': 0.2,\n                'disk_usage_percentage': 0.15,\n                'error_rate_percentage': 0.2,\n                'sync_lag_seconds': 0.15,\n                'db_query_avg_time_ms': 0.1\n            }\n            \n            for metric, weight in weights.items():\n                if metric in metrics:\n                    value = metrics[metric]\n                    \n                    # Convert to score (higher is worse for these metrics)\n                    if metric == 'sync_lag_seconds':\n                        score = max(0, 100 - (value / 10))  # 1000s = 0 score\n                    elif metric == 'db_query_avg_time_ms':\n                        score = max(0, 100 - (value / 5))   # 500ms = 0 score\n                    else:\n                        score = max(0, 100 - value)         # percentage metrics\n                    \n                    scores.append(score * weight)\n            \n            return sum(scores) if scores else 50  # Default to fair if no metrics\n            \n        except Exception as e:\n            logger.error(f\"Failed to calculate health score: {e}\")\n            return 50\n    \n    async def _alert_processor(self):\n        \"\"\"Process and manage active alerts\"\"\"\n        while True:\n            try:\n                # Check for resolved alerts\n                resolved_alerts = []\n                \n                for alert_id, alert in self.active_alerts.items():\n                    if await self._is_alert_resolved(alert):\n                        alert.is_resolved = True\n                        resolved_alerts.append(alert_id)\n                        \n                        # Send resolution notification\n                        await self._send_resolution_notification(alert)\n                \n                # Remove resolved alerts\n                for alert_id in resolved_alerts:\n                    del self.active_alerts[alert_id]\n                \n                await asyncio.sleep(300)  # Check every 5 minutes\n                \n            except Exception as e:\n                logger.error(f\"Alert processor error: {e}\")\n                await asyncio.sleep(300)\n    \n    async def _is_alert_resolved(self, alert: HealthAlert) -> bool:\n        \"\"\"Check if an alert condition has been resolved\"\"\"\n        try:\n            # Get current metric value\n            if alert.metric_name == 'network_latency_ms':\n                if 'central_connectivity' in alert.alert_id:\n                    connected, _ = await self.connectivity_monitor.check_central_connectivity()\n                    return connected\n                else:\n                    # Peer connectivity check would go here\n                    return False\n            else:\n                # Get latest metrics\n                if alert.metric_name in ['cpu_usage_percentage', 'memory_usage_percentage']:\n                    current_metrics = self.metrics_collector.collect_system_metrics()\n                elif alert.metric_name.startswith('db_'):\n                    current_metrics = self.metrics_collector.collect_database_metrics()\n                else:\n                    current_metrics = self.metrics_collector.collect_application_metrics()\n                \n                if alert.metric_name in current_metrics:\n                    current_value = current_metrics[alert.metric_name]\n                    return current_value < alert.threshold_value\n            \n            return False\n            \n        except Exception as e:\n            logger.error(f\"Failed to check alert resolution: {e}\")\n            return False\n    \n    async def _send_resolution_notification(self, alert: HealthAlert):\n        \"\"\"Send notification when alert is resolved\"\"\"\n        try:\n            resolution_message = f\"RESOLVED: {alert.title} - The issue has been resolved.\"\n            logger.info(resolution_message)\n            \n            # Could send email/Slack notification here\n            \n        except Exception as e:\n            logger.error(f\"Failed to send resolution notification: {e}\")\n    \n    async def _health_reporter(self):\n        \"\"\"Generate periodic health reports\"\"\"\n        while True:\n            try:\n                await asyncio.sleep(3600)  # Every hour\n                await self._generate_health_report()\n                \n            except Exception as e:\n                logger.error(f\"Health reporter error: {e}\")\n                await asyncio.sleep(3600)\n    \n    async def _generate_health_report(self):\n        \"\"\"Generate and send health report\"\"\"\n        try:\n            # Collect summary metrics\n            report_data = {\n                'node_id': self.node_identity.node_id,\n                'timestamp': timezone.now().isoformat(),\n                'active_alerts': len(self.active_alerts),\n                'critical_alerts': len([a for a in self.active_alerts.values() if a.severity == AlertSeverity.CRITICAL]),\n                'location': self.node_identity.location.name if self.node_identity.location else 'Central',\n            }\n            \n            # Store report\n            cache.set(f\"health_report:{self.node_identity.node_id}\", report_data, timeout=86400)\n            \n            logger.info(f\"Health report generated: {report_data}\")\n            \n        except Exception as e:\n            logger.error(f\"Failed to generate health report: {e}\")\n\n\n# Global health monitoring service\nhealth_monitor = HealthMonitoringService()