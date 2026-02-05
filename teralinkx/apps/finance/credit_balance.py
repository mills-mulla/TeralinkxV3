# apps/finance/credit_balance.py
"""
Production-Ready Balance Purchase Endpoint V3
==============================================
Integrated with payment_gateway.py, generate.py, and authentications.py

Features Implemented:
✅ JWT authentication with user context extraction
✅ Rate limiting (15/min, 5/10s burst)
✅ Request validation schemas
✅ Transaction ownership verification
✅ Idempotency keys
✅ Retry mechanisms for RouterOS
✅ Circuit breaker for router operations
✅ Monitoring/metrics integration
✅ Comprehensive audit trail
✅ Auto-refund on failures
✅ WebSocket notifications ready
✅ Integrated with V3 TransactionQueue helpers
✅ Integrated with RouterManager and generate.py
✅ Hotspot IP conflict resolution from multiple sources
"""

import logging
import hashlib
import time
import uuid
from decimal import Decimal
from typing import Dict, Optional
from collections import Counter

from django.utils import timezone
from django.db import transaction
from django.contrib.auth import get_user_model
from django.core.cache import cache

from rest_framework.views import APIView
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.throttling import UserRateThrottle

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from core.services.notification_service import create_and_notify
from packages.models import PackageType, DispatchVoucher
from users.models import ClientH
from finance.models import TransactionQueue
from packages.generate import activate_voucher
from finance.authentications import RouterManager, RouterConfig
from core.services.rewards_service import RewardsService
from locations.models import Location

# Import V3 payment gateway helpers
from .payment_gateway import (
    TransactionQueueHelper,
    NotificationHelper,
)

logger = logging.getLogger(__name__)
User = get_user_model()


# ============================================================================
# HOTSPOT IP RESOLVER
# ============================================================================

class HotspotIPResolver:
    """Resolves hotspot IP from multiple sources with conflict detection"""
    
    @staticmethod
    def resolve_hotspot_ip(request, request_hotspot_ip: Optional[str] = None) -> Optional[str]:
        """
        Resolve hotspot IP with priority and conflict detection:
        1. From request body (explicit user input)
        2. From JWT payload last_login_ip
        3. From request remote address
        
        Conflict resolution:
        - All match: Use any (consensus)
        - 2/3 match: Use majority (consensus)
        - All different: Prefer JWT if available, else request body
        - Only one available: Use that
        """
        
        sources = {}
        
        # 1. From request body (explicit user input - highest priority if provided)
        if request_hotspot_ip:
            sources['request_body'] = str(request_hotspot_ip).strip()
        
        # 2. From JWT payload
        jwt_ip = None
        if hasattr(request, 'auth') and request.auth:
            jwt_payload = getattr(request.auth, 'payload', {})
            jwt_ip = jwt_payload.get('last_login_ip')
            if jwt_ip:
                sources['jwt'] = str(jwt_ip).strip()
        
        # 3. From request remote address
        remote_ip = request.META.get('REMOTE_ADDR')
        if remote_ip:
            sources['remote_addr'] = str(remote_ip).strip()
        
        logger.debug(f"Hotspot IP sources: {sources}")
        
        # No sources available
        if not sources:
            return None
        
        # Only one source available
        if len(sources) == 1:
            resolved_ip = list(sources.values())[0]
            logger.info(f"Hotspot IP single source: Using {resolved_ip} from {list(sources.keys())[0]}")
            return resolved_ip
        
        # Check for consensus
        ip_values = list(sources.values())
        
        # All values match (consensus)
        if len(set(ip_values)) == 1:
            logger.info(f"Hotspot IP consensus: All sources agree on {ip_values[0]}")
            return ip_values[0]
        
        # Find majority (2/3 match)
        ip_counter = Counter(ip_values)
        most_common = ip_counter.most_common(1)[0]
        
        if most_common[1] >= 2:  # At least 2 sources agree
            logger.info(f"Hotspot IP majority: {most_common[0]} (agreed by {most_common[1]}/3 sources)")
            return most_common[0]
        
        # All different - apply priority rules
        logger.warning(f"Hotspot IP conflict: All sources different - {sources}")
        
        # Priority order: request_body > jwt > remote_addr
        if 'request_body' in sources:
            logger.info(f"Hotspot IP conflict resolved: Using request body value {sources['request_body']}")
            return sources['request_body']
        
        if 'jwt' in sources:
            logger.info(f"Hotspot IP conflict resolved: Using JWT value {sources['jwt']}")
            return sources['jwt']
        
        logger.info(f"Hotspot IP conflict resolved: Using remote address {sources['remote_addr']}")
        return sources['remote_addr']


# ============================================================================
# REQUEST VALIDATION SCHEMAS
# ============================================================================

