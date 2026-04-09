"""
Production-grade roaming service for multi-location voucher management
Handles roaming validation, pricing, conflict resolution, and distributed voucher activation
"""

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

from .models import Location, NodeIdentity, DistributedTransaction
from .sync_services import get_sync_service, get_transaction_manager, ConflictFreeReplicatedDataType
from users.models import ClientH
from packages.models import DispatchVoucher, PackageType

logger = logging.getLogger(__name__)


class RoamingError(Exception):
    """Base exception for roaming errors"""
    pass


class RoamingValidationError(RoamingError):
    """Roaming validation failed"""
    pass


class RoamingPricingError(RoamingError):
    """Roaming pricing calculation failed"""
    pass


class RoamingActivationError(RoamingError):
    """Roaming voucher activation failed"""
    pass


@dataclass
class RoamingValidationResult:
    """Result of roaming validation"""
    is_valid: bool
    error_message: str = ""
    warnings: List[str] = None
    pricing_info: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.warnings is None:
            self.warnings = []


@dataclass
class RoamingPricingInfo:
    """Roaming pricing information"""
    base_price: Decimal
    roaming_multiplier: Decimal
    roaming_surcharge: Decimal
    total_price: Decimal
    currency: str = "KES"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'base_price': str(self.base_price),
            'roaming_multiplier': str(self.roaming_multiplier),
            'roaming_surcharge': str(self.roaming_surcharge),
            'total_price': str(self.total_price),
            'currency': self.currency
        }


