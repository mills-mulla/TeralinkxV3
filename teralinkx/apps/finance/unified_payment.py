# apps/finance/unified_payment.py
import logging
from decimal import Decimal
from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from users.models import ClientH
from packages.models import PackageType, Coupon
from .credit_balance import BalancePurchaseProcessor
from .payment_gateway import MpesaGatewayHelper, TransactionQueueHelper
from .models import TransactionQueue

logger = logging.getLogger(__name__)

class UnifiedPaymentAPIView(APIView):
    """Unified payment endpoint handling credit, M-Pesa, and mixed payments"""
    
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Process unified payment request"""
        
        data = request.data
        payment_method = data.get('payment_method')  # 'credit', 'mpesa', 'mixed'
        package_id = data.get('package_id')
        coupon_code = data.get('coupon_code')
        use_credit = data.get('use_credit', True)  # Check if user wants to use credit
        
        
        # Validate required fields
        if not all([payment_method, package_id]):
            return Response({
                'success': False,
                'error': 'Missing required fields: payment_method, package_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get package
        try:
            package = PackageType.objects.get(id=package_id)
        except PackageType.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Package not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get user context
        try:
            from .credit_balance import BalanceUserContextExtractor
            user_context = BalanceUserContextExtractor.extract_user_data(request)
        except Exception as e:
            return Response({
                'success': False,
                'error': f'User context error: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Calculate final price with coupon
        final_price, applied_coupon = self.calculate_final_price(package, coupon_code)
        
        # Override payment method if user doesn't want to use credit
        if not use_credit and payment_method in ['credit', 'mixed']:
            payment_method = 'mpesa'
            
        
        # Route to appropriate payment handler
        if payment_method == 'credit':
            return self.handle_credit_payment(user_context, package, final_price, applied_coupon)
        elif payment_method == 'mpesa':
            return self.handle_mpesa_payment(request, user_context, package, final_price, applied_coupon)
        elif payment_method == 'mixed':
            return self.handle_mixed_payment(request, user_context, package, final_price, applied_coupon)
        else:
            return Response({
                'success': False,
                'error': 'Invalid payment method'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def calculate_final_price(self, package, coupon_code):
        """Calculate final price with coupon discount, ensuring M-Pesa compatibility (whole numbers)"""
        base_price = package.price
        applied_coupon = None
        
        if coupon_code:
            try:
                coupon = Coupon.objects.get(code=coupon_code, is_active=True)
                
                # Validate coupon
                if coupon.valid_until < timezone.now():
                    raise ValueError('Coupon has expired')
                
                if coupon.total_uses >= coupon.max_uses:
                    raise ValueError('Coupon usage limit reached')
                
                # Calculate discount with M-Pesa compatibility
                if coupon.coupon_type == 'percentage':
                    # Calculate discount amount
                    discount_amount = base_price * (coupon.discount_value / 100)
                    
                    # 🔴 DYNAMIC M-PESA DISCOUNT ROUNDING SYSTEM
                    # For expensive packages (≥50 KES): Round UP (ceiling) - more generous
                    # For cheap packages (<50 KES): Round DOWN (floor) - conservative
                    if base_price >= 50:
                        # Expensive packages: Round UP for better customer experience
                        import math
                        discount_amount = Decimal(str(math.ceil(float(discount_amount))))
                        logger.info(f"Expensive package ({base_price} KES): Using ceiling discount")
                    else:
                        # Cheap packages: Round DOWN to maintain profitability
                        import math
                        discount_amount = Decimal(str(math.floor(float(discount_amount))))
                        logger.info(f"Budget package ({base_price} KES): Using floor discount")
                    
                    # Ensure discount doesn't exceed base price
                    discount_amount = min(discount_amount, base_price)
                else:
                    # Fixed amount discount - already whole number
                    discount_amount = min(coupon.discount_value, base_price)
                
                final_price = base_price - discount_amount
                
                # Ensure final price is not negative
                final_price = max(Decimal('1'), final_price)  # Minimum 1 KES
                
                applied_coupon = coupon
                
                logger.info(f"Applied coupon {coupon_code}: {base_price} -> {final_price} (M-Pesa compatible)")
                return final_price, applied_coupon
                
            except Coupon.DoesNotExist:
                raise ValueError('Invalid coupon code')
        
        return base_price, applied_coupon
    
    def handle_credit_payment(self, user_context, package, final_price, applied_coupon):
        """Handle pure credit payment"""
        try:
            # Check sufficient balance
            client = user_context['client']
            if client.balance < final_price:
                return Response({
                    'success': False,
                    'error': 'Insufficient balance',
                    'required': float(final_price),
                    'available': float(client.balance),
                    'shortage': float(final_price - client.balance)
                }, status=status.HTTP_402_PAYMENT_REQUIRED)
            
            # Use existing balance purchase processor
            result = BalancePurchaseProcessor.process_purchase(
                user_context=user_context,
                package=package,
                hotspot_ip=None,
                auto_login=True,
                coupon_code=applied_coupon.code if applied_coupon else None
            )
            
            # Mark coupon as used
            if applied_coupon:
                self.mark_coupon_used(applied_coupon)
            
            return Response({
                'success': True,
                'payment_method': 'credit',
                'transaction_id': result.get('transaction_id'),
                'voucher_code': result.get('voucher_code'),
                'amount_paid': float(final_price),
                'balance_after': float(client.balance - final_price)
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            logger.error(f"Credit payment error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def handle_mpesa_payment(self, request, user_context, package, final_price, applied_coupon):
        """Handle pure M-Pesa payment"""
        try:
            phone_number = request.data.get('phone_number')
            if not phone_number:
                # Try to get from JWT
                jwt_payload = getattr(request.auth, 'payload', {})
                phone_number = jwt_payload.get('phone_number')
            
            if not phone_number:
                return Response({
                    'success': False,
                    'error': 'Phone number required for M-Pesa payment'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            client = user_context['client']
            
                
            # Initiate M-Pesa payment
            result = MpesaGatewayHelper.initiate_stk_push(
                phone=phone_number,
                amount=int(final_price),
                account_reference=f"TERALINKX_WAVES_{client.account}",
                description=f"Payment for {package.name}",
                package_data=[{
                    'package': package.name,
                    'pkg_code': package.code,
                    'price': float(final_price)
                }]
            )
            
            if not result.get('success'):
                return Response({
                    'success': False,
                    'error': result.get('error', 'M-Pesa initiation failed')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create queue item with ZERO used_credit for pure M-Pesa
            queue_item = TransactionQueueHelper.create_payment_queue(
                user=client,
                package_code=package.code,
                initiator_phone=phone_number,
                checkout_id=result.get('checkout_request_id'),
                recipient_account=client.account,
                package_name=package.name,
                price=final_price,
                used_credit=0,  # 🔍 EXPLICIT ZERO for pure M-Pesa
                result=result
            )
            
            
            # Store coupon info in queue metadata
            if applied_coupon:
                queue_item.metadata['coupon_code'] = applied_coupon.code
                queue_item.metadata['original_price'] = float(package.price)
                queue_item.metadata['discount_amount'] = float(package.price - final_price)
                queue_item.save()
            
            return Response({
                'success': True,
                'payment_method': 'mpesa',
                'checkout_request_id': result.get('checkout_request_id'),
                'merchant_request_id': result.get('merchant_request_id'),
                'customer_message': result.get('customer_message'),
                'amount_to_pay': float(final_price)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"M-Pesa payment error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def handle_mixed_payment(self, request, user_context, package, final_price, applied_coupon):
        """Handle mixed credit + M-Pesa payment"""
        try:
            credit_amount = Decimal(str(request.data.get('credit_amount', '0')))
            phone_number = request.data.get('phone_number')
            
            if not phone_number:
                jwt_payload = getattr(request.auth, 'payload', {})
                phone_number = jwt_payload.get('phone_number')
            
            if not phone_number:
                return Response({
                    'success': False,
                    'error': 'Phone number required for mixed payment'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            client = user_context['client']
            
            # Validate credit amount
            if credit_amount > client.balance:
                return Response({
                    'success': False,
                    'error': 'Insufficient balance for credit portion'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            if credit_amount > final_price:
                return Response({
                    'success': False,
                    'error': 'Credit amount cannot exceed package price'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            mpesa_amount = final_price - credit_amount
            
            if mpesa_amount <= 0:
                # If M-Pesa amount is 0, redirect to credit payment
                return self.handle_credit_payment(user_context, package, final_price, applied_coupon)
            
            # Initiate M-Pesa for remaining amount
            result = MpesaGatewayHelper.initiate_stk_push(
                phone=phone_number,
                amount=int(mpesa_amount),
                account_reference=f"TERALINKX_WAVES_{client.account}",
                description=f"Payment for {package.name} (Mixed)",
                package_data=[{
                    'package': package.name,
                    'pkg_code': package.code,
                    'price': float(final_price),
                    'credit_used': float(credit_amount),
                    'mpesa_amount': float(mpesa_amount)
                }]
            )
            
            if not result.get('success'):
                return Response({
                    'success': False,
                    'error': result.get('error', 'M-Pesa initiation failed')
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Create queue item with mixed payment info
            queue_item = TransactionQueueHelper.create_payment_queue(
                user=client,
                package_code=package.code,
                initiator_phone=phone_number,
                checkout_id=result.get('checkout_request_id'),
                recipient_account=client.account,
                package_name=package.name,
                price=final_price,
                used_credit=credit_amount,
                result=result
            )
            
            # method is already set to 'mpesa+balance' in create_payment_queue
            queue_item.metadata.update({
                'payment_breakdown': {
                    'total_amount': float(final_price),
                    'credit_amount': float(credit_amount),
                    'mpesa_amount': float(mpesa_amount)
                }
            })
            
            if applied_coupon:
                queue_item.metadata['coupon_code'] = applied_coupon.code
                queue_item.metadata['original_price'] = float(package.price)
                queue_item.metadata['discount_amount'] = float(package.price - final_price)
            
            queue_item.save()
            
            return Response({
                'success': True,
                'payment_method': 'mixed',
                'checkout_request_id': result.get('checkout_request_id'),
                'merchant_request_id': result.get('merchant_request_id'),
                'customer_message': result.get('customer_message'),
                'payment_breakdown': {
                    'total_amount': float(final_price),
                    'credit_amount': float(credit_amount),
                    'mpesa_amount': float(mpesa_amount)
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Mixed payment error: {e}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def mark_coupon_used(self, coupon):
        """Mark coupon as used"""
        try:
            coupon.total_uses += 1
            if coupon.total_uses >= coupon.max_uses:
                coupon.is_active = False
            coupon.save()
            logger.info(f"Coupon {coupon.code} marked as used")
        except Exception as e:
            logger.error(f"Error marking coupon as used: {e}")