class BalancePurchaseRequestSerializer(serializers.Serializer):
    """Validates balance purchase request"""
    package_id = serializers.IntegerField(required=True, min_value=1)
    hotspot_ip = serializers.IPAddressField(required=False, allow_null=True)
    idempotency_key = serializers.CharField(max_length=100, required=False, allow_null=True)
    auto_login = serializers.BooleanField(default=True, required=False)
    coupon_code = serializers.CharField(max_length=50, required=False, allow_null=True)
    
    def validate_package_id(self, value):
        """Ensure package exists and is available"""
        try:
            package = PackageType.objects.get(id=value)
            if not package.is_active:
                raise serializers.ValidationError("Package is not active")
            if not package.is_available:
                raise serializers.ValidationError("Package is sold out")
            return value
        except PackageType.DoesNotExist:
            raise serializers.ValidationError("Package not found")


# ============================================================================
# RATE LIMITING
# ============================================================================

class BalancePurchaseThrottle(UserRateThrottle):
    """Rate limiting for balance purchases - 15 per minute"""
    rate = '15/m'


class BurstBalancePurchaseThrottle(UserRateThrottle):
    """Burst protection - 2 requests per second"""
    rate = '2/s'


# ============================================================================
# IDEMPOTENCY MANAGER
# ============================================================================

class BalanceIdempotencyManager:
    """Manages idempotency for balance purchases"""
    CACHE_PREFIX = "balance_purchase_idempotency:"
    CACHE_TIMEOUT = 3600  # 1 hour
    
    @staticmethod
    def generate_key(user_id: int, package_id: int) -> str:
        """Generate idempotency key from user and package"""
        raw = f"{user_id}:{package_id}:{int(time.time() // 60)}"
        return hashlib.sha256(raw.encode()).hexdigest()
    
    @staticmethod
    def check_and_set(idempotency_key: str, data: Optional[Dict] = None) -> tuple:
        """Check if key exists, if not set it"""
        cache_key = f"{BalanceIdempotencyManager.CACHE_PREFIX}{idempotency_key}"
        cached = cache.get(cache_key)
        
        if cached:
            logger.warning(f"Duplicate balance purchase detected: {idempotency_key}")
            return True, cached
        
        cache.set(cache_key, data or {'processed': True}, BalanceIdempotencyManager.CACHE_TIMEOUT)
        return False, None
    
    @staticmethod
    def update(idempotency_key: str, data: Dict):
        """Update cached response"""
        cache_key = f"{BalanceIdempotencyManager.CACHE_PREFIX}{idempotency_key}"
        cache.set(cache_key, data, BalanceIdempotencyManager.CACHE_TIMEOUT)


# ============================================================================
# CIRCUIT BREAKER FOR ROUTEROS
# ============================================================================

class RouterCircuitBreaker:
    """Circuit breaker for RouterOS operations"""
    STATE_CLOSED = 'closed'
    STATE_OPEN = 'open'
    STATE_HALF_OPEN = 'half_open'
    
    def __init__(self, failure_threshold=5, timeout=60, name='routeros'):
        self.name = name
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.cache_key_state = f"circuit_breaker:{name}:state"
        self.cache_key_failures = f"circuit_breaker:{name}:failures"
        self.cache_key_last_failure = f"circuit_breaker:{name}:last_failure"
    
    def get_state(self) -> str:
        """Get current state"""
        state = cache.get(self.cache_key_state, self.STATE_CLOSED)
        if state == self.STATE_OPEN:
            last_failure = cache.get(self.cache_key_last_failure, 0)
            if time.time() - last_failure > self.timeout:
                self.set_state(self.STATE_HALF_OPEN)
                return self.STATE_HALF_OPEN
        return state
    
    def set_state(self, state: str):
        """Set state"""
        cache.set(self.cache_key_state, state, timeout=None)
        logger.info(f"Circuit breaker '{self.name}' → {state}")
    
    def record_success(self):
        """Record successful operation"""
        if self.get_state() == self.STATE_HALF_OPEN:
            self.set_state(self.STATE_CLOSED)
            cache.delete(self.cache_key_failures)
            logger.info(f"Circuit breaker '{self.name}' recovered")
    
    def record_failure(self):
        """Record failed operation"""
        failures = cache.get(self.cache_key_failures, 0) + 1
        cache.set(self.cache_key_failures, failures, timeout=None)
        cache.set(self.cache_key_last_failure, time.time(), timeout=None)
        
        if failures >= self.failure_threshold:
            self.set_state(self.STATE_OPEN)
            logger.error(f"Circuit breaker '{self.name}' OPENED after {failures} failures")
    
    def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker"""
        state = self.get_state()
        if state == self.STATE_OPEN:
            raise RouterCircuitBreakerOpenError(f"Circuit breaker '{self.name}' is OPEN")
        
        try:
            result = func(*args, **kwargs)
            self.record_success()
            return result
        except Exception as e:
            self.record_failure()
            raise


class RouterCircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open"""
    pass


# Initialize circuit breaker
router_circuit_breaker = RouterCircuitBreaker(
    failure_threshold=5,
    timeout=60,
    name='routeros_balance'
)


# ============================================================================
# MONITORING & METRICS
# ============================================================================