class RoamingValidator:
    """Comprehensive roaming validation service"""
    
    def __init__(self):
        self.node_identity = NodeIdentity.get_current_node()
    
    def validate_roaming_voucher(
        self, 
        voucher: DispatchVoucher, 
        current_location: Location,
        user: ClientH = None
    ) -> RoamingValidationResult:
        """Comprehensive roaming voucher validation"""
        
        try:
            # Basic voucher validation
            basic_validation = self._validate_basic_voucher(voucher)
            if not basic_validation.is_valid:
                return basic_validation
            
            # Location validation
            location_validation = self._validate_location_roaming(
                voucher.home_location, current_location
            )
            if not location_validation.is_valid:
                return location_validation
            
            # Package validation
            package_validation = self._validate_package_roaming(voucher.package)
            if not package_validation.is_valid:
                return package_validation
            
            # User validation
            if user:
                user_validation = self._validate_user_roaming(user, current_location)
                if not user_validation.is_valid:
                    return user_validation
            
            # Time-based validation
            time_validation = self._validate_roaming_time_restrictions(current_location)
            if not time_validation.is_valid:
                return time_validation
            
            # Concurrent roaming validation
            concurrent_validation = self._validate_concurrent_roaming(voucher, current_location)
            if not concurrent_validation.is_valid:
                return concurrent_validation
            
            # Calculate pricing
            pricing_info = self._calculate_roaming_pricing(voucher, current_location)
            
            # Balance validation
            if user:
                balance_validation = self._validate_user_balance(user, pricing_info.total_price)
                if not balance_validation.is_valid:
                    return balance_validation
            
            # Capacity validation
            capacity_validation = self._validate_location_capacity(current_location)
            if not capacity_validation.is_valid:
                return capacity_validation
            
            return RoamingValidationResult(
                is_valid=True,
                pricing_info=pricing_info.to_dict(),
                warnings=self._collect_warnings(voucher, current_location)
            )
            
        except Exception as e:
            logger.error(f"Roaming validation error: {e}")
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Validation failed: {str(e)}"
            )
    
    def _validate_basic_voucher(self, voucher: DispatchVoucher) -> RoamingValidationResult:
        """Validate basic voucher properties"""
        if not voucher.is_active:
            return RoamingValidationResult(
                is_valid=False,
                error_message="Voucher is not active"
            )
        
        if voucher.voucher_expires and voucher.voucher_expires <= timezone.now():
            return RoamingValidationResult(
                is_valid=False,
                error_message="Voucher has expired"
            )
        
        if voucher.is_used:
            return RoamingValidationResult(
                is_valid=False,
                error_message="Voucher has already been used"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_location_roaming(
        self, 
        home_location: Location, 
        current_location: Location
    ) -> RoamingValidationResult:
        """Validate location-level roaming permissions"""
        
        if home_location == current_location:
            return RoamingValidationResult(is_valid=True)  # Home location - always allowed
        
        if not home_location.allow_roaming_out:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Roaming out not allowed from {home_location.name}"
            )
        
        if not current_location.allow_roaming_in:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Roaming in not allowed at {current_location.name}"
            )
        
        if not current_location.is_operational:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Location {current_location.name} is not operational"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_package_roaming(self, package: PackageType) -> RoamingValidationResult:
        """Validate package-level roaming permissions"""
        if not package.allow_roaming:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Package {package.name} does not allow roaming"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_user_roaming(self, user: ClientH, current_location: Location) -> RoamingValidationResult:
        """Validate user-level roaming permissions and limits"""
        
        # Check if user is already roaming at maximum locations
        current_roaming_count = DispatchVoucher.objects.filter(
            user=user,
            is_roaming=True,
            is_active=True
        ).values('roaming_location').distinct().count()
        
        max_roaming_locations = user.home_location.max_roaming_locations
        if current_roaming_count >= max_roaming_locations:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"User has reached maximum roaming locations ({max_roaming_locations})"
            )
        
        # Check user account status
        if user.status not in ['active', 'premium']:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"User account status '{user.status}' does not allow roaming"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_roaming_time_restrictions(self, location: Location) -> RoamingValidationResult:
        """Validate time-based roaming restrictions"""
        restrictions = location.roaming_time_restrictions
        if not restrictions:
            return RoamingValidationResult(is_valid=True)
        
        now = timezone.now()
        
        # Check maintenance windows
        maintenance_windows = restrictions.get('maintenance_windows', [])
        for window in maintenance_windows:
            if self._is_time_in_window(now, window):
                return RoamingValidationResult(
                    is_valid=False,
                    error_message=f"Roaming not allowed during maintenance window: {window}"
                )
        
        # Check blocked days
        blocked_days = restrictions.get('blocked_days', [])
        current_day = now.strftime('%A').lower()
        if current_day in blocked_days:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Roaming not allowed on {current_day.title()}"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_concurrent_roaming(
        self, 
        voucher: DispatchVoucher, 
        current_location: Location
    ) -> RoamingValidationResult:
        """Validate concurrent roaming restrictions"""
        
        # Check if voucher is already active at another location
        if voucher.is_roaming and voucher.roaming_location != current_location:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Voucher is already active at {voucher.roaming_location.name}"
            )
        
        # Check if user has another active voucher at this location
        existing_voucher = DispatchVoucher.objects.filter(
            user=voucher.user,
            roaming_location=current_location,
            is_active=True,
            is_roaming=True
        ).exclude(id=voucher.id).first()
        
        if existing_voucher:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"User already has an active voucher at {current_location.name}"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_user_balance(self, user: ClientH, required_amount: Decimal) -> RoamingValidationResult:
        """Validate user has sufficient balance for roaming"""
        available_credit = user.get_available_credit()
        
        if available_credit < required_amount:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Insufficient balance. Required: {required_amount}, Available: {available_credit}"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _validate_location_capacity(self, location: Location) -> RoamingValidationResult:
        """Validate location has capacity for roaming users"""
        if location.is_overloaded:
            return RoamingValidationResult(
                is_valid=False,
                error_message=f"Location {location.name} is over capacity ({location.capacity_percentage:.1f}%)"
            )
        
        return RoamingValidationResult(is_valid=True)
    
    def _calculate_roaming_pricing(
        self, 
        voucher: DispatchVoucher, 
        current_location: Location
    ) -> RoamingPricingInfo:
        """Calculate roaming pricing"""
        base_price = voucher.package.price
        roaming_multiplier = current_location.roaming_price_multiplier
        
        roaming_surcharge = base_price * (roaming_multiplier - Decimal('1.0'))
        total_price = base_price + roaming_surcharge
        
        return RoamingPricingInfo(
            base_price=base_price,
            roaming_multiplier=roaming_multiplier,
            roaming_surcharge=roaming_surcharge,
            total_price=total_price
        )
    
    def _is_time_in_window(self, current_time: timezone.datetime, window: str) -> bool:
        """Check if current time is within a time window"""
        try:
            start_time, end_time = window.split('-')
            current_time_str = current_time.strftime('%H:%M')
            return start_time <= current_time_str <= end_time
        except (ValueError, AttributeError):
            return False
    
    def _collect_warnings(self, voucher: DispatchVoucher, current_location: Location) -> List[str]:
        """Collect non-blocking warnings"""
        warnings = []
        
        # High roaming surcharge warning
        pricing = self._calculate_roaming_pricing(voucher, current_location)
        if pricing.roaming_multiplier > Decimal('1.5'):
            warnings.append(f"High roaming surcharge: {pricing.roaming_surcharge} KES")
        
        # Location capacity warning
        if current_location.capacity_percentage > 80:
            warnings.append(f"Location is {current_location.capacity_percentage:.1f}% full")
        
        # Voucher expiry warning
        if voucher.voucher_expires:
            time_to_expiry = voucher.voucher_expires - timezone.now()
            if time_to_expiry < timedelta(hours=1):
                warnings.append(f"Voucher expires in {time_to_expiry}")
        
        return warnings


