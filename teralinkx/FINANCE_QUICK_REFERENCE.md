# 🚀 Finance Management - Quick Reference

## ⚡ Quick Start (3 Steps)

### 1. Create Sample Data
```bash
docker exec -it teralinkx_web python manage.py create_sample_streams
```

### 2. Test API
```bash
# In browser or Postman
GET https://service.teralinkxwaves.uk/api/finance/api/revenue-streams/
Authorization: Bearer YOUR_JWT_TOKEN
```

### 3. View in Dashboard
- Open admin dashboard
- Click **Finance** in sidebar
- See your revenue streams!

## 📍 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/finance/api/revenue-streams/` | GET | All active revenue streams |
| `/api/finance/api/expenses/` | GET | Approved/paid expenses |
| `/api/finance/api/investments/` | GET | All investments |
| `/api/finance/api/departments/` | GET | Active departments |

## 💰 Revenue Categories

| Category | Color | Description |
|----------|-------|-------------|
| `ads_revenue` | Pink | Advertising revenue from ads |
| `voucher_sales` | Blue | Internet voucher sales |
| `package_sales` | Purple | Data package subscriptions |
| `usage_charges` | Emerald | Pay-as-you-go usage |
| `premium_services` | Amber | VIP/premium features |
| `value_added` | Cyan | Additional services |
| `other` | Slate | Other revenue |

## 📊 What Gets Calculated

### Revenue Streams:
- **Current Revenue**: From TransactionQueue (completed M-Pesa) + Advertisement (ads)
- **Target Achievement**: `(current / target) × 100`
- **Growth**: `((current - previous) / previous) × 100`

### Departments:
- **Current Spending**: Sum of expenses this month
- **Budget Utilization**: `(spending / budget) × 100`

## 🎨 Frontend Features

### Summary Cards:
1. Total Revenue (sum of all streams)
2. Active Streams (count)
3. Average Growth (%)
4. Average Achievement (%)

### Data Table:
- Stream name & category
- Current vs target revenue
- Achievement progress bar
- Growth indicator (↑/↓)
- Active/Inactive status

## 🔐 Authentication

All endpoints require JWT token:
```javascript
headers: {
  'Authorization': 'Bearer YOUR_JWT_TOKEN'
}
```

## 📝 Create Revenue Stream (Django Admin)

1. Go to Django Admin → Finance → Revenue Streams
2. Click "Add Revenue Stream"
3. Fill in:
   - Name: "My Revenue Stream"
   - Category: Choose from dropdown
   - Target Revenue: 100000
   - Target Growth Rate: 10.0
   - Is Active: ✓
4. Save

## 🐛 Troubleshooting

### No data showing?
- Check if revenue streams exist: `RevenueStream.objects.count()`
- Run: `python manage.py create_sample_streams`

### API returns 401?
- Check JWT token is valid
- Token in header: `Authorization: Bearer TOKEN`

### Revenue shows 0?
- Check TransactionQueue has completed transactions
- Check Advertisement model has total_spent > 0

## 📚 Documentation Files

- `API_DOCUMENTATION.md` - Full API docs
- `BACKEND_COMPLETE.md` - Complete setup guide
- `FINANCE_FRONTEND_SETUP.md` - Frontend setup
- `REVENUESTREAM_FUNCTIONAL.md` - Model documentation
- `QUICKSTART.md` - Quick start guide

## ✅ Status

- ✅ Backend API functional
- ✅ Frontend UI complete
- ✅ Real data integration
- ✅ Ads revenue tracking
- ✅ Authentication working
- ✅ Sample data command

**Everything is ready to use!** 🎉