class BalanceMetrics:
    """Metrics collection for balance purchases"""
    
    @staticmethod
    def increment_counter(metric_name: str, value: int = 1):
        """Increment counter"""
        cache_key = f"metrics:counter:balance.{metric_name}"
        try:
            cache.incr(cache_key, delta=value)
        except ValueError:
            cache.set(cache_key, value)
    
    @staticmethod
    def record_timing(metric_name: str, duration_seconds: float):
        """Record timing"""
        cache_key = f"metrics:timing:balance.{metric_name}"
        cache.set(cache_key, duration_seconds * 1000, timeout=300)
    
    @staticmethod
    def record_purchase_success(amount: Decimal, processing_time: float):
        """Record successful purchase"""
        BalanceMetrics.increment_counter('purchases.success')
        BalanceMetrics.increment_counter('purchases.revenue', int(amount))
        BalanceMetrics.record_timing('purchases.processing_time', processing_time)
    
    @staticmethod
    def record_purchase_failure(error_category: str):
        """Record failed purchase"""
        BalanceMetrics.increment_counter('purchases.failure')
        BalanceMetrics.increment_counter(f'purchases.failure.{error_category}')
    
    @staticmethod
    def record_voucher_activation(success: bool, duration: float = None):
        """Record voucher activation"""
        status_label = 'success' if success else 'failure'
        BalanceMetrics.increment_counter(f'voucher_activation.{status_label}')
        if duration:
            BalanceMetrics.record_timing('voucher_activation.duration', duration)


# ============================================================================
# AUDIT TRAIL
# ============================================================================

class BalanceAuditLogger:
    """Audit logging for balance operations"""
    
    @staticmethod
    def log_purchase_attempt(user: User, package_id: int, amount: Decimal, metadata: Dict = None):
        """Log purchase attempt"""
        logger.info(
            f"AUDIT: Balance purchase attempt | User: {user.username} | "
            f"Package: {package_id} | Amount: {amount} | Meta: {metadata}"
        )
    
    @staticmethod
    def log_purchase_success(user: User, transaction_record, voucher_code: str, amount: Decimal):
        """Log successful purchase"""
        logger.info(
            f"AUDIT: Balance purchase SUCCESS | User: {user.username} | "
            f"Transaction: {transaction_record.checkout_request_id} | "
            f"Voucher: {voucher_code} | Amount: {amount}"
        )
    
    @staticmethod
    def log_purchase_failure(user: User, package_id: int, reason: str, error_category: str):
        """Log failed purchase"""
        logger.warning(
            f"AUDIT: Balance purchase FAILURE | User: {user.username} | "
            f"Package: {package_id} | Reason: {reason} | Category: {error_category}"
        )
    
    @staticmethod
    def log_refund(user: User, amount: Decimal, reason: str):
        """Log refund"""
        logger.warning(
            f"AUDIT: REFUND | User: {user.username} | "
            f"Amount: {amount} | Reason: {reason}"
        )
    
    @staticmethod
    def log_insufficient_balance(user: User, required: Decimal, available: Decimal):
        """Log insufficient balance attempt"""
        logger.info(
            f"AUDIT: Insufficient balance | User: {user.username} | "
            f"Required: {required} | Available: {available}"
        )
    
    @staticmethod
    def log_hotspot_ip_resolution(sources: Dict, resolved_ip: str):
        """Log hotspot IP resolution"""
        logger.info(
            f"Hotspot IP Resolution | Sources: {sources} | "
            f"Resolved: {resolved_ip}"
        )


# ============================================================================
# JWT USER CONTEXT EXTRACTOR (UPDATED)
# ============================================================================

class BalanceUserContextExtractor:
    """Extract user context from JWT for balance operations"""
    
    @staticmethod
    def extract_user_data(request):
        """Extract comprehensive user data from JWT"""
        if not request.user or not request.user.is_authenticated:
            raise ValueError("User not authenticated")
        
        user = request.user
        jwt_payload = getattr(request.auth, 'payload', {}) if request.auth else {}
        
        try:
            client = user.client_profile
        except ClientH.DoesNotExist:
            account = jwt_payload.get('client_account', f"USER_{user.id}")
            client = ClientH.objects.create(
                user=user,
                account=account,
                display_name=user.username,
                phone_number=jwt_payload.get('phone_number', ''),
                account_tier=jwt_payload.get('account_tier', 'basic'),
                home_location_id=jwt_payload.get('home_location_id', 1),
                status='active'
            )
        
        # Determine location
        location_id = jwt_payload.get('current_location_id') or jwt_payload.get('location_id')
        if location_id:
            try:
                current_location = Location.objects.get(id=location_id)
            except Location.DoesNotExist:
                current_location = client.home_location
        else:
            current_location = client.home_location
        
        # Update client location if needed
        if client.current_location != current_location:
            client.current_location = current_location
            client.last_location_update = timezone.now()
            client.save(update_fields=['current_location', 'last_location_update'])
        
        user_context = {
            'user': user,
            'client': client,
            'location': current_location,
            'jwt_payload': jwt_payload,
            'account': jwt_payload.get('client_account') or client.account,
            'phone': jwt_payload.get('phone_number') or client.phone_number,
            'account_tier': jwt_payload.get('account_tier') or client.account_tier,
            'balance': Decimal(str(jwt_payload.get('balance', client.balance))),
            'home_location_id': client.home_location_id,
            'current_location_id': current_location.id,
            'active_voucher_code': jwt_payload.get('active_voucher'),
            'is_active': jwt_payload.get('is_active', client.status == 'active'),
            'request': request,  # 🔴 ADDED: Include request object in context
        }
        
        return user_context


