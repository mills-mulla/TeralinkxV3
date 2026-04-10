# Admin Frontend - What to Expect

## 🌐 Access URL
**Production**: `https://su.teralinkxwaves.uk`  
**Local Dev**: `http://localhost:5173` (if running `npm run dev`)

---

## ✅ **Existing Pages** (Already Working)

### Overview Section
1. **Dashboard** - Main overview with stats
2. **Analytics** - Business analytics

### User Management
3. **Clients** - Customer management (ISP subscribers)
4. **Users** - Admin user management
5. **Devices** - Connected devices tracking
6. **Sessions** - Active user sessions

### Products & Services
7. **Packages** - Internet packages (data plans)
8. **Vouchers** - Voucher codes management
9. **Coupons** - Discount coupons
10. **Promotions** - Marketing promotions

### Financial Section
11. **Finance** - Financial overview
12. **🆕 Churn Prediction** - **JUST ADDED** (Phase 1.2)
13. **Transactions** - Payment transactions
14. **Refunds** - Refund management

### Network
15. **Locations** - Hotspot locations

### Support
16. Documentation, Help Center, System Info, About

---

## 🆕 **New Churn Prediction Dashboard**

### Location in Menu
**Sidebar → Financial Section → "Churn Prediction"** (red icon with trending chart)

### What You'll See

#### 1. **Header Section**
- Title: "Churn Prediction Dashboard"
- Button: "Generate Predictions" (triggers ML model)

#### 2. **Filter Bar**
- Dropdown: Filter by risk level (All, Critical, High, Medium, Low)

#### 3. **Stats Cards** (4 cards)
```
┌─────────────┬─────────────┬─────────────┬─────────────┐
│ Critical    │ High Risk   │ Medium Risk │ Revenue at  │
│ Risk        │             │             │ Risk        │
│ [COUNT]     │ [COUNT]     │ [COUNT]     │ KES [AMOUNT]│
└─────────────┴─────────────┴─────────────┴─────────────┘
```

#### 4. **Predictions Table**
Columns:
- **Customer** - Account name
- **Risk Level** - Badge (Critical/High/Medium/Low)
- **Churn Score** - Percentage (0-100%)
- **MRR** - Monthly Recurring Revenue
- **Top Factors** - Why customer is at risk
- **Actions** - "Create Task" button

---

## 📊 **Sample Data Display**

### Example Row:
```
Customer: CLI000123
Risk Level: [CRITICAL] (red badge)
Churn Score: 78.5%
MRR: KES 5,000
Top Factors:
  • No session in 45 days
  • 3 billing disputes (90d)
  • Downgraded package last month
Actions: [Create Task]
```

---

## 🔌 **Backend APIs Connected**

The dashboard calls these endpoints:

1. **GET** `/api/finance/api/churn-predictions/`
   - Lists all predictions
   - Filters: `?risk_level=critical`

2. **POST** `/api/finance/api/churn-predictions/generate/`
   - Generates new predictions for all customers
   - Uses ML model if available, falls back to rules

3. **GET** `/api/finance/api/retention-tasks/`
   - Lists retention tasks
   - Filters: `?status=pending`

---

## ⚠️ **Current Limitations**

### Data Requirements
- **Needs 50+ customer records** to train ML model
- Falls back to rule-based scoring if insufficient data
- Predictions based on:
  - Days since last payment
  - Payment history
  - Support tickets (TODO)
  - Package changes (TODO)

### Not Yet Implemented
- ❌ Celery task for weekly retraining
- ❌ Real-time monitoring of model accuracy
- ❌ Support ticket integration
- ❌ Package downgrade tracking

---

## 🚀 **How to Use**

### Step 1: Access Dashboard
1. Login to admin panel: `https://su.teralinkxwaves.uk`
2. Click **"Churn Prediction"** in sidebar (Financial section)

### Step 2: Generate Predictions
1. Click **"Generate Predictions"** button
2. Wait for processing (generates for first 50 customers)
3. Table populates with results

### Step 3: Review At-Risk Customers
1. Filter by **"Critical"** or **"High"** risk
2. Review top factors for each customer
3. Check MRR to prioritize high-value customers

### Step 4: Create Retention Tasks
1. Click **"Create Task"** for at-risk customer
2. System automatically:
   - High-value (>KES 5K): Auto-applies 20% discount
   - Medium-value (>KES 2K): Sends SMS with 10% offer
   - Low-value: Sends re-engagement SMS

---

## 🎨 **Visual Design**

### Color Coding
- **Critical Risk**: Red badge, red border
- **High Risk**: Orange badge, orange border
- **Medium Risk**: Yellow badge, yellow border
- **Low Risk**: Green badge (not shown by default)

### Stats Cards
- Blue: Active Users
- Green: Sessions
- Purple: Devices
- Amber: Refunds

---

## 🔧 **Developer Notes**

### Component Location
`/admteralinkx/adminstration/src/components/finance/ChurnDashboard.vue`

### Router Entry
```javascript
{
  path: '/finance/churn',
  name: 'ChurnPrediction',
  component: () => import('../components/finance/ChurnDashboard.vue'),
  meta: { requiresAuth: true }
}
```

### Sidebar Entry
```javascript
{ 
  id: 11.5, 
  name: 'Churn Prediction', 
  icon: '<svg>...</svg>', 
  component: 'ChurnPrediction', 
  color: '#dc2626' 
}
```

---

## 📈 **Expected Behavior**

### On First Load
1. Dashboard loads empty
2. Click "Generate Predictions"
3. Backend processes 50 customers
4. Table populates with results
5. Stats cards update with counts

### After Data Exists
1. Dashboard shows cached predictions
2. Filter dropdown works instantly
3. Stats update based on filter
4. "Create Task" creates retention workflow

### If No Data
- Shows empty table
- Message: "No predictions found. Click Generate Predictions."

---

## 🐛 **Troubleshooting**

### "No predictions found"
- Click "Generate Predictions" button
- Check backend logs: `docker-compose logs teralinkx`
- Verify API endpoint: `curl https://srv.teralinkxwaves.uk/api/finance/api/churn-predictions/`

### "Failed to load predictions"
- Check CORS settings
- Verify JWT token in browser localStorage
- Check network tab in browser DevTools

### "Model not trained"
- Run: `python manage.py train_churn_model`
- Requires 50+ customer records
- Falls back to rule-based automatically

---

## 📝 **Next Steps**

To fully activate:

1. **Install dependencies**:
   ```bash
   pip install xgboost scikit-learn
   ```

2. **Train ML model** (if 50+ customers):
   ```bash
   python manage.py train_churn_model
   ```

3. **Generate predictions**:
   - Via admin UI: Click "Generate Predictions"
   - Via API: `POST /api/finance/api/churn-predictions/generate/`

4. **Monitor results**:
   - Check predictions table
   - Review retention tasks
   - Track customer outcomes

---

**Status**: ✅ Frontend integrated, backend ready, needs data to train ML model

**Progress**: 4.0/10 (Phase 1.2 complete with frontend)
