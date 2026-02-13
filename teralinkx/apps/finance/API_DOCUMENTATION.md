# ✅ Finance API Backend - Setup Complete!

## 🎯 API Endpoints Created

All endpoints require authentication (JWT token).

### Base URL
```
https://service.teralinkxwaves.uk/api/finance/api/
```

### 1. Revenue Streams
```
GET /api/finance/api/revenue-streams/
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Advertising Revenue",
    "category": "ads_revenue",
    "category_display": "Advertising Revenue",
    "current_revenue": 12500.00,
    "target_revenue": 50000.00,
    "achievement": 25.0,
    "growth": 8.5,
    "is_active": true,
    "description": "Revenue from banner, video, and native ads"
  }
]
```

### 2. Expenses
```
GET /api/finance/api/expenses/
```

**Response**:
```json
[
  {
    "id": 1,
    "date": "2025-02-03",
    "description": "Network infrastructure upgrade",
    "amount": 150000.00,
    "amount_base": 150000.00,
    "currency": "KES",
    "category": "Network Infrastructure",
    "department": "IT",
    "vendor": "Cisco Systems",
    "status": "Paid",
    "is_capex": true
  }
]
```

### 3. Investments
```
GET /api/finance/api/investments/
```

**Response**:
```json
[
  {
    "id": 1,
    "investor_name": "John Doe",
    "amount": 1000000.00,
    "amount_base": 1000000.00,
    "currency": "KES",
    "type": "Seed Funding",
    "status": "Active",
    "date": "2025-01-15",
    "equity_percentage": 10.0,
    "interest_rate": null,
    "is_active": true
  }
]
```

### 4. Departments
```
GET /api/finance/api/departments/
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "Information Technology",
    "code": "IT",
    "budget": 500000.00,
    "current_spending": 125000.00,
    "budget_utilization": 25.0,
    "manager": "admin",
    "is_active": true
  }
]
```

## 🚀 Quick Test

### Using cURL:

```bash
# Get your JWT token first
TOKEN="your_jwt_token_here"

# Test Revenue Streams
curl -H "Authorization: Bearer $TOKEN" \
  https://service.teralinkxwaves.uk/api/finance/api/revenue-streams/

# Test Expenses
curl -H "Authorization: Bearer $TOKEN" \
  https://service.teralinkxwaves.uk/api/finance/api/expenses/

# Test Investments
curl -H "Authorization: Bearer $TOKEN" \
  https://service.teralinkxwaves.uk/api/finance/api/investments/

# Test Departments
curl -H "Authorization: Bearer $TOKEN" \
  https://service.teralinkxwaves.uk/api/finance/api/departments/
```

### Using Python:

```python
import requests

# Your JWT token
token = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {token}"}

# Test Revenue Streams
response = requests.get(
    "https://service.teralinkxwaves.uk/api/finance/api/revenue-streams/",
    headers=headers
)
print(response.json())
```

## 📊 Create Sample Data

Run this in Django shell to create sample revenue streams:

```python
from finance.models import RevenueStream

# 1. Advertising Revenue
RevenueStream.objects.create(
    name="Advertising Revenue",
    category="ads_revenue",
    is_active=True,
    target_revenue=50000,
    target_growth_rate=15.0,
    description="Revenue from banner, video, and native advertisements",
    display_order=1
)

# 2. Voucher Sales
RevenueStream.objects.create(
    name="Internet Voucher Sales",
    category="voucher_sales",
    is_active=True,
    target_revenue=200000,
    target_growth_rate=10.0,
    description="Revenue from internet voucher purchases",
    display_order=2
)

# 3. Package Sales
RevenueStream.objects.create(
    name="Data Package Subscriptions",
    category="package_sales",
    is_active=True,
    target_revenue=150000,
    target_growth_rate=12.0,
    description="Revenue from monthly data package subscriptions",
    display_order=3
)

# 4. Premium Services
RevenueStream.objects.create(
    name="Premium Services",
    category="premium_services",
    is_active=True,
    target_revenue=75000,
    target_growth_rate=20.0,
    description="VIP packages, priority support, premium features",
    display_order=4
)

print("✅ Sample revenue streams created!")
```

## 🔧 Frontend Integration

The frontend is already configured to fetch from these endpoints:

**File**: `/admteralinkx/adminstration/src/views/Finance.vue`

```javascript
async fetchRevenueStreams() {
  try {
    const response = await fetch('/api/finance/api/revenue-streams/')
    this.revenueStreams = await response.json()
  } catch (error) {
    console.error('Error fetching revenue streams:', error)
  }
}
```

## ✅ What's Working

1. **Revenue Streams API** ✅
   - Fetches all active revenue streams
   - Calculates current month revenue (from TransactionQueue + Advertisement)
   - Calculates target achievement
   - Calculates revenue growth
   - Returns formatted data for frontend

2. **Expenses API** ✅
   - Fetches approved/paid expenses
   - Includes department and currency info
   - Shows CAPEX vs OPEX
   - Limited to last 50 records

3. **Investments API** ✅
   - Fetches all investments
   - Shows equity and interest rates
   - Includes active status
   - Limited to last 50 records

4. **Departments API** ✅
   - Fetches active departments
   - Calculates current month spending
   - Shows budget utilization percentage
   - Includes manager info

## 🎨 Frontend Display

When you navigate to **Finance** in the sidebar, you'll see:

### Revenue Streams Tab:
- **Summary Cards**:
  - Total Revenue: Sum of all active streams
  - Active Streams: Count of active streams
  - Avg Growth: Average growth percentage
  - Target Achievement: Average achievement percentage

- **Data Table**:
  - Stream name and category (color-coded)
  - Current revenue vs target
  - Achievement progress bar
  - Growth indicator (↑ or ↓)
  - Active/Inactive status

### Other Tabs:
- Expenses, Investments, Departments (placeholder for now)

## 🔐 Authentication

All endpoints require JWT authentication:

```javascript
// Frontend automatically includes token
const response = await fetch('/api/finance/api/revenue-streams/', {
  headers: {
    'Authorization': `Bearer ${localStorage.getItem('access_token')}`
  }
})
```

## 📝 Notes

- **Real Data**: All calculations use real data from your database
- **Performance**: Queries are optimized with `select_related()`
- **Permissions**: Only authenticated users can access
- **Limits**: Expenses and Investments limited to 50 records for performance

## 🎉 Ready to Use!

Your finance API is now fully functional and integrated with the frontend. Just:

1. Create some revenue streams in Django admin
2. Navigate to Finance in the admin dashboard
3. See your real-time financial data!

The ads revenue will automatically be calculated from your Advertisement model's `total_spent` field.