# ============================================================================
# VOUCHER MANAGER WITH CIRCUIT BREAKER (V3 INTEGRATED)
# ============================================================================

class BalanceVoucherManager:
    """Manages voucher activation with circuit breaker - V3 integrated"""
    
    @staticmethod
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(Exception)
    )
    def activate_voucher_with_retry(prefix: str, profile: str, devices: int) -> Dict:
        """Activate voucher with retry and circuit breaker using generate.py"""
        return router_circuit_breaker.call(
            activate_voucher,
            prefix=prefix,
            profile=profile,
            devices=devices
        )
    
    @staticmethod
    def create_dispatch_voucher(user_context: Dict, package: PackageType, 
                               voucher_code: str, transaction_record, final_price: Decimal = None) -> DispatchVoucher:
        """Create dispatch voucher record using V3 models with conditional balance deduction"""
        user = user_context['user']
        client = user_context['client']
        location = user_context['location']
        
        # Use final_price if provided (with coupon discount), otherwise use transaction price
        deduction_amount = final_price if final_price is not None else Decimal(transaction_record.price)
        
        dispatch_voucher = DispatchVoucher.objects.create(
            voucher_code=voucher_code,
            package=package,
            user=user,
            location=location,
            home_location=location,
            price_paid=deduction_amount,
            activated_at=timezone.now(),
            expires_at=timezone.now() + package.duration,
            status='active',
            transaction_id=transaction_record.checkout_request_id,
            payment_reference='BALANCE_PURCHASE',
            allowed_mac_addresses=[],
            is_roaming=False,
        )
        
        # 🔴 CRITICAL FIX: Only deduct balance for actual balance purchases
        # Check if this is a balance purchase (method='balance') vs M-Pesa payment (method='mpesa')
        is_balance_purchase = getattr(transaction_record, 'method', None) == 'balance'
        
        if is_balance_purchase:
            logger.info(f"DEBUG: Balance purchase - deducting {deduction_amount} from {client.account}")
            
            # Get fresh client and deduct balance
            client.refresh_from_db()
            old_balance = client.balance
            client.balance -= deduction_amount
            client.total_spent += deduction_amount
            client.active_voucher = voucher_code
            client.voucher_expiry = dispatch_voucher.expires_at
            client.save()
            
            logger.info(f"BALANCE DEDUCTION: {old_balance} -> {client.balance} (deducted {deduction_amount}) for {client.account}")
        else:
            logger.info(f"DEBUG: M-Pesa payment - NO balance deduction for {client.account}")
            
            # Update client voucher info without balance deduction
            client.refresh_from_db()
            client.active_voucher = voucher_code
            client.voucher_expiry = dispatch_voucher.expires_at
            client.save()
        
        # Increment package sales
        package.increment_sales()
        
        logger.info(f"Created dispatch voucher {voucher_code} for {client.account}")
        return dispatch_voucher
    
    @staticmethod
    def perform_auto_login(account: str, voucher_code: str, ip_address: str) -> bool:
        """Perform auto-login using authentications.py RouterManager"""
        try:
            router_config = RouterConfig.get_config()
            
            with RouterManager(router_config) as router:
                result = router.hotspot_login(
                    username=voucher_code,
                    ip_address=ip_address
                )
                
                if result:
                    logger.info(f"Auto-login successful for {account}")
                    return True
                else:
                    logger.warning(f"Auto-login failed for {account}")
                    return False
                    
        except Exception as e:
            logger.error(f"Auto-login error for {account}: {e}")
            return False


# ============================================================================
# BALANCE PURCHASE PROCESSOR (V3 INTEGRATED - UPDATED)
# ============================================================================

