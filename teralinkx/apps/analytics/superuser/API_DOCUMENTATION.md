# SUPERUSER API ENDPOINTS DOCUMENTATION

Base URL: `https://service.teralinkxwaves.uk/suapi/`

## Authentication Endpoints
- `POST /suapi/auth/login/` - Admin login
- `POST /suapi/auth/logout/` - Admin logout
- `GET /suapi/auth/check/` - Check authentication status
- `POST /suapi/auth/verify/` - Verify token
- `POST /suapi/token/` - Obtain JWT token pair
- `POST /suapi/token/refresh/` - Refresh JWT token

---

## Dashboard & Analytics
- `GET /suapi/dashboard-metrics/` - Get dashboard metrics
- `GET /suapi/dashboard-metrics/revenue-analytics/?period=7d` - Revenue analytics (7d, 30d, 90d)
- `GET /suapi/dashboard-metrics/client-growth/?period=30d` - Client growth analytics
- `GET /suapi/system-status/` - System status and health

---

## Clients (ClientH)
- `GET /suapi/clients/` - List all clients (with pagination, search, filters)
- `POST /suapi/clients/` - Create new client
- `GET /suapi/clients/{id}/` - Get single client
- `PUT /suapi/clients/{id}/` - Update client
- `PATCH /suapi/clients/{id}/` - Partial update client
- `DELETE /suapi/clients/{id}/` - Delete client
- `GET /suapi/clients/stats/` - Get client statistics
- `GET /suapi/clients/eligible_for_refund/` - Get clients eligible for refund

**Query Parameters:**
- `search` - Search by account, username, email
- `ordering` - Sort by fields (e.g., `-created_at`)
- `page` - Page number
- `page_size` - Items per page

---

## Users (Django User)
- `GET /suapi/users/` - List all users
- `POST /suapi/users/` - Create new user
- `GET /suapi/users/{id}/` - Get single user
- `PUT /suapi/users/{id}/` - Update user
- `PATCH /suapi/users/{id}/` - Partial update user
- `DELETE /suapi/users/{id}/` - Delete user
- `GET /suapi/users/stats/` - Get user statistics

**Query Parameters:**
- `search` - Search by username, email, first_name, last_name
- `ordering` - Sort by id, username, date_joined, last_login

---

## Devices (UserDevice)
- `GET /suapi/devices/` - List all devices
- `POST /suapi/devices/` - Create new device
- `GET /suapi/devices/{id}/` - Get single device
- `PUT /suapi/devices/{id}/` - Update device
- `PATCH /suapi/devices/{id}/` - Partial update device
- `DELETE /suapi/devices/{id}/` - Delete device
- `GET /suapi/devices/stats/` - Get device statistics
- `POST /suapi/devices/{id}/block/` - Block a device
- `POST /suapi/devices/{id}/unblock/` - Unblock a device

**Query Parameters:**
- `search` - Search by mac_address, device_name, user__account
- `status` - Filter by status (active, inactive, suspended)
- `user_id` - Filter by user ID
- `online_only` - Filter online devices (true/false)

---

## Sessions (UserSession)
- `GET /suapi/sessions/` - List all sessions
- `POST /suapi/sessions/` - Create new session
- `GET /suapi/sessions/{id}/` - Get single session
- `PUT /suapi/sessions/{id}/` - Update session
- `PATCH /suapi/sessions/{id}/` - Partial update session
- `DELETE /suapi/sessions/{id}/` - Delete session
- `GET /suapi/sessions/stats/` - Get session statistics
- `POST /suapi/sessions/{id}/terminate/` - Terminate a session

**Query Parameters:**
- `search` - Search by session_id, user__account, device__device_name, ip_address
- `is_active` - Filter by active status (true/false)
- `user_id` - Filter by user ID
- `device_id` - Filter by device ID

---

## Packages (PackageType)
- `GET /suapi/packages/` - List all packages
- `POST /suapi/packages/` - Create new package
- `GET /suapi/packages/{id}/` - Get single package
- `PUT /suapi/packages/{id}/` - Update package
- `PATCH /suapi/packages/{id}/` - Partial update package
- `DELETE /suapi/packages/{id}/` - Delete package
- `GET /suapi/packages/stats/` - Get package statistics

**Query Parameters:**
- `search` - Search by name, description, category
- `is_active` - Filter by active status (true/false)
- `category` - Filter by category
- `tier` - Filter by tier

---

## Vouchers (DispatchVoucher)
- `GET /suapi/vouchers/` - List all vouchers
- `POST /suapi/vouchers/` - Create new voucher
- `GET /suapi/vouchers/{id}/` - Get single voucher
- `PUT /suapi/vouchers/{id}/` - Update voucher
- `PATCH /suapi/vouchers/{id}/` - Partial update voucher
- `DELETE /suapi/vouchers/{id}/` - Delete voucher
- `GET /suapi/vouchers/stats/` - Get voucher statistics

