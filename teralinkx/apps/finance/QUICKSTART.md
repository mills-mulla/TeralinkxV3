# RevenueStream Quick Start Guide 🚀

## ✅ Migration Applied Successfully!

The RevenueStream model is now fully functional with ads revenue support.

## 🎯 Quick Setup (5 Minutes)

### Step 1: Access Django Admin
```
http://your-domain/admin/finance/revenuestream/
```

### Step 2: Create Your First Revenue Streams

#### 1. **Advertising Revenue Stream**
```
Name: Advertising Revenue
Category: Advertising Revenue (ads_revenue)
Is Active: ✓
Target Revenue: 50000 (KES 50,000/month)
Target Growth Rate: 15.0 (15% growth)
Description: Revenue from banner, video, and native advertisements
Display Order: 1
```

#### 2. **Voucher Sales Stream**
```
Name: Internet Voucher Sales
Category: Voucher Sales (voucher_sales)
Is Active: ✓
Target Revenue: 200000 (KES 200,000/month)
Target Growth Rate: 10.0 (10% growth)
Description: Revenue from internet voucher purchases
Display Order: 2
```

#### 3. **Package Sales Stream**
```
Name: Data Package Subscriptions
Category: Package Sales (package_sales)
Is Active: ✓
Target Revenue: 150000 (KES 150,000/month)
Target Growth Rate: 12.0 (12% growth)
Description: Revenue from monthly data package subscriptions
Display Order: 3
```

#### 4. **Premium Services Stream**
```
Name: Premium Services
Category: Premium Services (premium_services)
Is Active: ✓
Target Revenue: 75000 (KES 75,000/month)
Target Growth Rate: 20.0 (20% growth)
Description: VIP packages, priority support, premium features
Display Order: 4
```

### Step 3: View Real-Time Metrics

Once created, you'll see in the admin list:

| Name | Category | Current Month | Target Achievement | Revenue Growth |
|------|----------|---------------|-------------------|----------------|
| Advertising Revenue | Ads Revenue | KES 12,500 | 25% ████░░░░░░ | ↑ 8.5% |
| Voucher Sales | Voucher Sales | KES 185,000 | 92% █████████░ | ↑ 15.2% |
| Package Sales | Package Sales | KES 160,000 | 106% ██████████ | ↑ 12.8% |
| Premium Services | Premium Services | KES 45,000 | 60% ██████░░░░ | ↓ 3.1% |

## 📊 How It Works

### Ads Revenue Tracking
Your existing `Advertisement` model tracks:
- **Impressions**: How many times ads are shown
- **Clicks**: How many times ads are clicked
- **Total Spent**: Revenue generated from ads

The RevenueStream automatically pulls this data:
```python
# When category = 'ads_revenue'
ads_revenue = Advertisement.objects.filter(
    status='active',
    created_at__gte=current_month
).aggregate(total=Sum('total_spent'))['total']
```

### Transaction Revenue Tracking
For all other categories (vouchers, packages, etc.):
```python
# Uses TransactionQueue for completed M-Pesa transactions
transaction_revenue = TransactionQueue.objects.filter(
    method='mpesa',
    status__in=['completed', 'processed'],
    created_at__gte=current_month
).aggregate(total=Sum('price'))['total']
```

## 🔧 Admin Actions

### 1. **Update KPIs** (Recommended: Run Monthly)
- Select revenue streams
- Actions → "Update KPIs for selected streams"
- This calculates:
  - Customer Acquisition Cost (CAC)
  - Customer Lifetime Value (CLV)
  - Monthly Recurring Revenue (MRR)
  - Churn Rate

### 2. **Calculate Metrics** (Real-time)
- Select revenue streams
- Actions → "Calculate metrics for selected streams"
- Forces recalculation of all metrics

### 3. **Activate/Deactivate Streams**
- Select revenue streams
- Actions → "Activate selected streams" or "Deactivate selected streams"

## 📈 Viewing Detailed Metrics