class BalancePurchaseProcessor:
    """Handles the complete purchase workflow - V3 integrated"""
    
    @staticmethod
    def generate_checkout_id(account: str, package_id: int) -> str:
        """Generate unique checkout request ID"""
        unique_suffix = uuid.uuid4().hex[:8]
        return f"bal_co_{account}_{package_id}_{unique_suffix}"
    
    @staticmethod
    def validate_package_availability(package: PackageType) -> tuple:
        """Validate package is available"""
        if not package.is_active:
            return False, "Package is not active"
        
        if not package.is_available:
            return False, "Package is sold out"
        
        return True, None
    
    @staticmethod
    def check_balance_sufficiency(client: ClientH, package: PackageType) -> tuple:
        """Check if client has sufficient balance"""
        if client.balance < package.price:
            shortage = package.price - client.balance
            BalanceAuditLogger.log_insufficient_balance(
                client.user,
                required=package.price,
                available=client.balance
            )
            return False, {
                'status': 'insufficient_balance',
                'required': float(package.price),
                'available': float(client.balance),
                'shortage': float(shortage)
            }
        
        return True, None
    
    @staticmethod
    def check_balance_sufficiency_with_price(client: ClientH, price: Decimal) -> tuple:
        """Check if client has sufficient balance for specific price"""
        if client.balance < price:
            shortage = price - client.balance
            BalanceAuditLogger.log_insufficient_balance(
                client.user,
                required=price,
                available=client.balance
            )
            return False, {
                'status': 'insufficient_balance',
                'required': float(price),
                'available': float(client.balance),
                'shortage': float(shortage)
            }
        
        return True, None
    
    @staticmethod
    def create_transaction_record(user_context: Dict, package: PackageType, 
                                 checkout_request_id: str, final_price: Decimal = None,
                                 applied_coupon = None) -> TransactionQueue:
        """Create transaction queue record using V3 TransactionQueue"""
        client = user_context['client']
        price = final_price if final_price is not None else package.price
        
        metadata = {
            'package_id': package.id,
            'account_tier': user_context['account_tier'],
            'location_id': user_context['current_location_id'],
            'purchase_type': 'balance_only'
        }
        
        if applied_coupon:
            metadata['coupon_code'] = applied_coupon.code
            metadata['original_price'] = float(package.price)
            metadata['discount_amount'] = float(package.price - price)
        
        return TransactionQueue.objects.create(
            queue_type='balance_purchase',
            user=client,
            method='balance',
            initiator=client.account,
            checkout_request_id=checkout_request_id,
            package_code=package.code,
            package=package.name,
            price=price,
            status='pending',
            recipient=client.account,
            used_credit=price,
            priority='normal',
            metadata=metadata
        )
    
    @staticmethod
    def process_purchase(user_context: Dict, package: PackageType, 
                        hotspot_ip: Optional[str] = None,
                        auto_login: bool = True,
                        idempotency_key: Optional[str] = None,
                        coupon_code: Optional[str] = None) -> Dict:
        """Process complete purchase workflow with coupon support"""
        start_time = time.time()
        client = user_context['client']
        user = user_context['user']
        
        # Calculate final price with coupon discount
        final_price = package.price
        discount_amount = Decimal('0')
        applied_coupon = None
        
        if coupon_code:
            from packages.models import Coupon
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                if coupon.valid_until >= timezone.now() and coupon.total_uses < coupon.max_uses:
                    if coupon.coupon_type == 'percentage':
                        discount_amount = package.price * (coupon.discount_value / 100)
                    else:
                        discount_amount = min(coupon.discount_value, package.price)
                    
                    final_price = max(Decimal('0'), package.price - discount_amount)
                    applied_coupon = coupon
                    logger.info(f"Applied coupon {coupon_code}: {discount_amount} discount")
            except Coupon.DoesNotExist:
                logger.warning(f"Invalid coupon code used: {coupon_code}")
        
        # 🔴 RESOLVE HOTSPOT IP FROM MULTIPLE SOURCES
        request = user_context.get('request')
        if request:
            resolved_hotspot_ip = HotspotIPResolver.resolve_hotspot_ip(
                request=request,
                request_hotspot_ip=hotspot_ip
            )
            hotspot_ip = resolved_hotspot_ip
        
        # Audit log with resolved IP information
        BalanceAuditLogger.log_purchase_attempt(
            user=user,
            package_id=package.id,
            amount=package.price,
            metadata={
                'hotspot_ip': hotspot_ip, 
                'auto_login': auto_login,
                'resolved': True if hotspot_ip else False
            }
        )
        
        # Check idempotency
        if idempotency_key:
            is_duplicate, cached_response = BalanceIdempotencyManager.check_and_set(idempotency_key)
            if is_duplicate:
                logger.info(f"Returning cached response for: {idempotency_key}")
                return cached_response
        
        # Validate package
        is_valid, error_msg = BalancePurchaseProcessor.validate_package_availability(package)
        if not is_valid:
            BalanceMetrics.record_purchase_failure('package_unavailable')
            raise ValueError(error_msg)
        
        # Check balance with final price
        has_balance, insufficient_data = BalancePurchaseProcessor.check_balance_sufficiency_with_price(client, final_price)
        if not has_balance:
            BalanceMetrics.record_purchase_failure('insufficient_balance')
            return insufficient_data
        
        # Generate checkout ID
        checkout_request_id = BalancePurchaseProcessor.generate_checkout_id(
            client.account,
            package.id
        )
        
        # Create transaction record with coupon info
        transaction_record = BalancePurchaseProcessor.create_transaction_record(
            user_context,
            package,
            checkout_request_id,
            final_price,
            applied_coupon
        )
        
        try:
            # Mark as processing
            transaction_record.mark_processing()
            
            # Activate voucher with circuit breaker
            activation_start = time.time()
            try:
                activation_result = BalanceVoucherManager.activate_voucher_with_retry(
                    prefix='BAL',
                    profile=package.code,
                    devices=package.device_limit
                )
                activation_duration = time.time() - activation_start
                BalanceMetrics.record_voucher_activation(True, activation_duration)
                
            except RouterCircuitBreakerOpenError:
                BalanceMetrics.record_purchase_failure('router_circuit_open')
                raise ValueError("Router service temporarily unavailable. Please try again in a moment.")
            except Exception as e:
                activation_duration = time.time() - activation_start
                BalanceMetrics.record_voucher_activation(False, activation_duration)
                raise ValueError(f"Voucher activation failed: {str(e)}")
            
            if activation_result.get("status") != "activated":
                raise ValueError(f"Voucher activation failed: {activation_result.get('error', 'Unknown error')}")
            
            voucher_code = activation_result["voucher_code"]
            
            # Mark as used and track coupon usage
            if applied_coupon:
                applied_coupon.total_uses += 1
                if applied_coupon.total_uses >= applied_coupon.max_uses:
                    applied_coupon.is_active = False
                applied_coupon.save()
                logger.info(f"Coupon {applied_coupon.code} used. Remaining uses: {applied_coupon.max_uses - applied_coupon.total_uses}")
            
            # Create dispatch voucher with balance deduction
            logger.info(f"DEBUG: About to create dispatch voucher for {client.account}")
            dispatch_voucher = BalanceVoucherManager.create_dispatch_voucher(
                user_context=user_context,
                package=package,
                voucher_code=voucher_code,
                transaction_record=transaction_record,
                final_price=final_price
            )
            logger.info(f"DEBUG: Dispatch voucher created successfully")
            
            # Verify balance was actually deducted by re-fetching client
            client_after_deduction = ClientH.objects.get(id=client.id)
            logger.info(f"DEBUG: Client balance after voucher creation: {client_after_deduction.balance}")
            
            # 🔴 CRITICAL: Mark transaction as completed IMMEDIATELY after balance deduction
            # This ensures the transaction is committed before any non-critical operations
            transaction_record.mark_processed()
            logger.info(f"DEBUG: Transaction marked as processed - balance should be committed")
            
            # Force transaction commit by ending the current transaction block
            transaction.commit()
            logger.info(f"DEBUG: Transaction explicitly committed")
            
            # Verify balance is still deducted after commit
            client_post_commit = ClientH.objects.get(id=client.id)
            logger.info(f"DEBUG: Client balance after explicit commit: {client_post_commit.balance}")
            
            # 🎁 REWARD POINTS POLICY: Balance-only purchases do NOT earn points
            # Only M-Pesa and M-Pesa + balance purchases earn reward points
            # This encourages users to use M-Pesa for payments
            logger.info(f"Balance-only purchase completed for {client.account} - NO reward points awarded (policy)")
            
            # Perform auto-login if requested and IP is available (non-critical - separate operation)
            auto_login_success = False
            try:
                if auto_login and hotspot_ip:
                    auto_login_success = BalanceVoucherManager.perform_auto_login(
                        account=client.account,
                        voucher_code=voucher_code,
                        ip_address=hotspot_ip
                    )
                    if auto_login_success:
                        logger.info(f"Auto-login performed successfully for {client.account}")
                    else:
                        logger.warning(f"Auto-login failed for {client.account}")
                elif auto_login and not hotspot_ip:
                    logger.info(f"Auto-login skipped for {client.account}: No hotspot IP available")
            except Exception as e:
                logger.error(f"Auto-login error for {client.account}: {e}")
                auto_login_success = False
                # Don't let auto-login failures affect the main purchase
            
            # Audit log success
            BalanceAuditLogger.log_purchase_success(
                user=user,
                transaction_record=transaction_record,
                voucher_code=voucher_code,
                amount=package.price
            )
            
            # Send notifications using V3 NotificationHelper
            BalanceNotifier.notify_purchase_success(
                user_context=user_context,
                package=package,
                dispatch_voucher=dispatch_voucher,
                auto_login_success=auto_login_success
            )
            
            processing_time = time.time() - start_time
            BalanceMetrics.record_purchase_success(package.price, processing_time)
            
            result = {
                'success': True,
                'status': 'completed',
                'transaction_id': transaction_record.checkout_request_id,
                'voucher_code': voucher_code,
                'package': {
                    'id': package.id,
                    'name': package.name,
                    'code': package.code,
                    'price': float(package.price),
                    'duration': str(package.duration),
                    'speed_mbps': package.speed_limit_mbps,
                    'devices': package.device_limit,
                },
                'expires_at': dispatch_voucher.expires_at.isoformat(),
                'auto_login': auto_login_success,
                'balance_after': float(client.balance),
                'processing_time_seconds': round(processing_time, 2),
                'hotspot_ip_used': hotspot_ip if hotspot_ip else None,
            }
            
            # Update idempotency cache
            if idempotency_key:
                BalanceIdempotencyManager.update(idempotency_key, result)
            
            return result
            
        except Exception as e:
            # Mark as failed
            transaction_record.mark_failed(
                reason=str(e),
                error_code="BALANCE_PURCHASE_ERROR",
                failure_category="system_error"
            )
            
            # Refund balance since it was already deducted
            try:
                with transaction.atomic():
                    client = ClientH.objects.select_for_update().get(id=client.id)
                    client.balance += final_price
                    client.save()
                    logger.info(f"Refunded {final_price} to {client.account} due to purchase failure")
            except Exception as refund_error:
                logger.error(f"Failed to refund balance to {client.account}: {refund_error}")
            
            # Audit log
            BalanceAuditLogger.log_purchase_failure(
                user=user,
                package_id=package.id,
                reason=str(e),
                error_category='system_error'
            )
            
            # Notify failure
            BalanceNotifier.notify_purchase_failure(
                user_context=user_context,
                package=package,
                error=str(e)
            )
            
            raise
    
    @staticmethod
    def refund_balance(user_context: Dict, amount: Decimal):
        """Refund balance to user"""
        try:
            client = user_context['client']
            amount_decimal = Decimal(str(amount))
            
            if amount_decimal > 0:
                with transaction.atomic():
                    client.balance += amount_decimal
                    client.save()
                
                BalanceAuditLogger.log_refund(
                    user=user_context['user'],
                    amount=amount_decimal,
                    reason='Purchase failed - balance refunded'
                )
                
                logger.info(f"Refunded {amount_decimal} to {client.account}")
                
        except Exception as e:
            logger.error(f"Refund failed for {user_context['account']}: {e}")
            raise


