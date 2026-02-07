# apps/sync/radius_sync.py
"""
Sync voucher usage from FreeRADIUS via Radius API
"""
import logging
import requests
from django.conf import settings
from packages.models import DispatchVoucher

logger = logging.getLogger(__name__)

RADIUS_API_URL = getattr(settings, 'RADIUS_API_URL', 'http://localhost:8010/api')
BATCH_SIZE = 100


class RadiusUsageSyncService:
    """Service to sync voucher usage from FreeRADIUS"""
    
    @staticmethod
    def sync_single_voucher(voucher_code):
        """Sync usage for a single voucher"""
        try:
            response = requests.get(
                f'{RADIUS_API_URL}/vouchers/usage/',
                params={'username': voucher_code},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data
                }
            else:
                logger.error(f"Failed to get usage for {voucher_code}: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.RequestException as e:
            logger.error(f"Request error for {voucher_code}: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def sync_batch_vouchers(voucher_codes):
        """Sync usage for multiple vouchers in one request"""
        try:
            response = requests.post(
                f'{RADIUS_API_URL}/vouchers/usage/batch/',
                json={'usernames': voucher_codes},
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'results': data.get('results', [])
                }
            else:
                logger.error(f"Batch sync failed: {response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
                
        except requests.RequestException as e:
            logger.error(f"Batch request error: {e}")
            return {'success': False, 'error': str(e)}
    
    @staticmethod
    def update_voucher_from_usage(voucher, usage_data):
        """Update DispatchVoucher model with usage data"""
        try:
            voucher.download_bytes = usage_data.get('total_downloaded', 0)
            voucher.upload_bytes = usage_data.get('total_uploaded', 0)
            voucher.session_count = usage_data.get('total_sessions', 0)
            voucher.concurrent_sessions = usage_data.get('active_sessions', 0)
            
            # Update status if data exhausted
            voucher.update_status()
            
            voucher.save(update_fields=[
                'download_bytes', 
                'upload_bytes', 
                'session_count',
                'concurrent_sessions',
                'status'
            ])
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update voucher {voucher.voucher_code}: {e}")
            return False
    
    @classmethod
    def sync_active_vouchers(cls):
        """Sync all active vouchers"""
        active_vouchers = DispatchVoucher.objects.filter(status='active')
        total = active_vouchers.count()
        
        if total == 0:
            logger.info("No active vouchers to sync")
            return {'synced': 0, 'failed': 0, 'total': 0}
        
        logger.info(f"Syncing {total} active vouchers")
        
        synced = 0
        failed = 0
        
        # Process in batches
        voucher_list = list(active_vouchers)
        for i in range(0, len(voucher_list), BATCH_SIZE):
            batch = voucher_list[i:i + BATCH_SIZE]
            voucher_codes = [v.voucher_code for v in batch]
            
            # Batch API call
            result = cls.sync_batch_vouchers(voucher_codes)
            
            if result['success']:
                # Update each voucher
                usage_map = {r['username']: r for r in result['results']}
                
                for voucher in batch:
                    usage_data = usage_map.get(voucher.voucher_code)
                    if usage_data:
                        if cls.update_voucher_from_usage(voucher, usage_data):
                            synced += 1
                        else:
                            failed += 1
            else:
                failed += len(batch)
                logger.error(f"Batch sync failed for {len(batch)} vouchers")
        
        logger.info(f"Sync complete: {synced} synced, {failed} failed, {total} total")
        return {'synced': synced, 'failed': failed, 'total': total}
    
    @classmethod
    def sync_critical_vouchers(cls):
        """Sync vouchers near data limit (>80% used)"""
        # Get vouchers with data limits
        vouchers = DispatchVoucher.objects.filter(
            status='active',
            package__data_limit_mb__isnull=False
        )
        
        critical_vouchers = []
        for voucher in vouchers:
            if voucher.package.data_limit_mb:
                total_used = voucher.download_bytes + voucher.upload_bytes
                limit_bytes = voucher.package.data_limit_mb * 1024 * 1024
                usage_percent = (total_used / limit_bytes) * 100 if limit_bytes > 0 else 0
                
                if usage_percent >= 80:
                    critical_vouchers.append(voucher)
        
        if not critical_vouchers:
            logger.info("No critical vouchers to sync")
            return {'synced': 0, 'failed': 0, 'total': 0}
        
        logger.info(f"Syncing {len(critical_vouchers)} critical vouchers")
        
        synced = 0
        failed = 0
        
        # Process in batches
        for i in range(0, len(critical_vouchers), BATCH_SIZE):
            batch = critical_vouchers[i:i + BATCH_SIZE]
            voucher_codes = [v.voucher_code for v in batch]
            
            result = cls.sync_batch_vouchers(voucher_codes)
            
            if result['success']:
                usage_map = {r['username']: r for r in result['results']}
                
                for voucher in batch:
                    usage_data = usage_map.get(voucher.voucher_code)
                    if usage_data:
                        if cls.update_voucher_from_usage(voucher, usage_data):
                            synced += 1
                        else:
                            failed += 1
            else:
                failed += len(batch)
        
        logger.info(f"Critical sync complete: {synced} synced, {failed} failed")
        return {'synced': synced, 'failed': failed, 'total': len(critical_vouchers)}