Click on any revenue stream to see:

### Current Performance
- **Current Month Revenue**: Real-time revenue for this month
- **Target Achievement**: Progress towards monthly target
- **Revenue Growth**: Percentage change vs last month

### Advanced Metrics (Collapsed Section)
- **Customer Lifetime Value (CLV)**: How much a customer is worth
- **Customer Acquisition Cost (CAC)**: Cost to acquire one customer
- **Churn Rate**: Percentage of customers leaving

### KPI Data (JSON)
```json
{
  "customer_acquisition_cost": 150.50,
  "lifetime_value": 2500.00,
  "monthly_recurring_revenue": 50000.00,
  "churn_rate": 5.2,
  "net_promoter_score": 0,
  "updated_at": "2025-02-03T10:30:00"
}
```

## 💡 Pro Tips

### 1. **Set Realistic Targets**
- Start with current revenue as baseline
- Increase by 10-20% for growth targets
- Review and adjust quarterly

### 2. **Monitor CAC vs CLV Ratio**
- **Healthy**: CLV > 3x CAC
- **Warning**: CLV < 3x CAC (reduce marketing spend)
- **Critical**: CLV < CAC (losing money on each customer)

### 3. **Track Revenue Growth**
- **Green (↑)**: Positive growth - keep doing what works
- **Red (↓)**: Negative growth - investigate and fix
- **Flat (0%)**: Stagnant - need new strategies

### 4. **Use Display Order**
- Order streams by importance (1 = highest)
- Most important revenue sources at top
- Makes admin list easier to scan

## 🔍 Troubleshooting

### "Current Month Revenue shows 0"
**Cause**: No completed transactions this month
**Solution**: 
- Check TransactionQueue for completed transactions
- Verify `method='mpesa'` and `status='completed'`
- For ads, check Advertisement model has `total_spent > 0`

### "Target Achievement not showing"
**Cause**: Target Revenue not set
**Solution**: Edit revenue stream and set Target Revenue field

### "Revenue Growth shows 0%"
**Cause**: No data for previous month
**Solution**: Wait until you have 2 months of data

### "Ads Revenue not tracking"
**Cause**: Advertisement model not recording revenue
**Solution**: 
- Check Advertisement.total_spent field is being updated
- Verify ads are status='active'
- Check record_impression() and record_click() methods are being called

## 📱 Next Steps

### 1. **Create API Endpoint** (Optional)
Expose revenue data to your frontend:
```python
# apps/finance/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import RevenueStream

class RevenueStreamAPIView(APIView):
    def get(self, request):
        streams = RevenueStream.objects.filter(is_active=True)
        return Response([{
            'name': s.name,
            'category': s.get_category_display(),
            'current_revenue': float(s.current_month_revenue),
            'target': float(s.target_revenue or 0),
            'achievement': float(s.target_achievement),
            'growth': float(s.revenue_growth),
        } for s in streams])
```

### 2. **Add to Analytics Dashboard**
Display revenue streams in your admin dashboard:
- Current month revenue by category
- Target achievement progress bars
- Revenue growth trends
- Top performing streams

### 3. **Set Up Alerts** (Optional)
Create notifications for:
- Target achievement < 50% (mid-month warning)
- Negative revenue growth
- CAC > CLV (losing money)
- Churn rate > 10%

## 🎉 You're All Set!

Your RevenueStream model is now:
- ✅ Fully functional
- ✅ Tracking real revenue data
- ✅ Integrated with Advertisement model
- ✅ Calculating CLV, CAC, and growth metrics
- ✅ Ready for production use

Go to Django Admin and create your first revenue streams! 🚀

---

**Need Help?**
- Check `/apps/finance/REVENUESTREAM_FUNCTIONAL.md` for detailed documentation
- Check `/apps/finance/FINANCE_MODELS_EXPLAINED.md` for P&L calculations
- Review your Advertisement model in `/apps/ads/models.py`
