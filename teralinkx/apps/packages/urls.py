from django.urls import path, include
from .packages import PackageAPIView,FeaturedPackagesAPIView,PackageDetailAPIView,PackageCreateAPIView
from .dispatch_voucher import DispatchVoucherAPIView
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
      
]