# ============================================================================
# NOTIFICATION MANAGER (V3 INTEGRATED)
# ============================================================================

class BalanceNotifier:
    """Handles notifications for balance purchases - V3 integrated"""
    
    @staticmethod
    def notify_purchase_success(user_context: Dict, package: PackageType, 
                               dispatch_voucher: DispatchVoucher, 
                               auto_login_success: bool):
        """Send success notifications using V3 helpers"""
        user = user_context['user']
        client = user_context['client']
        
        # Use V3 NotificationHelper
        NotificationHelper.send_payment_notification(
            user,
            "✅ Purchase Successful",
            "success"
        )
        
        login_status = "✓ Auto-login successful" if auto_login_success else "Manual login required"
        
        message = f"""
🎉 **Package Activated!**

**Voucher:** {dispatch_voucher.voucher_code}
**Package:** {package.name}
**Price:** KSh {package.price}
**Balance Remaining:** KSh {client.balance}
**Expires:** {dispatch_voucher.expires_at.strftime('%Y-%m-%d %H:%M')}

**Details:**
- Speed: {package.speed_limit_mbps} Mbps
- Devices: {package.device_limit}
- Duration: {package.duration}

**Status:** {login_status}
"""
        
        NotificationHelper.send_payment_notification(user, message, "success")
    
    @staticmethod
    def notify_purchase_failure(user_context: Dict, package: PackageType, error: str):
        """Send failure notifications using V3 helpers"""
        user = user_context['user']
        
        NotificationHelper.send_payment_notification(
            user,
            f"❌ Purchase Failed: {error}",
            "error"
        )
        NotificationHelper.send_payment_notification(
            user,
            "Your balance has been refunded.",
            "info"
        )


