from django.db import transaction
from django.core.exceptions import ValidationError
from packages.models import Coupon, CouponUsage, PackageType

class CouponService:
    """Service for handling coupon operations"""
    
    @staticmethod
    def validate_coupon(code, user, package):
        """Validate if coupon can be applied"""
        try:
            coupon = Coupon.objects.get(code=code.upper())
        except Coupon.DoesNotExist:
            return False, "Invalid coupon code"
        
        # Check basic validity
        if not coupon.is_valid:
            return False, "Coupon is expired or inactive"
        
        # Check user usage limit
        user_uses = CouponUsage.get_user_usage_count(user, coupon)
        if user_uses >= coupon.max_uses_per_user:
            return False, f"Maximum uses ({coupon.max_uses_per_user}) reached"
        
        # Check if applicable to package
        can_apply, message = coupon.can_apply_to_package(package)
        if not can_apply:
            return False, message
        
        # Check minimum purchase amount
        if coupon.min_purchase_amount and package.price < coupon.min_purchase_amount:
            return False, f"Minimum purchase of {coupon.min_purchase_amount} required"
        
        return True, "Valid coupon"
    
    @staticmethod
    @transaction.atomic
    def apply_coupon(code, user, package, voucher=None):
        """Apply coupon and create usage record"""
        # Validate
        is_valid, message = CouponService.validate_coupon(code, user, package)
        if not is_valid:
            raise ValidationError(message)
        
        coupon = Coupon.objects.get(code=code.upper())
        
        # Calculate discount
        discount = coupon.calculate_discount(package.price)
        final_price = package.price - discount
        
        # Create usage record
        usage = CouponUsage.objects.create(
            coupon=coupon,
            user=user,
            package=package,
            voucher=voucher,
            original_price=package.price,
            discount_amount=discount,
            final_price=final_price,
        )
        
        # Increment coupon usage
        coupon.increment_use()
        
        return usage, discount, final_price
    
    @staticmethod
    def get_available_coupons_for_package(user, package):
        """Get all valid coupons for a specific package"""
        coupons = Coupon.objects.filter(is_valid=True)
        
        available = []
        for coupon in coupons:
            can_apply, message = coupon.can_apply_to_package(package)
            if can_apply:
                # Check user hasn't exceeded limit
                user_uses = CouponUsage.get_user_usage_count(user, coupon)
                if user_uses < coupon.max_uses_per_user:
                    available.append({
                        'code': coupon.code,
                        'name': coupon.name,
                        'description': coupon.description,
                        'coupon_type': coupon.coupon_type,
                        'discount_value': float(coupon.discount_value),
                        'max_uses_per_user': coupon.max_uses_per_user,
                        'user_uses': user_uses,
                    })
        
        return available