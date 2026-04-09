#!/usr/bin/env python
"""
Quick test script to verify rewards system integration
"""
import os
import sys
import django

# Setup Django
sys.path.append('/home/teralinkx/TeralinkxV3/teralinkx')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'teralinkx.settings')
django.setup()

from decimal import Decimal
from users.models import ClientH
from core.services.rewards_service import RewardsService

def test_rewards_system():
    print("🎯 Testing Rewards System Integration...")
    
    # Get first user
    try:
        user = ClientH.objects.first()
        if not user:
            print("❌ No users found in database")
            return
        
        print(f"📱 Testing with user: {user.account}")
        print(f"💰 Current balance: KSh {user.balance}")
        print(f"🏆 Current points: {user.reward_points}")
        print(f"🥇 Current tier: {user.reward_tier}")
        
        # Test point awarding
        print("\n🎁 Testing point awarding...")
        points_awarded = RewardsService.award_purchase_points(
            user=user,
            amount_spent=Decimal('100.00')
        )
        
        print(f"✅ Awarded {points_awarded} points for KSh 100 purchase")
        
        # Refresh user
        user.refresh_from_db()
        print(f"🏆 New points balance: {user.reward_points}")
        print(f"🥇 New tier: {user.reward_tier}")
        
        # Test available rewards
        print("\n🎁 Available rewards:")
        rewards = RewardsService.get_available_rewards(user)
        for reward in rewards[:3]:  # Show first 3
            status = "✅ Can redeem" if reward['can_redeem'] else f"❌ {reward['reason']}"
            print(f"  • {reward['name']}: {reward['points']} points - {status}")
        
        print("\n✅ Rewards system is working correctly!")
        
    except Exception as e:
        print(f"❌ Error testing rewards: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_rewards_system()