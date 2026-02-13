# Finance Models Explanation & Profit/Loss Calculation

## 📊 Your Finance Models Explained

### 1. **Currency & ExchangeRate**
**Purpose**: Multi-currency support for international operations
- **Currency**: Stores all world currencies (KES, USD, EUR, etc.)
- **ExchangeRate**: Tracks conversion rates between currencies
- **Use Case**: Convert all transactions to KES (base currency) for unified reporting

### 2. **PaymentTransaction** 💰
**Purpose**: Records ONLY successful payments that received callbacks
- Stores completed M-Pesa, Stripe, PayPal payments
- Multi-currency support with auto-conversion to KES
- **This is your PRIMARY REVENUE source**
- Status: completed, refunded, partially_refunded

### 3. **TransactionQueue** ⏳
**Purpose**: Tracks ALL payment attempts (pending, processing, completed, failed)
- Payment lifecycle management
- Retry logic for failed payments
- **Use for revenue**: Filter by `status IN ['completed', 'processed']` and `method='mpesa'`
- **Currently using this for analytics**

### 4. **Investment** 💼
**Purpose**: Track business funding and capital
- **Types**: Seed funding, angel investment, VC, loans, personal investment
- **Status**: Proposed → Approved → Disbursed → Active → Repaid
- **Use Case**: 
  - Track where money came from
  - Calculate ROI (Return on Investment)
  - Monitor loan repayments
  - **NOT counted as revenue** (it's capital, not income)

### 5. **Department** 🏢
**Purpose**: Cost centers for organizing expenses
- Examples: IT, Marketing, Operations, Customer Service
- Each has a budget and manager
- **Use Case**: Track spending by department, monitor budget utilization

### 6. **BudgetCategory** 📋
**Purpose**: Detailed budget planning within departments
- Links to specific department
- Has planned amount for fiscal year
- **Use Case**: Compare planned vs actual spending, identify overspending

### 7. **Expense** 💸
**Purpose**: Track ALL business costs
- **Categories**: Network infrastructure, salaries, marketing, utilities, software, etc.
- **Types**: 
  - **CAPEX** (Capital Expenditure): Equipment, infrastructure (depreciated over time)
  - **OPEX** (Operational Expenditure): Day-to-day costs (salaries, utilities)
- **Approval workflow**: Draft → Submitted → Approved → Paid
- **Tax tracking**: VAT, tax deductions
- **This is your PRIMARY COST source**

### 8. **RevenueStream** 📈
**Purpose**: Categorize and track different income sources
- **Categories**:
  - **Voucher Sales**: Internet voucher purchases
  - **Package Sales**: Data package subscriptions
  - **Usage Charges**: Pay-as-you-go internet usage
  - **Premium Services**: VIP packages, priority support
  - **Value Added Services**: Additional services (ads revenue, etc.)
- **Use Case**: 
  - Identify which products make most money
  - Track revenue targets per stream
  - Calculate Customer Lifetime Value (CLV)
  - Monitor growth rates

### 9. **FinancialReport** 📊
**Purpose**: Pre-generated reports for fast analytics
- **Types**: Daily sales, weekly revenue, monthly income, quarterly P&L, annual financial
- Cached for performance
- **Use Case**: Quick access to historical reports without recalculating

---

## 💰 PROFIT & LOSS (P&L) CALCULATION

### Formula:
```
PROFIT = REVENUE - EXPENSES

Where:
- REVENUE = All income from sales
- EXPENSES = All business costs
- PROFIT = What's left (can be positive or negative)
```

### Detailed P&L Structure:

```
REVENUE (Income)
├── Voucher Sales          (from TransactionQueue/PaymentTransaction)
├── Package Sales          (from TransactionQueue/PaymentTransaction)
├── Usage Charges          (from TransactionQueue/PaymentTransaction)
├── Premium Services       (from TransactionQueue/PaymentTransaction)
└── Other Revenue          (from TransactionQueue/PaymentTransaction)
─────────────────────────
= TOTAL REVENUE (Gross Income)

COST OF GOODS SOLD (COGS)
├── Internet Bandwidth Costs    (from Expense: category='network')
├── Infrastructure Costs        (from Expense: category='network')
└── Direct Service Costs        (from Expense: category='maintenance')
─────────────────────────
= TOTAL COGS

GROSS PROFIT = TOTAL REVENUE - TOTAL COGS

OPERATING EXPENSES (OPEX)
├── Salaries & Wages           (from Expense: category='salaries')
├── Marketing & Advertising    (from Expense: category='marketing')
├── Office Expenses            (from Expense: category='office')
├── Utilities                  (from Expense: category='utility')
├── Software & Licensing       (from Expense: category='software')
├── Travel                     (from Expense: category='travel')
├── Training                   (from Expense: category='training')
└── Other Operating Costs      (from Expense: category='other')
─────────────────────────
= TOTAL OPERATING EXPENSES

OPERATING PROFIT (EBITDA) = GROSS PROFIT - OPERATING EXPENSES

DEPRECIATION & AMORTIZATION
└── Capital Equipment Depreciation  (from Expense: is_capex=True)
─────────────────────────
= TOTAL DEPRECIATION

EBIT (Earnings Before Interest & Tax) = OPERATING PROFIT - DEPRECIATION

INTEREST & FINANCING
├── Loan Interest Payments     (from Investment: investment_type='loan')
└── Investment Returns         (from Investment: expected_roi)
─────────────────────────
= NET INTEREST

EBT (Earnings Before Tax) = EBIT - NET INTEREST

TAXES
└── Corporate Tax (30% in Kenya)
─────────────────────────
= TOTAL TAX

NET PROFIT (Bottom Line) = EBT - TAXES
```

---

## 🎯 How to Use These Models for P&L

### 1. **Calculate Revenue**
```python
from finance.models import TransactionQueue
from django.db.models import Sum

# Total revenue from completed transactions
revenue = TransactionQueue.objects.filter(
    method='mpesa',
    status__in=['completed', 'processed']
).aggregate(total=Sum('price'))['total'] or 0
```

### 2. **Calculate Expenses**
```python
from finance.models import Expense

# Total expenses
total_expenses = Expense.objects.filter(
    approval_status='paid'
).aggregate(total=Sum('amount_base'))['total'] or 0

# By category
network_costs = Expense.objects.filter(
    category='network',
    approval_status='paid'
).aggregate(total=Sum('amount_base'))['total'] or 0

salaries = Expense.objects.filter(
    category='salaries',
    approval_status='paid'
).aggregate(total=Sum('amount_base'))['total'] or 0
```

### 3. **Calculate Profit**
```python
profit = revenue - total_expenses

# Profit margin percentage
profit_margin = (profit / revenue * 100) if revenue > 0 else 0
```

### 4. **Revenue by Stream**
```python
from finance.models import RevenueStream

# Get revenue breakdown by stream
for stream in RevenueStream.objects.filter(is_active=True):
    stream_revenue = stream.current_month_revenue
    print(f"{stream.name}: KSh {stream_revenue}")
```

---

## 📊 Key Financial Metrics You Can Calculate

1. **Gross Profit Margin** = (Gross Profit / Revenue) × 100
2. **Operating Profit Margin** = (Operating Profit / Revenue) × 100
3. **Net Profit Margin** = (Net Profit / Revenue) × 100
4. **Return on Investment (ROI)** = (Net Profit / Total Investment) × 100
5. **Break-Even Point** = Fixed Costs / (Revenue per Unit - Variable Cost per Unit)
6. **Customer Acquisition Cost (CAC)** = Marketing Expenses / New Customers
7. **Customer Lifetime Value (CLV)** = Average Revenue per User × Customer Lifespan
8. **Burn Rate** = Monthly Expenses (for startups)
9. **Runway** = Cash Balance / Burn Rate (months until money runs out)

---

## 🚀 Next Steps

Would you like me to:
1. **Create a P&L Statement View** - Real-time profit/loss dashboard
2. **Build Financial Analytics Endpoints** - API for all these calculations
3. **Add Revenue Stream Tracking** - Categorize your income sources
4. **Create Budget vs Actual Reports** - Compare planned vs actual spending
5. **Build Cash Flow Statement** - Track money in/out over time

Let me know which you'd like to implement first! 💰📊
