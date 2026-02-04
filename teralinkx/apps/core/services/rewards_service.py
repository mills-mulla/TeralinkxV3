# apps/core/services/rewards_service.py
from django.utils import timezone
from datetime import timedelta
import uuid
from decimal import Decimal

from packages.models import Coupon, PointTransaction
from users.models import ClientH


class RewardsService:
    """Service for managing reward points and redemptions"""
    
    # Reward catalog - points required for different rewards
    REWARD_CATALOG = [
        {'points': 100, 'discount': 5, 'name': '5% Discount', 'tier': None},
        {'points': 200, 'discount': 10, 'name': '10% Discount', 'tier': None},
        {'points': 300, 'discount': 15, 'name': '15% Discount', 'tier': 'silver'},
        {'points': 500, 'discount': 20, 'name': '20% Discount', 'tier': 'silver'},
        {'points': 1000, 'discount': 30, 'name': '30% Premium Discount', 'tier': 'gold'},
        {'points': 2000, 'discount': 50, 'name': '50% Platinum Discount', 'tier': 'platinum'},
    ]
    
    @classmethod
    def award_purchase_points(cls, user, amount_spent, voucher=None):
        """Award points for package purchase"""
        points = int(amount_spent)  # 1 point per KSh
        
        return user.award_points(
            points=points,
            transaction_type='earned_purchase',
            description=f'Earned {points} points from KSh {amount_spent} purchase',
            related_voucher=voucher
        )
    
    @classmethod
    def award_referral_points(cls, referrer, referee):
        """Award points for successful referral"""
        # Award referrer
        referrer_points = referrer.award_points(
            points=500,
            transaction_type='earned_referral',
            description=f'Referral bonus for inviting {referee.display_name}'
        )
        
        # Award referee
        referee_points = referee.award_points(
            points=200,
            transaction_type='earned_referral',
            description='Welcome bonus for joining via referral'
        )
        
        return referrer_points, referee_points
    
    @classmethod
    def get_available_rewards(cls, user):
        """Get rewards available to user based on points and tier"""
        available_rewards = []
        
        for reward in cls.REWARD_CATALOG:
            # Check if user has enough points
            if user.reward_points >= reward['points']:
                # Check tier requirement
                if reward['tier'] is None or cls._tier_meets_requirement(user.reward_tier, reward['tier']):
                    available_rewards.append({
                        **reward,
                        'can_redeem': True,
                        'reason': None
                    })
                else:
                    available_rewards.append({
                        **reward,
                        'can_redeem': False,
                        'reason': f'Requires {reward["tier"].title()} tier'
                    })
            else:
                points_needed = reward['points'] - user.reward_points
                available_rewards.append({
                    **reward,
                    'can_redeem': False,
                    'reason': f'Need {points_needed} more points'
                })
        
        return available_rewards
    
    @classmethod
    def redeem_discount_coupon(cls, user, points_cost, discount_percentage):
        """Redeem points for a discount coupon"""
        # Check if user has enough points
        success, message = user.redeem_points(points_cost, f'Redeemed {discount_percentage}% discount coupon')
        if not success:
            return False, message, None
        
        # Generate reward coupon
        coupon = Coupon.objects.create(
            code=f"REWARD-{uuid.uuid4().hex[:8].upper()}",
            name=f"{discount_percentage}% Reward Discount",
            description=f"Reward coupon redeemed for {points_cost} points",
            coupon_type='percentage',
            discount_value=Decimal(str(discount_percentage)),
            is_reward=True,
            points_cost=points_cost,
            auto_generated=True,
            max_uses=1,
            max_uses_per_user=1,
            valid_from=timezone.now(),
            valid_until=timezone.now() + timedelta(days=30)
        )
        
        # Update transaction with coupon reference
        latest_transaction = user.point_transactions.filter(
            transaction_type='redeemed_coupon'
        ).order_by('-created_at').first()
        
        if latest_transaction:
            latest_transaction.related_coupon = coupon
            latest_transaction.save()
        
        return True, f"Successfully redeemed {discount_percentage}% discount coupon", coupon
    
    @classmethod
    def get_user_reward_summary(cls, user):
        """Get comprehensive reward summary for user"""
        recent_transactions = user.point_transactions.order_by('-created_at')[:10]
        
        return {
            'current_points': user.reward_points,
            'current_tier': user.reward_tier,
            'total_earned': user.total_points_earned,
            'total_redeemed': user.total_points_redeemed,
            'next_tier_points': user.next_tier_points,
            'tier_progress': user.tier_progress_percentage,
            'available_rewards': cls.get_available_rewards(user),
            'recent_transactions': [
                {
                    'type': t.transaction_type,
                    'points': t.points,
                    'description': t.description,
                    'date': t.created_at.isoformat(),
                    'coupon_code': t.related_coupon.code if t.related_coupon else None
                }
                for t in recent_transactions
            ]
        }
    
    @classmethod
    def _tier_meets_requirement(cls, user_tier, required_tier):
        """Check if user tier meets requirement"""
        tier_hierarchy = ['bronze', 'silver', 'gold', 'platinum']
        user_level = tier_hierarchy.index(user_tier)
        required_level = tier_hierarchy.index(required_tier)
        return user_level >= required_level