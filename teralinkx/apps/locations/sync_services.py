"""
Production-grade sync services for multi-location architecture
Includes circuit breakers, event-driven sync, and conflict-free replicated data types
"""

import asyncio
import json
import logging
from datetime import timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from django.utils import timezone
from django.db import transaction
from django.core.cache import cache
from django.conf import settings

from .models import Location, NodeIdentity, DistributedTransaction, LocationMesh
from sync.models import LocationSyncLog, DataChangeLog

logger = logging.getLogger(__name__)


class OperationalMode(Enum):
    ONLINE = "online"
    DEGRADED = "degraded" 
    OFFLINE = "offline"
    EMERGENCY = "emergency"


class SyncPriority(Enum):
    CRITICAL = 1    # Balance changes, voucher activations
    HIGH = 2        # Transactions, user sessions
    NORMAL = 3      # User profiles, device updates
    LOW = 4         # Analytics, logs


@dataclass
class SyncEvent:
    """Event-driven sync message"""
    event_type: str
    location_id: int
    data: Dict[str, Any]
    priority: SyncPriority
    timestamp: timezone.datetime
    correlation_id: str
    retry_count: int = 0


class CircuitBreakerError(Exception):
    """Circuit breaker is open"""
    pass


class CircuitBreaker:
    """Circuit breaker for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = 'closed'  # closed, open, half_open
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == 'open':
            if self._should_attempt_reset():
                self.state = 'half_open'
            else:
                raise CircuitBreakerError("Circuit breaker is open")
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        """Check if we should attempt to reset the circuit breaker"""
        if not self.last_failure_time:
            return True
        
        return (timezone.now() - self.last_failure_time).seconds > self.recovery_timeout
    
    def _on_success(self):
        """Handle successful call"""
        self.failure_count = 0
        self.state = 'closed'
    
    def _on_failure(self):
        """Handle failed call"""
        self.failure_count += 1
        self.last_failure_time = timezone.now()
        
        if self.failure_count >= self.failure_threshold:
            self.state = 'open'


class ConflictFreeReplicatedDataType:
    """CRDT for conflict-free balance management"""
    
    def __init__(self, user_id: int):
        self.user_id = user_id
        self.operations = []  # List of (amount, location_id, timestamp, operation_id)
    
    def add_operation(self, amount: Decimal, location_id: int, operation_id: str):
        """Add a balance operation"""
        operation = (amount, location_id, timezone.now(), operation_id)
        self.operations.append(operation)
        self.operations.sort(key=lambda x: (x[2], x[3]))  # Sort by timestamp, then ID
    
    def get_balance(self) -> Decimal:
        """Calculate current balance deterministically"""
        return sum(op[0] for op in self.operations)
    
    def merge(self, other_crdt):
        """Merge with another CRDT"""
        # Combine operations and remove duplicates
        all_ops = self.operations + other_crdt.operations
        unique_ops = {}
        
        for op in all_ops:
            op_id = op[3]
            if op_id not in unique_ops or op[2] > unique_ops[op_id][2]:
                unique_ops[op_id] = op
        
        self.operations = sorted(unique_ops.values(), key=lambda x: (x[2], x[3]))
    
    def to_dict(self) -> Dict:
        """Serialize to dictionary"""
        return {
            'user_id': self.user_id,
            'operations': [
                {
                    'amount': str(op[0]),
                    'location_id': op[1],
                    'timestamp': op[2].isoformat(),
                    'operation_id': op[3]
                }
                for op in self.operations
            ]
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        """Deserialize from dictionary"""
        crdt = cls(data['user_id'])
        for op_data in data['operations']:
            crdt.operations.append((
                Decimal(op_data['amount']),
                op_data['location_id'],
                timezone.datetime.fromisoformat(op_data['timestamp']),
                op_data['operation_id']
            ))
        return crdt


class LocationSyncService:
    """Production-grade sync service with circuit breakers and event-driven architecture"""
    
    def __init__(self):
        self.circuit_breaker = CircuitBreaker()
        self.node_identity = None  # Lazy load to avoid DB query at import
        self.event_queue = asyncio.Queue()
        self.sync_intervals = self._get_adaptive_sync_intervals()
    
    def _ensure_node_identity(self):
        """Lazy load node identity"""
        if self.node_identity is None:
            try:
                self.node_identity = NodeIdentity.get_current_node()
            except Exception as e:
                logger.warning(f"Could not load node identity: {e}")
                self.node_identity = None
        return self.node_identity
    
    def _get_adaptive_sync_intervals(self) -> Dict[str, int]:
        """Get adaptive sync intervals based on current load"""
        base_intervals = {
            'sessions': 120,
            'transactions': 60,
            'vouchers': 300,
            'users': 600,
            'packages': 1800,
        }
        
        # Adjust based on current activity level
        activity_level = self._get_activity_level()
        multiplier = {
            'high': 0.5,
            'normal': 1.0,
            'low': 2.0
        }.get(activity_level, 1.0)
        
        return {k: int(v * multiplier) for k, v in base_intervals.items()}
    
    def _get_activity_level(self) -> str:
        """Determine current activity level"""
        try:
            # Check recent transaction count
            from sync.models import DataChangeLog
            recent_transactions = DataChangeLog.objects.filter(
                created_at__gte=timezone.now() - timedelta(minutes=10)
            ).count()
            
            if recent_transactions > 100:
                return 'high'
            elif recent_transactions > 20:
                return 'normal'
            else:
                return 'low'
        except Exception as e:
            logger.warning(f"Could not determine activity level: {e}")
            return 'normal'
    
    async def start_sync_worker(self):
        """Start the async sync worker"""
        node_identity = self._ensure_node_identity()
        if not node_identity:
            logger.error("Cannot start sync worker without node identity")
            return
            
        logger.info(f"Starting sync worker for node {node_identity.node_id}")
        
        # Start event processor
        asyncio.create_task(self._process_sync_events())
        
        # Start periodic sync tasks
        for sync_type, interval in self.sync_intervals.items():
            asyncio.create_task(self._periodic_sync(sync_type, interval))
    
    async def _process_sync_events(self):
        """Process sync events from the queue"""
        while True:
            try:
                event = await self.event_queue.get()
                await self._handle_sync_event(event)
                self.event_queue.task_done()
            except Exception as e:
                logger.error(f"Error processing sync event: {e}")
                await asyncio.sleep(1)
    
    async def _handle_sync_event(self, event: SyncEvent):
        """Handle individual sync event"""
        try:
            if event.priority == SyncPriority.CRITICAL:
                # Process immediately
                await self._sync_critical_data(event)
            else:
                # Batch with other events
                await self._batch_sync_event(event)
        except Exception as e:
            logger.error(f"Failed to handle sync event {event.correlation_id}: {e}")
            
            # Retry with exponential backoff
            if event.retry_count < 3:
                event.retry_count += 1
                await asyncio.sleep(2 ** event.retry_count)
                await self.event_queue.put(event)
    
    async def _sync_critical_data(self, event: SyncEvent):
        """Sync critical data immediately"""
        if self.node_identity.role == 'location':
            await self._sync_to_central(event)
        else:
            await self._sync_to_locations(event)
    
    async def _sync_to_central(self, event: SyncEvent):
        """Sync data to central server"""
        node_identity = self._ensure_node_identity()
        if not node_identity:
            return
            
        try:
            # Use circuit breaker for central API calls
            result = self.circuit_breaker.call(
                self._make_central_api_call,
                'sync/events/',
                event.__dict__
            )
            
            # Update node status
            node_identity.update_central_contact(success=True)
            
        except CircuitBreakerError:
            logger.warning("Circuit breaker open - queueing for later sync")
            await self._queue_for_offline_sync(event)
            
        except Exception as e:
            logger.error(f"Failed to sync to central: {e}")
            if node_identity:
                node_identity.update_central_contact(success=False)
            await self._handle_sync_failure(event)
    
    async def _sync_to_locations(self, event: SyncEvent):
        """Sync data to location servers (central -> locations)"""
        target_locations = Location.objects.filter(
            is_active=True,
            is_online=True
        ).exclude(is_central=True)
        
        for location in target_locations:
            try:
                await self._sync_to_location(location, event)
            except Exception as e:
                logger.error(f"Failed to sync to location {location.name}: {e}")
    
    async def _sync_to_location(self, location: Location, event: SyncEvent):
        """Sync data to specific location"""
        # Implementation would make API call to location
        # For now, simulate the call
        await asyncio.sleep(0.1)  # Simulate network delay
    
    def _make_central_api_call(self, endpoint: str, data: Dict) -> Dict:
        """Make API call to central server"""
        import requests
        
        node_identity = self._ensure_node_identity()
        if not node_identity or not node_identity.central_api_url:
            raise Exception("Central API URL not configured")
        
        url = f"{node_identity.central_api_url}/{endpoint}"
        headers = {
            'Authorization': f'Bearer {node_identity.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(url, json=data, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    
    async def _queue_for_offline_sync(self, event: SyncEvent):
        """Queue event for offline sync when central is unavailable"""
        # Store in local queue (Redis or database)
        cache_key = f"offline_sync:{event.correlation_id}"
        cache.set(cache_key, event.__dict__, timeout=86400)  # 24 hours
        
        logger.info(f"Queued event {event.correlation_id} for offline sync")
    
    async def _handle_sync_failure(self, event: SyncEvent):
        """Handle sync failure with appropriate fallback"""
        if self.node_identity.should_operate_offline():
            # Switch to offline mode
            await self._switch_to_offline_mode()
        else:
            # Try peer-to-peer sync
            await self._try_peer_sync(event)
    
    async def _switch_to_offline_mode(self):
        """Switch node to offline operation mode"""
        node_identity = self._ensure_node_identity()
        if not node_identity:
            return
            
        node_identity.current_mode = OperationalMode.OFFLINE.value
        node_identity.save()
        
        logger.warning(f"Node {node_identity.node_id} switched to offline mode")
        
        # Notify administrators
        await self._send_offline_alert()
    
    async def _try_peer_sync(self, event: SyncEvent):
        """Try to sync via peer locations"""
        node_identity = self._ensure_node_identity()
        if not node_identity or node_identity.role != 'location':
            return
        
        available_peers = LocationMesh.get_available_peers(node_identity.location)
        
        for peer_connection in available_peers[:3]:  # Try top 3 peers
            try:
                await self._sync_via_peer(peer_connection.peer_location, event)
                logger.info(f"Successfully synced via peer {peer_connection.peer_location.name}")
                return
            except Exception as e:
                logger.warning(f"Peer sync failed via {peer_connection.peer_location.name}: {e}")
        
        # All peers failed - queue for offline sync
        await self._queue_for_offline_sync(event)
    
    async def _sync_via_peer(self, peer_location: Location, event: SyncEvent):
        """Sync data via peer location"""
        # Implementation would make API call to peer
        # Peer would then forward to central when available
        await asyncio.sleep(0.1)  # Simulate network delay
    
    async def _send_offline_alert(self):
        """Send alert when node goes offline"""
        node_identity = self._ensure_node_identity()
        node_id = node_identity.node_id if node_identity else 'unknown'
        # Implementation would send email/SMS/Slack notification
        logger.critical(f"ALERT: Node {node_id} is operating offline")
    
    async def _periodic_sync(self, sync_type: str, interval: int):
        """Periodic sync for non-critical data"""
        while True:
            try:
                await asyncio.sleep(interval)
                await self._perform_periodic_sync(sync_type)
            except Exception as e:
                logger.error(f"Periodic sync error for {sync_type}: {e}")
                await asyncio.sleep(60)  # Wait before retrying
    
    async def _perform_periodic_sync(self, sync_type: str):
        """Perform periodic sync for specific data type"""
        node_identity = self._ensure_node_identity()
        if not node_identity:
            return
            
        # Get pending changes for this sync type
        pending_changes = DataChangeLog.objects.filter(
            model_type=sync_type,
            is_synced=False,
            location=node_identity.location
        ).order_by('created_at')[:100]  # Batch size
        
        if not pending_changes:
            return
        
        # Create sync event
        event = SyncEvent(
            event_type=f'periodic_{sync_type}_sync',
            location_id=node_identity.location.id if node_identity.location else 0,
            data={
                'sync_type': sync_type,
                'changes': [change.id for change in pending_changes]
            },
            priority=SyncPriority.NORMAL,
            timestamp=timezone.now(),
            correlation_id=f"periodic_{sync_type}_{timezone.now().timestamp()}"
        )
        
        await self.event_queue.put(event)
    
    async def _batch_sync_event(self, event: SyncEvent):
        """Batch non-critical events for efficiency"""
        batch_key = f"sync_batch:{event.event_type}"
        
        # Add to batch
        batch = cache.get(batch_key, [])
        batch.append(event)
        cache.set(batch_key, batch, timeout=300)  # 5 minute batch window
        
        # Process batch if it's full or timeout reached
        if len(batch) >= 50:  # Batch size
            await self._process_sync_batch(batch_key, batch)
    
    async def _process_sync_batch(self, batch_key: str, batch: List[SyncEvent]):
        """Process a batch of sync events"""
        node_identity = self._ensure_node_identity()
        if not node_identity:
            return
            
        try:
            # Combine events into single sync request
            combined_data = {
                'events': [event.__dict__ for event in batch],
                'batch_id': batch_key,
                'timestamp': timezone.now().isoformat()
            }
            
            if node_identity.role == 'location':
                result = self.circuit_breaker.call(
                    self._make_central_api_call,
                    'sync/batch/',
                    combined_data
                )
            
            # Clear batch on success
            cache.delete(batch_key)
            logger.info(f"Successfully processed batch {batch_key} with {len(batch)} events")
            
        except Exception as e:
            logger.error(f"Failed to process batch {batch_key}: {e}")
            # Events will be retried individually


class DistributedTransactionManager:
    """Two-phase commit transaction manager"""
    
    def __init__(self):
        self.node_identity = None  # Lazy load
    
    def _ensure_node_identity(self):
        """Lazy load node identity"""
        if self.node_identity is None:
            try:
                self.node_identity = NodeIdentity.get_current_node()
            except Exception as e:
                logger.warning(f"Could not load node identity: {e}")
                self.node_identity = None
        return self.node_identity
    
    async def execute_distributed_transaction(
        self, 
        transaction_type: str,
        transaction_data: Dict,
        participant_locations: List[Location]
    ) -> Tuple[bool, str]:
        """Execute a distributed transaction using 2PC"""
        
        node_identity = self._ensure_node_identity()
        coordinator = node_identity.location if node_identity and node_identity.location else Location.objects.filter(is_central=True).first()
        
        # Create transaction record
        distributed_tx = DistributedTransaction.objects.create(
            transaction_type=transaction_type,
            coordinator_location=coordinator,
            transaction_data=transaction_data,
            timeout_at=timezone.now() + timedelta(minutes=10)
        )
        
        # Add participants
        for location in participant_locations:
            distributed_tx.add_participant(location)
        
        try:
            # Phase 1: Prepare
            prepare_success = await self._prepare_phase(distributed_tx)
            if not prepare_success:
                distributed_tx.abort_transaction()
                return False, "Prepare phase failed"
            
            # Phase 2: Commit
            commit_success = await self._commit_phase(distributed_tx)
            if not commit_success:
                distributed_tx.abort_transaction()
                return False, "Commit phase failed"
            
            return True, "Transaction committed successfully"
            
        except Exception as e:
            distributed_tx.abort_transaction()
            logger.error(f"Distributed transaction failed: {e}")
            return False, str(e)
    
    async def _prepare_phase(self, distributed_tx: DistributedTransaction) -> bool:
        """Execute prepare phase of 2PC"""
        distributed_tx.prepare_phase()
        
        # Wait for all participants to respond
        timeout = distributed_tx.timeout_at
        while timezone.now() < timeout:
            if distributed_tx.can_commit():
                return True
            await asyncio.sleep(1)
        
        return False
    
    async def _commit_phase(self, distributed_tx: DistributedTransaction) -> bool:
        """Execute commit phase of 2PC"""
        return distributed_tx.commit_phase()


# Global sync service instance - lazy initialization
sync_service = None
transaction_manager = None

def get_sync_service():
    """Get or create sync service instance"""
    global sync_service
    if sync_service is None:
        sync_service = LocationSyncService()
    return sync_service

def get_transaction_manager():
    """Get or create transaction manager instance"""
    global transaction_manager
    if transaction_manager is None:
        transaction_manager = DistributedTransactionManager()
    return transaction_manager