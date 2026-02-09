# TeralinkxV3 Model Structure

## App Organization & Models

### 1. **users** - User Management
- `ClientH` - Main client/user model with balance, rewards, status
- `UserDevice` - User devices (MAC, IP, browser, OS)
- `UserSession` - Active user sessions with device tracking

### 2. **packages** - Package & Voucher Management
- `PackageType` - Internet packages (speed, duration, price)
- `PackageTypeLocation` - Package availability per location
- `DispatchVoucher` - Activated vouchers for users
- `AvailableVoucher` - Voucher pool/inventory
- `Coupon` - Discount coupons
- `CouponUsage` - Coupon usage tracking
- `PointTransaction` - Reward points transactions
- `FeaturedPromotion` - Promotional campaigns
- `FeaturedPromotionLocation` - Promotion availability per location

### 3. **finance** - Financial Management
- `Currency` - Multi-currency support (150+ currencies)
- `ExchangeRate` - Currency exchange rates
- `PaymentGateway` - Payment gateway configs (M-Pesa, Stripe, etc)
- `PaymentTransaction` - Successful payment records
- `BalanceTransaction` - Double-entry balance accounting
- `TransactionQueue` - Async payment processing queue
- `Investment` - Business investments tracking
- `Department` - Cost centers
- `BudgetCategory` - Budget planning
- `Expense` - Business expenses (CAPEX/OPEX)
- `FinancialReport` - Pre-generated financial reports
- `RevenueStream` - Revenue source analytics

### 4. **locations** - Location Management
- `Location` - Physical locations/hotspots

### 5. **notifications** - Notification System
- `Notification` - User notifications
- `NotificationTemplate` - Notification templates

### 6. **security** - Authentication & Security
- `PhoneOTP` - OTP verification
- `VerificationSession` - OTP sessions
- `AuthSession` - JWT auth sessions
- `SecurityLog` - Security audit logs
- `ISPEquipment` - Network equipment tracking
- `ISPEquipmentLog` - Equipment change logs

### 7. **analytics** - Analytics & Monitoring
- `ActiveSession` - Real-time active sessions
- `DataUsageRecord` - Data usage analytics
- `DHCPLease` - DHCP lease information

### 8. **ads** - Advertisement Management
- `Advertisement` - Ad campaigns
- `AdMedia` - Ad media files

### 9. **sync** - Data Synchronization
- `LocationSyncLog` - Location sync history
- `SyncConfiguration` - Sync settings
- `DataChangeLog` - Data change tracking

## Missing Models (To Be Created)

### For Refund System
- `RefundLog` - Refund transaction records
  - Fields: account, refund_amount, downtime_minutes, refund_type, created_at
  - Location: `analytics/models.py` or `finance/models.py`

- `DowntimeRecord` - Network downtime tracking
  - Fields: name, start_time, end_time, duration_minutes, severity, reason, affected_services
  - Location: `analytics/models.py`

## Current Serializers (analytics/superuser/serializers/)

### Existing:
- `user_serializers.py` - DjangoUserSerializer, UserDeviceSerializer, UserSessionSerializer
- `package_serializers.py` - PackageTypeSerializer, DispatchVoucherSerializer, CouponSerializer, FeaturedPromotionSerializer, PointTransactionSerializer
- `location_serializers.py` - LocationSerializer
- `serializers.py` - ClientSerializer, TransactionSerializer (PaymentTransaction)

### To Be Created:
- RefundLogSerializer
- DowntimeRecordSerializer

## Current ViewSets (analytics/superuser/views/)

### Existing:
- `auth.py` - AdminLoginView, TokenRefreshView, VerifyTokenView, CheckAuthView, AdminLogoutView
- `clientsview.py` - ClientViewSet
- `transactionsview.py` - TransactionViewSet (PaymentTransaction)
- `user_views.py` - DjangoUserViewSet, UserDeviceViewSet, UserSessionViewSet
- `package_views.py` - PackageTypeViewSet, DispatchVoucherViewSet, CouponViewSet, FeaturedPromotionViewSet, PointTransactionViewSet
- `location_views.py` - LocationViewSet
- `dashboard_metrics.py` - DashboardMetricsView, RevenueAnalyticsView, ClientGrowthView
- `systemstatusview.py` - SystemStatusView

### To Be Created:
- RefundViewSet (after creating RefundLog/DowntimeRecord models)

## API Endpoints (suapi/)

### Authentication
- POST `/suapi/auth/login/` - Admin JWT login
- POST `/suapi/token/refresh/` - Refresh JWT token
- GET `/suapi/auth/verify/` - Verify JWT token
- GET `/suapi/auth/check/` - Check auth status
- POST `/suapi/auth/logout/` - Logout

### Resources (CRUD)
- `/suapi/clients/` - ClientH management
- `/suapi/transactions/` - PaymentTransaction management
- `/suapi/users/` - Django User management
- `/suapi/devices/` - UserDevice management
- `/suapi/sessions/` - UserSession management
- `/suapi/packages/` - PackageType management
- `/suapi/vouchers/` - DispatchVoucher management
- `/suapi/coupons/` - Coupon management
- `/suapi/promotions/` - FeaturedPromotion management
- `/suapi/point-transactions/` - PointTransaction management
- `/suapi/locations/` - Location management

### Analytics
- GET `/suapi/dashboard-metrics/` - Dashboard stats
- GET `/suapi/dashboard-metrics/revenue-analytics/` - Revenue analytics
- GET `/suapi/dashboard-metrics/client-growth/` - Client growth
- GET `/suapi/system-status/` - System status

## Frontend Pages (adminstration/src/views/)

### Existing:
- Dashboard.vue
- Clients.vue
- Users.vue
- Devices.vue
- Sessions.vue
- Packages.vue
- Vouchers.vue
- Coupons.vue
- Promotions.vue
- PointTransactions.vue
- Locations.vue
- Transactions.vue

### To Be Created:
- Refunds.vue (after backend models are ready)

## Next Steps

1. **Create Missing Models**
   - Add RefundLog to analytics/models.py
   - Add DowntimeRecord to analytics/models.py
   - Run migrations

2. **Create Refund Serializers**
   - RefundLogSerializer
   - DowntimeRecordSerializer

3. **Create Refund ViewSet**
   - RefundViewSet with stats, eligible_clients, process_individual, batch_refund actions

4. **Update URLs**
   - Register RefundViewSet in router
   - Add custom refund endpoints

5. **Create Frontend**
   - Refunds.vue page
   - Update router and sidebar

## Import Patterns

```python
# Users
from users.models import ClientH, UserDevice, UserSession

# Packages
from packages.models import PackageType, DispatchVoucher, Coupon, FeaturedPromotion, PointTransaction

# Finance
from finance.models import PaymentTransaction, TransactionQueue, Currency, PaymentGateway

# Locations
from locations.models import Location

# Analytics
from analytics.models import ActiveSession, DataUsageRecord, DHCPLease

# Security
from security.models import AuthSession, SecurityLog

# Notifications
from notifications.models import Notification
```