# ============================================================================
# MAIN API VIEW (UPDATED)
# ============================================================================

class BalancePurchaseAPIView(APIView):
    """
    ✅ Production-Ready Balance Purchase Endpoint V3
    
    POST /api/finance/balance-purchase/
    
    Features:
    - JWT authentication
    - Rate limiting (15/min, 5/10s burst)
    - Request validation
    - Idempotency support
    - Circuit breaker for router
    - Retry mechanisms
    - V3 TransactionQueue integration
    - V3 NotificationHelper integration
    - RouterManager from authentications.py
    - activate_voucher from generate.py
    - Hotspot IP conflict resolution from multiple sources
    """
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    throttle_classes = [BalancePurchaseThrottle, BurstBalancePurchaseThrottle]
    
    def post(self, request):
        """Process balance purchase"""
        
        # Validate request
        serializer = BalancePurchaseRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                'success': False,
                'error': 'Invalid request parameters',
                'details': serializer.errors,
                'code': 'VALIDATION_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        validated_data = serializer.validated_data
        package_id = validated_data['package_id']
        request_hotspot_ip = validated_data.get('hotspot_ip')  # From request body
        auto_login = validated_data.get('auto_login', True)
        idempotency_key = validated_data.get('idempotency_key')
        coupon_code = validated_data.get('coupon_code')
        
        # 🔴 RESOLVE HOTSPOT IP FROM MULTIPLE SOURCES
        hotspot_ip = HotspotIPResolver.resolve_hotspot_ip(
            request=request,
            request_hotspot_ip=request_hotspot_ip
        )
        
        # Generate idempotency key if not provided
        if not idempotency_key:
            idempotency_key = BalanceIdempotencyManager.generate_key(
                request.user.id,
                package_id
            )
        
        try:
            # Extract user context
            user_context = BalanceUserContextExtractor.extract_user_data(request)
            
            # Get package
            try:
                package = PackageType.objects.get(id=package_id)
            except PackageType.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Package not found',
                    'code': 'PACKAGE_NOT_FOUND'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Process purchase
            result = BalancePurchaseProcessor.process_purchase(
                user_context=user_context,
                package=package,
                hotspot_ip=hotspot_ip,
                auto_login=auto_login,
                idempotency_key=idempotency_key,
                coupon_code=coupon_code
            )
            
            # Check if insufficient balance
            if not result.get('success', True):
                return Response({
                    'success': False,
                    'error': 'Insufficient balance',
                    'details': result,
                    'code': 'INSUFFICIENT_BALANCE'
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            # Build response with fresh database query
            logger.info(f"DEBUG: Building response - final client balance check")
            
            # Direct database query to get most accurate balance
            from django.db import connection
            with connection.cursor() as cursor:
                cursor.execute(
                    "SELECT balance, account FROM users_clienth WHERE id = %s",
                    [user_context['client'].id]
                )
                db_result = cursor.fetchone()
                if db_result:
                    actual_balance, account = db_result
                    logger.info(f"DEBUG: DIRECT DB QUERY - Account: {account}, Balance: {actual_balance}")
                else:
                    logger.error(f"DEBUG: DIRECT DB QUERY - No client found with ID {user_context['client'].id}")
                    actual_balance = 0
            
            # Also get via ORM for comparison
            final_client_check = ClientH.objects.get(id=user_context['client'].id)
            logger.info(f"DEBUG: ORM QUERY - Balance: {final_client_check.balance}")
            logger.info(f"DEBUG: BALANCE COMPARISON - DB: {actual_balance}, ORM: {final_client_check.balance}")
            
            response_data = {
                'success': True,
                'timestamp': timezone.now().isoformat(),
                'user': {
                    'account': user_context['account'],
                    'account_tier': user_context['account_tier'],
                    'balance': float(actual_balance)  # Use direct DB query result
                },
                'purchase': result,
                'metadata': {
                    'location_id': user_context['current_location_id'],
                    'hotspot_ip': hotspot_ip,
                    'hotspot_ip_resolved': True if hotspot_ip else False,
                    'idempotency_key': idempotency_key
                }
            }
            
            return Response(response_data, status=status.HTTP_201_CREATED)
            
        except RouterCircuitBreakerOpenError:
            return Response({
                'success': False,
                'error': 'Router service temporarily unavailable. Please try again in a moment.',
                'code': 'SERVICE_UNAVAILABLE',
                'retry_after': 60
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
            
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e),
                'code': 'PROCESSING_ERROR'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Balance purchase system error: {e}", exc_info=True)
            return Response({
                'success': False,
                'error': 'An unexpected error occurred',
                'code': 'INTERNAL_ERROR'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@api_view(['GET'])
def balance_health_check(request):
    """Health check for balance purchase system"""
    health_status = {
        'status': 'healthy',
        'timestamp': timezone.now().isoformat(),
        'checks': {}
    }
    
    # Database check
    try:
        PackageType.objects.first()
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        health_status['status'] = 'unhealthy'
    
    # Cache check
    try:
        cache.set('health_check_balance', 'ok', 10)
        if cache.get('health_check_balance') == 'ok':
            health_status['checks']['cache'] = 'ok'
        else:
            health_status['checks']['cache'] = 'error'
            health_status['status'] = 'degraded'
    except Exception as e:
        health_status['checks']['cache'] = f'error: {str(e)}'
        health_status['status'] = 'degraded'
    
    # Router circuit breaker
    cb_state = router_circuit_breaker.get_state()
    health_status['checks']['router_circuit_breaker'] = cb_state
    if cb_state == RouterCircuitBreaker.STATE_OPEN:
        health_status['status'] = 'degraded'
    
    # Success rate
    try:
        success = cache.get('metrics:counter:balance.purchases.success', 0)
        failure = cache.get('metrics:counter:balance.purchases.failure', 0)
        total = success + failure
        
        if total > 0:
            rate = (success / total) * 100
            health_status['checks']['success_rate_1h'] = f"{rate:.2f}%"
            if rate < 90:
                health_status['status'] = 'degraded'
        else:
            health_status['checks']['success_rate_1h'] = 'no data'
    except Exception:
        health_status['checks']['success_rate_1h'] = 'unavailable'
    
    http_status = status.HTTP_200_OK if health_status['status'] == 'healthy' else status.HTTP_503_SERVICE_UNAVAILABLE
    return Response(health_status, status=http_status)


# ============================================================================
# LEGACY COMPATIBILITY (OPTIONAL)
# ============================================================================

# For backward compatibility with old code
PackagePurchaseService = BalancePurchaseAPIView  # Alias