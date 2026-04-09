from django.urls import path, include
from .packages import PackageAPIView,FeaturedPackagesAPIView,PackageDetailAPIView,PackageCreateAPIView
from .dispatch_voucher import DispatchVoucherAPIView
from .rewards_views import get_reward_summary, get_available_rewards, redeem_reward, get_point_history, get_user_coupons
from .coupon_views import validate_coupon, apply_coupon
# from .available_voucher import 
# from .views import voucher_views, package_views

app_name = 'packages'

urlpatterns = [
    # Package Management
    path('packages/', PackageAPIView.as_view(), name='package-list-create'),
    path('featurepackages/', FeaturedPackagesAPIView.as_view(), name='package-list-featured'),
    path('packagesdetail/', PackageDetailAPIView.as_view(), name='package-list-detail'),
    path('packagescreate/', PackageCreateAPIView.as_view(), name='package-list-create'),
    path('vouchers/', DispatchVoucherAPIView.as_view(), name='dispatch-voucher-list-create'),
    
    # Rewards System
    path('rewards/summary/', get_reward_summary, name='reward-summary'),
    path('rewards/available/', get_available_rewards, name='available-rewards'),
    path('rewards/redeem/', redeem_reward, name='redeem-reward'),
    path('rewards/coupons/', get_user_coupons, name='user-coupons'),
    path('rewards/history/', get_point_history, name='point-history'),
    
    # Coupon Management
    path('coupons/validate/', validate_coupon, name='validate-coupon'),
    path('coupons/apply/', apply_coupon, name='apply-coupon'),
      
]