class RoamingActivationService:
    """Service for activating roaming vouchers"""
    
    def __init__(self):
        self.validator = RoamingValidator()
        self.node_identity = NodeIdentity.get_current_node()
    
    async def activate_roaming_voucher(
        self, 
        voucher: DispatchVoucher, 
        current_location: Location,
        user: ClientH
    ) -> Tuple[bool, str, Optional[DispatchVoucher]]:
        """Activate a voucher for roaming use"""
        
        try:
            # Validate roaming
            validation_result = self.validator.validate_roaming_voucher(
                voucher, current_location, user
            )
            
            if not validation_result.is_valid:
                return False, validation_result.error_message, None
            
            # Execute distributed transaction for roaming activation
            success, message = await self._execute_roaming_transaction(
                voucher, current_location, user, validation_result.pricing_info
            )
            
            if success:
                # Create roaming voucher record
                roaming_voucher = await self._create_roaming_voucher(
                    voucher, current_location, validation_result.pricing_info
                )
                return True, "Roaming voucher activated successfully", roaming_voucher
            else:
                return False, message, None
                
        except Exception as e:
            logger.error(f"Roaming activation error: {e}")
            return False, f"Activation failed: {str(e)}", None
    
    async def _execute_roaming_transaction(
        self,
        voucher: DispatchVoucher,
        current_location: Location,
        user: ClientH,
        pricing_info: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """Execute distributed transaction for roaming activation"""
        
        # Determine participants
        participants = [current_location]  # Current location
        if voucher.home_location != current_location:
            participants.append(voucher.home_location)  # Home location
        
        # Add central server if we're not central
        if not self.node_identity.is_central:
            central_location = Location.objects.filter(is_central=True).first()
            if central_location:
                participants.append(central_location)
        
        # Transaction data
        transaction_data = {
            'voucher_id': voucher.id,
            'user_id': user.id,
            'current_location_id': current_location.id,
            'home_location_id': voucher.home_location.id,
            'pricing_info': pricing_info,
            'activation_timestamp': timezone.now().isoformat()
        }
        
        # Execute distributed transaction
        return await transaction_manager.execute_distributed_transaction(
            transaction_type='roaming_activation',
            transaction_data=transaction_data,
            participant_locations=participants
        )
    
    async def _create_roaming_voucher(
        self,
        original_voucher: DispatchVoucher,
        current_location: Location,
        pricing_info: Dict[str, Any]
    ) -> DispatchVoucher:
        """Create roaming voucher record"""
        
        with transaction.atomic():
            # Mark original voucher as roaming
            original_voucher.is_roaming = True
            original_voucher.roaming_location = current_location
            original_voucher.save()
            
            # Create new voucher for current location
            roaming_voucher = DispatchVoucher.objects.create(
                user=original_voucher.user,
                package=original_voucher.package,
                home_location=original_voucher.home_location,
                is_roaming=True,
                roaming_location=current_location,
                voucher_code=f"R-{original_voucher.voucher_code}",
                voucher_expires=original_voucher.voucher_expires,
                is_active=True,
                activation_location=current_location
            )
            
            # Update user balance using CRDT
            await self._update_user_balance_crdt(
                original_voucher.user,
                -Decimal(pricing_info['total_price']),
                current_location
            )
            
            return roaming_voucher
    
    async def _update_user_balance_crdt(
        self,
        user: ClientH,
        amount: Decimal,
        location: Location
    ):
        """Update user balance using CRDT for conflict-free replication"""
        
        # Get or create CRDT for user
        crdt_key = f"balance_crdt:{user.id}"
        crdt_data = cache.get(crdt_key)
        
        if crdt_data:
            crdt = ConflictFreeReplicatedDataType.from_dict(crdt_data)
        else:
            crdt = ConflictFreeReplicatedDataType(user.id)
        
        # Add operation
        operation_id = f"{location.id}_{timezone.now().timestamp()}_{amount}"
        crdt.add_operation(amount, location.id, operation_id)
        
        # Store updated CRDT
        cache.set(crdt_key, crdt.to_dict(), timeout=86400)  # 24 hours
        
        # Update local balance
        user.balance += amount
        user.save()
        
        # Sync balance change
        from .sync_services import SyncEvent, SyncPriority
        balance_event = SyncEvent(
            event_type='balance_update',
            location_id=location.id,
            data={
                'user_id': user.id,
                'amount': str(amount),
                'operation_id': operation_id,
                'crdt_data': crdt.to_dict()
            },
            priority=SyncPriority.CRITICAL,
            timestamp=timezone.now(),
            correlation_id=f"balance_{user.id}_{timezone.now().timestamp()}"
        )
        
        await sync_service.event_queue.put(balance_event)


class RoamingConflictResolver:
    """Resolve conflicts in roaming scenarios"""
    
    def __init__(self):
        self.node_identity = NodeIdentity.get_current_node()
    
    async def resolve_balance_conflict(
        self,
        user: ClientH,
        conflicting_operations: List[Dict[str, Any]]
    ) -> Decimal:
        """Resolve balance conflicts using CRDT"""
        
        # Create CRDT and add all operations
        crdt = ConflictFreeReplicatedDataType(user.id)
        
        for op_data in conflicting_operations:
            crdt.add_operation(
                Decimal(op_data['amount']),
                op_data['location_id'],
                op_data['operation_id']
            )
        
        # Calculate resolved balance
        resolved_balance = crdt.get_balance()
        
        # Update user balance
        user.balance = resolved_balance
        user.save()
        
        logger.info(f"Resolved balance conflict for user {user.id}: {resolved_balance}")
        return resolved_balance
    
    async def resolve_voucher_conflict(
        self,
        voucher: DispatchVoucher,
        conflicting_activations: List[Dict[str, Any]]
    ) -> bool:
        """Resolve voucher activation conflicts"""
        
        # Use timestamp-based resolution (first activation wins)
        earliest_activation = min(
            conflicting_activations,
            key=lambda x: x['activation_timestamp']
        )
        
        winning_location_id = earliest_activation['location_id']
        winning_location = Location.objects.get(id=winning_location_id)
        
        # Update voucher to reflect winning activation
        voucher.is_roaming = True
        voucher.roaming_location = winning_location
        voucher.save()
        
        # Cancel other activations
        for activation in conflicting_activations:
            if activation['location_id'] != winning_location_id:
                await self._cancel_voucher_activation(voucher, activation)
        
        logger.info(f"Resolved voucher conflict for {voucher.voucher_code}: {winning_location.name} wins")
        return True
    
    async def _cancel_voucher_activation(
        self,
        voucher: DispatchVoucher,
        activation_data: Dict[str, Any]
    ):
        """Cancel a conflicting voucher activation"""
        
        # Refund user balance
        refund_amount = Decimal(activation_data['pricing_info']['total_price'])
        voucher.user.balance += refund_amount
        voucher.user.save()
        
        # Log cancellation
        logger.info(f"Cancelled conflicting activation for {voucher.voucher_code}, refunded {refund_amount}")


# Global service instances
roaming_validator = None
roaming_activation_service = None
roaming_conflict_resolver = None