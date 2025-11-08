from django.urls import path, include
from .packages import PackageAPIView
from .dispatch_voucher import DispatchVoucherAPIView
from .available_voucher import AvailableVoucherAPIView
# from .views import voucher_views, package_views

app_name = 'packages'

urlpatterns = [
    # Package Management
    path('packages/', PackageAPIView.as_view(), name='package-list-create'),
    # path('packages/<int:pk>/', package_views.PackageDetailAPIView.as_view(), name='package-detail'),
    # path('packages/featured/', package_views.FeaturedPackagesAPIView.as_view(), name='featured-packages'),
    # path('packages/category/<str:category>/', package_views.PackageByCategoryAPIView.as_view(), name='packages-by-category'),
    
    # Dispatch Voucher Management
    path('dispatch-vouchers/', DispatchVoucherAPIView.as_view(), name='dispatch-voucher-list-create'),
    # path('dispatch-vouchers/<int:pk>/', voucher_views.DispatchVoucherDetailAPIView.as_view(), name='dispatch-voucher-detail'),
    # path('dispatch-vouchers/user/<int:user_id>/', voucher_views.UserDispatchVouchersAPIView.as_view(), name='user-dispatch-vouchers'),
    # path('dispatch-vouchers/active/', voucher_views.ActiveDispatchVouchersAPIView.as_view(), name='active-dispatch-vouchers'),
    # path('dispatch-vouchers/validate/<str:voucher_code>/', voucher_views.ValidateDispatchVoucherAPIView.as_view(), name='validate-dispatch-voucher'),
    
    # # Available Voucher Management
    # path('available-vouchers/', AvailableVoucherAPIView.as_view(), name='available-voucher-list-create'),
    # path('available-vouchers/<int:pk>/', voucher_views.AvailableVoucherDetailAPIView.as_view(), name='available-voucher-detail'),
    # path('available-vouchers/batch/<str:batch_id>/', voucher_views.BatchVouchersAPIView.as_view(), name='batch-vouchers'),
    # path('available-vouchers/activate/<str:voucher_code>/', voucher_views.ActivateAvailableVoucherAPIView.as_view(), name='activate-available-voucher'),
    
    # Voucher Actions
    # path('vouchers/purchase/', voucher_views.PurchaseVoucherAPIView.as_view(), name='purchase-voucher'),
    # path('vouchers/usage/<str:voucher_code>/', voucher_views.VoucherUsageAPIView.as_view(), name='voucher-usage'),
    # path('vouchers/extend/<str:voucher_code>/', voucher_views.ExtendVoucherAPIView.as_view(), name='extend-voucher'),
]