**Query Parameters:**
- `search` - Search by voucher_code, dispatch_account, clienth__account
- `status` - Filter by status
- `client_id` - Filter by client ID
- `expired` - Filter expired vouchers (true/false)

---

## Coupons
- `GET /suapi/coupons/` - List all coupons
- `POST /suapi/coupons/` - Create new coupon
- `GET /suapi/coupons/{id}/` - Get single coupon
- `PUT /suapi/coupons/{id}/` - Update coupon
- `PATCH /suapi/coupons/{id}/` - Partial update coupon
- `DELETE /suapi/coupons/{id}/` - Delete coupon
- `GET /suapi/coupons/stats/` - Get coupon statistics

**Query Parameters:**
- `search` - Search by code, name, description
- `is_active` - Filter by active status (true/false)
- `is_reward` - Filter reward coupons (true/false)
- `valid_only` - Filter valid coupons (true/false)

---

## Promotions (FeaturedPromotion)
- `GET /suapi/promotions/` - List all promotions
- `POST /suapi/promotions/` - Create new promotion
- `GET /suapi/promotions/{id}/` - Get single promotion
- `PUT /suapi/promotions/{id}/` - Update promotion
- `PATCH /suapi/promotions/{id}/` - Partial update promotion
- `DELETE /suapi/promotions/{id}/` - Delete promotion
- `GET /suapi/promotions/stats/` - Get promotion statistics

**Query Parameters:**
- `search` - Search by name, headline, description
- `is_active` - Filter by active status (true/false)
- `live_only` - Filter live promotions (true/false)

---

## Point Transactions
- `GET /suapi/point-transactions/` - List all point transactions
- `POST /suapi/point-transactions/` - Create new point transaction
- `GET /suapi/point-transactions/{id}/` - Get single point transaction
- `PUT /suapi/point-transactions/{id}/` - Update point transaction
- `PATCH /suapi/point-transactions/{id}/` - Partial update point transaction
- `DELETE /suapi/point-transactions/{id}/` - Delete point transaction
- `GET /suapi/point-transactions/stats/` - Get point transaction statistics

**Query Parameters:**
- `search` - Search by user__account, description, transaction_type
- `user_id` - Filter by user ID
- `transaction_type` - Filter by transaction type

---

## Locations
- `GET /suapi/locations/` - List all locations
- `POST /suapi/locations/` - Create new location
- `GET /suapi/locations/{id}/` - Get single location
- `PUT /suapi/locations/{id}/` - Update location
- `PATCH /suapi/locations/{id}/` - Partial update location
- `DELETE /suapi/locations/{id}/` - Delete location
- `GET /suapi/locations/stats/` - Get location statistics

**Query Parameters:**
- `search` - Search by name, address, city, region
- `is_active` - Filter by active status (true/false)
- `region` - Filter by region

---

## Transactions
- `GET /suapi/transactions/` - List all transactions
- `POST /suapi/transactions/` - Create new transaction
- `GET /suapi/transactions/{id}/` - Get single transaction
- `PUT /suapi/transactions/{id}/` - Update transaction
- `PATCH /suapi/transactions/{id}/` - Partial update transaction
- `DELETE /suapi/transactions/{id}/` - Delete transaction

---

## Refunds
- `GET /suapi/refunds/stats/` - Get refund statistics
- `GET /suapi/refunds/eligible-clients/` - Get eligible clients for refund
- `GET /suapi/refunds/client-details/{account}/` - Get client refund details
- `POST /suapi/refunds/process-individual/` - Process individual refund
- `POST /suapi/refunds/batch-refund/` - Process batch refund
- `GET /suapi/refunds/history/` - Get refund history
- `GET /suapi/refunds/recent-downtimes/` - Get recent downtimes
- `POST /suapi/refunds/record-downtime/` - Record new downtime
- `GET /suapi/refunds/downtime-stats/` - Get downtime statistics
- `GET /suapi/refunds/ongoing-downtimes/` - Get ongoing downtimes
- `GET /suapi/refunds/critical-downtimes/` - Get critical downtimes

---

## Common Response Format

### Success Response
```json
{
  "count": 100,
  "next": "https://service.teralinkxwaves.uk/suapi/clients/?page=2",
  "previous": null,
  "results": [...]
}
```

### Error Response
```json
{
  "error": "Error message here",
  "detail": "Detailed error information"
}
```

---

## Pagination
All list endpoints support pagination:
- Default page size: 10
- Max page size: 100
- Use `?page=2` for next page
- Use `?page_size=20` to change page size

---

## Filtering & Search
- Use `?search=keyword` for full-text search
- Use `?ordering=-created_at` for sorting (prefix with `-` for descending)
- Use specific filters as documented per endpoint

---

## Authentication
All endpoints require authentication. Include JWT token in header:
```
Authorization: Bearer <your_token_here>
```

Or use session authentication with cookies.
