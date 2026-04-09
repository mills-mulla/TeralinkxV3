"""
TimescaleDB Dual-Write Router
Gradually routes finance queries to TimescaleDB hypertables based on FeatureFlag rollout.
"""
import hashlib
from django.conf import settings
from core.models import FeatureFlag


class TimescaleDBRouter:
    """
    Routes finance app queries to TimescaleDB hypertables when feature flag is enabled.
    Uses consistent hashing for stable rollout based on user/transaction ID.
    """
    
    TIMESCALE_MODELS = {'paymenttransaction', 'transactionqueue'}
    FINANCE_APP = 'finance'
    
    def db_for_read(self, model, **hints):
        """Route reads to TimescaleDB if feature enabled for this entity."""
        if model._meta.app_label == self.FINANCE_APP:
            model_name = model._meta.model_name
            if model_name in self.TIMESCALE_MODELS:
                if self._should_use_timescale(hints):
                    return 'timescale'
        return None
    
    def db_for_write(self, model, **hints):
        """Route writes to TimescaleDB if feature enabled for this entity."""
        if model._meta.app_label == self.FINANCE_APP:
            model_name = model._meta.model_name
            if model_name in self.TIMESCALE_MODELS:
                if self._should_use_timescale(hints):
                    return 'timescale'
        return None
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations within same database."""
        if obj1._meta.app_label == self.FINANCE_APP or obj2._meta.app_label == self.FINANCE_APP:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Prevent migrations on timescale db - managed manually."""
        if db == 'timescale':
            return False
        return None
    
    def _should_use_timescale(self, hints):
        """Determine if query should use TimescaleDB based on feature flag."""
        try:
            flag = FeatureFlag.objects.using('default').get(name='timescaledb_migration')
            if not flag.enabled:
                return False
            
            # 100% rollout - use for everyone
            if flag.rollout_percentage >= 100:
                return True
            
            # 0% rollout - use for no one
            if flag.rollout_percentage <= 0:
                return False
            
            # Partial rollout - use consistent hashing
            entity_id = self._extract_entity_id(hints)
            if entity_id:
                return flag.is_enabled_for(entity_id)
            
            # No entity ID - default to PostgreSQL
            return False
            
        except FeatureFlag.DoesNotExist:
            return False
        except Exception:
            # On error, default to PostgreSQL
            return False
    
    def _extract_entity_id(self, hints):
        """Extract entity ID from query hints for consistent hashing."""
        # Try to get instance ID
        instance = hints.get('instance')
        if instance and hasattr(instance, 'id'):
            return str(instance.id)
        
        # Try to get from exact lookup
        exact = hints.get('exact')
        if exact:
            return str(exact)
        
        # Try to get from pk lookup
        pk = hints.get('pk_set')
        if pk:
            return str(sorted(pk)[0])
        
        return None
