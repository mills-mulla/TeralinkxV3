# Smart Business Management System — Comprehensive Implementation Plan

**Version**: 3.0 — Reviewed & Updated  
**Target**: ISP / Telecoms Operations (TeralinkX)  
**Horizon**: 90-Day Phased Rollout  
**Last Updated**: 2026  
**Philosophy**: Ship value every week. Every feature must answer: *"What decision does this help someone make faster?"*

---

## Executive Summary

This plan transforms TeralinkX's finance module into a full **Smart Business Management (SBM)** platform — integrating AI-assisted finance, customer intelligence, operations awareness, and executive decision support into a unified system. The HIDS network layer is treated as a first-class data source, not a bolt-on.

**Important**: TeralinkX already has a strong foundation. This plan builds *on top of* existing capabilities — it does not replace them. Before implementing any phase, review what already exists to avoid duplicating work.

---

## What Already Exists (Do Not Rebuild)

The current system is more capable than the original plan acknowledged. These features are **already implemented** and should be leveraged, not rebuilt:

**Backend (Django) — Strong Foundation**
- Multi-currency system with 150+ currencies and exchange rate tracking with auto-update
- Payment gateway integration: M-Pesa, Stripe, PayPal with transaction queue and retry logic
- ISP-specific metrics: MRR, ARR, ARPU, LTV, CLV, CAC, churn rate calculations
- CAPEX/OPEX tracking with depreciation schedules
- Expense approval workflows with multi-level sign-off
- Department and budget category management
- Revenue stream tracking with full analytics
- Pre-generated financial reporting system
- Investment tracking (equity, loans, ROI)

**Frontend (Vue.js Admin Panel) — Solid**
- Finance dashboard with 5 working tabs: Analytics, Revenue Streams, Expenses, Investments, Departments
- Real-time metrics display with dark mode support
- Full CRUD for all financial entities
- FinancialAnalytics component with charts

**What this means for implementation**: Skip anything in the phases below that duplicates the above. The sprint tasks assume a blank slate — they don't. Adjust scope accordingly before starting each phase.

---

## Core Design Principles

1. **Accuracy over impressiveness** — A churn score you trust is worth more than a fancy ML model you can't validate.
2. **Explainability** — Every AI output must include *why*. No black-box recommendations.
3. **Graceful degradation** — If ML models aren't trained yet, fall back to rule-based logic. Never show empty dashboards.
4. **Operator-first UX** — Staff using this daily are not data scientists. Every screen should be actionable in under 30 seconds.
5. **HIDS as signal, not noise** — Network anomalies are correlated with financial events only when the correlation is statistically meaningful. No false urgency.
6. **One thing properly beats five things half-built** — Each sprint ships one validated, usable feature. Not five features that are all 80% done.

---

## ML Engine Decisions

Different problems require different tools. Do not default to Random Forest for everything.

| Feature | Tool | Reason |
|---|---|---|
| Churn prediction | XGBoost | Handles class imbalance natively (`scale_pos_weight`), explainable, fast weekly retraining |
| Cash flow forecasting | Facebook Prophet | Time-series only — tree models are wrong here. Prophet handles Kenyan seasonal patterns (month-end spikes, school terms, public holidays) |
| Fraud / anomaly detection (now) | Rule engine | No labelled fraud data yet. A transparent rule engine outperforms an untrained ML model and won't produce constant false positives |
| Fraud / anomaly detection (later) | Isolation Forest | After 6–12 months of labelled cases. Not before. |
| Document OCR | Google Cloud Vision API | Not a local ML problem. Cloud Vision handles M-Pesa receipts, Swahili text, phone photos far better than Tesseract |
| Expense categorization | Logistic Regression + TF-IDF | Simple, fast, works on limited text data. No need for BERT at this scale. |

**Random Forest is not recommended** for any feature in this system. XGBoost is strictly better for imbalanced ISP churn data and trains faster for weekly retraining cycles.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                      TeralinkX SBM Platform                          │
├─────────────────────┬───────────────────────┬────────────────────────┤
│  EXISTING (Strong)  │  Intelligence Engine  │   Executive Layer       │
│                     │  (New — Build These)  │   (New — Build These)   │
│  • Multi-currency   │                       │                         │
│  • M-Pesa / Stripe  │  • Churn ML (XGBoost) │  • KPI Command Centre   │
│  • MRR/ARR/ARPU     │  • Fraud (Rule engine)│  • Board Reports        │
│  • Expense approvals│  • OCR (Cloud Vision) │  • Cash Flow Forecast   │
│  • Dept budgets     │  • Prophet Forecast   │  • Pricing Intelligence │
│  • Revenue streams  │  • HIDS Integration   │  • Vendor Intelligence  │
│  • Investments      │  • Reconciliation     │                         │
│  • Financial reports│  • Smart Categories   │                         │
└──────────┬──────────┴───────────────────────┴──────────┬─────────────┘
           │                                              │
           ▼                                              ▼
      Django REST API                              Vue.js Admin Panel
      Celery + Redis                               Real-time WebSocket
      PostgreSQL + TimescaleDB                     ApexCharts
      Event Bus (Django Signals)                   5 existing tabs + 5 new tabs
```

---

## Sprint-Based Implementation Strategy

Each sprint ships **one complete, validated feature**. This replaces the "build everything in 2 days" approach with a sustainable cadence.

| Sprint | Weeks | Focus |
|--------|-------|-------|
| 0 | 1–2 | Foundation — no visible features, but everything depends on this |
| 1 | 3 | Churn v1 (rule-based) — first actionable output |
| 2 | 4 | Churn v2 (XGBoost) + retention workflow |
| 3 | 5 | OCR invoice pipeline |
| 4 | 6 | Cash flow forecasting |
| 5 | 7 | Bank statement reconciliation |
| 6 | 8 | HIDS fraud correlation |
| 7 | 9 | Network → revenue impact |
| 8 | 10 | KPI Command Centre |
| 9 | 11 | Budget intelligence + vendor analysis |
| 10 | 12 | Board reports + pricing intelligence |

---

## Phase 0: Foundation Hardening (Weeks 1–2)

**Goal**: Fix what will break everything else if ignored. No visible features ship in this phase — that is correct and intentional.

### 0.1 Data Quality Audit
Before building any ML model, measure data completeness on existing records:
- PaymentTransaction: null rates, duplicate transactions, mismatched currencies
- Customer records: missing fields, orphaned accounts, inconsistent status values
- Expense records: categorization consistency (existing manual categories will seed the ML categorizer)
- Exchange rates: verify auto-update is running and rates are current

**Deliverable**: Simple admin view showing completeness % per entity. Fix anything below 90% before proceeding.

### 0.2 TimescaleDB Migration
Convert high-volume time-series tables to TimescaleDB hypertables:
- `PaymentTransaction` — cash flow forecasting queries 12+ months of data per customer
- `NetworkAnomalies` (HIDS feed)
- Session/usage data for churn feature extraction

**Why now**: Prophet and XGBoost feature extraction will time out on standard PostgreSQL for customers with 2+ years of history. This is a prerequisite for Phases 1 and 2.

**Caution**: Run parallel with existing queries. Test thoroughly. Full rollback plan required before cutover.

### 0.3 Event Bus (Django Signals + Celery)
Wire up event routing for real-time intelligence:
- `payment.completed` → trigger churn score refresh for that customer
- `expense.created` → trigger budget utilization recalculation
- `hids.anomaly` → trigger fraud correlation check
- `invoice.uploaded` → trigger OCR pipeline

Without this, "smart" features run on cron jobs — not on actual events.

### 0.4 ML Model Registry

```python
class MLModel(models.Model):
    name = models.CharField(max_length=100)       # 'churn_v1', 'churn_v2', 'fraud_rules_v1'
    version = models.CharField(max_length=20)
    model_type = models.CharField(max_length=50)  # 'xgboost', 'prophet', 'rules', 'logistic'
    trained_at = models.DateTimeField()
    accuracy_score = models.FloatField()          # AUC for classifiers, MAE for forecasters
    feature_importance = models.JSONField()
    is_active = models.BooleanField(default=False)
    fallback_strategy = models.CharField(max_length=50)  # 'rules', 'previous_version', 'none'
    training_data_size = models.IntegerField()
    notes = models.TextField(blank=True)
```

Every AI feature checks this registry first and falls back gracefully when no active model exists. This is what allows shipping churn v1 (rules) and upgrading to v2 (XGBoost) without touching frontend code.

---

## Phase 1: Customer Intelligence (Weeks 3–4)

**Business value**: Preventing one high-value customer from churning pays for this entire phase.

### New Models Required

```python
class ChurnPrediction(models.Model):
    customer = models.ForeignKey('users.ClientH', on_delete=models.CASCADE)
    churn_probability = models.FloatField()
    confidence = models.CharField(max_length=20)  # 'high', 'medium', 'low'
    risk_level = models.CharField(max_length=20,
        choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')])
    model_version = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True)
    top_factors = models.JSONField()              # [{factor, impact_pct}]
    predicted_revenue_at_risk = models.DecimalField(max_digits=15, decimal_places=2)
    predicted_at = models.DateTimeField(auto_now_add=True)
    refreshed_at = models.DateTimeField(auto_now=True)

class RetentionTask(models.Model):
    customer = models.ForeignKey('users.ClientH', on_delete=models.CASCADE)
    churn_prediction = models.ForeignKey(ChurnPrediction, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    talking_points = models.JSONField()
    suggested_offer = models.TextField()
    status = models.CharField(max_length=20,
        choices=[('pending','Pending'),('contacted','Contacted'),
                 ('retained','Retained'),('churned','Churned'),('no_response','No Response')])
    outcome_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    resolved_at = models.DateTimeField(null=True)
```

### 1.1 Churn Prediction

**Sprint 1 (Week 3)**: Rule-based scoring. No training data required. Ships immediately.

**ISP-specific feature set (ranked by predictive importance)**:
1. Days since last session — strongest single signal
2. Support tickets (last 90 days), especially billing disputes
3. Average session duration trend — declining = disengaging
4. Payment method changes — indicator of financial stress
5. Package downgrade history
6. Usage vs. package tier — paying for 20Mbps, using 2Mbps = underutilised = churn risk
7. Seasonal adjustment — silence in December ≠ churn; silence in March = problem

**Sprint 2 (Week 4)**: XGBoost replaces rules IF AUC > 0.75 on held-out test set. If not, rules stay active. Retrain weekly via Celery Beat.

**Output schema** (identical for both rule-based and XGBoost — frontend never changes):
```json
{
  "customer_id": "CL-00123",
  "churn_probability": 0.74,
  "confidence": "high",
  "risk_level": "critical",
  "model_version": "churn_v2",
  "explanation": {
    "top_factors": [
      {"factor": "No session in 18 days", "impact": "+32%"},
      {"factor": "3 billing disputes (90d)", "impact": "+28%"},
      {"factor": "Downgraded package last month", "impact": "+14%"}
    ]
  },
  "recommended_actions": [
    {
      "action": "Personal call from account manager",
      "urgency": "within_24h",
      "offer": "30% loyalty discount — 3 months",
      "estimated_save_probability": 0.61
    }
  ],
  "predicted_revenue_at_risk": 18400
}
```

`predicted_revenue_at_risk` = CLV × churn_probability. This is the number that triggers executive action.

### 1.2 Retention Workflow

Prediction without execution is useless:
1. Churn alert fires → creates `RetentionTask` assigned to account manager
2. Account manager sees task with auto-generated talking points from risk factors
3. Outcome recorded (retained / churned / contacted / no response)
4. Outcome feeds back into next week's model training — this is the feedback loop that makes the model improve

### 1.3 Revenue at Risk Dashboard

New tab `ChurnPrevention.vue`:
- Total MRR at risk (sum: monthly revenue × churn probability for all high-risk customers)
- Week-over-week trend
- Retention task completion rate
- Top 10 highest-value at-risk accounts — personal outreach, not automated email

### New API Endpoints
```
GET  /api/finance/api/churn-predictions/     ?risk_level=high&ordering=-predicted_revenue_at_risk
GET  /api/finance/api/revenue-at-risk/       Aggregate totals + week trend
POST /api/finance/api/retention-tasks/       Create outreach task
PATCH /api/finance/api/retention-tasks/{id}/ Record outcome
GET  /api/finance/api/retention-tasks/       My open tasks (account manager view)
```

---

## Phase 2: Financial Intelligence (Weeks 5–7)

### New Models Required

```python
class InvoiceDocument(models.Model):
    file = models.FileField(upload_to='invoices/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    extracted_data = models.JSONField(default=dict)
    vendor = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    currency = models.ForeignKey('Currency', on_delete=models.SET_NULL, null=True)
    invoice_date = models.DateField(null=True)
    confidence_score = models.FloatField(default=0.0)
    review_required = models.BooleanField(default=False)
    status = models.CharField(max_length=20,
        choices=[('pending','Pending'),('review','Needs Review'),
                 ('approved','Approved'),('rejected','Rejected')])
    linked_expense = models.OneToOneField('Expense', null=True, on_delete=models.SET_NULL)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CashFlowForecast(models.Model):
    generated_at = models.DateTimeField(auto_now_add=True)
    horizon_days = models.IntegerField()
    forecast_date = models.DateField()
    predicted_inflow = models.DecimalField(max_digits=15, decimal_places=2)
    predicted_outflow = models.DecimalField(max_digits=15, decimal_places=2)
    net_position = models.DecimalField(max_digits=15, decimal_places=2)
    confidence_lower = models.DecimalField(max_digits=15, decimal_places=2)  # P10
    confidence_upper = models.DecimalField(max_digits=15, decimal_places=2)  # P90
    scenario = models.CharField(max_length=20,
        choices=[('optimistic','Optimistic'),('base','Base'),('conservative','Conservative')])
    model_version = models.ForeignKey(MLModel, on_delete=models.SET_NULL, null=True)

class ReconciliationSession(models.Model):
    bank_statement_file = models.FileField(upload_to='bank_statements/%Y/%m/')
    upload_date = models.DateTimeField(auto_now_add=True)
    period_start = models.DateField()
    period_end = models.DateField()
    total_items = models.IntegerField(default=0)
    matched_count = models.IntegerField(default=0)
    unmatched_count = models.IntegerField(default=0)
    match_rate = models.FloatField(default=0.0)
    status = models.CharField(max_length=20,
        choices=[('processing','Processing'),('ready','Ready for Review'),('approved','Approved')])
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
```

### 2.1 Document Processing — OCR (Sprint 3, Week 5)

**Use Google Cloud Vision API, not Tesseract.** Tesseract fails on:
- M-Pesa receipts (SMS format, not invoice layout)
- Handwritten delivery notes
- Low-quality phone photos
- Mixed English/Swahili text
- Multiple currency symbols on one document

Cost: ~$1.50 per 1,000 documents.

**Confidence thresholds**:
- Above 90%: Auto-create expense draft, notify finance for final approval
- 70–90%: Pre-filled draft flagged for human review
- Below 70%: Show raw extracted text, ask user to fill manually

**Vendor templates**: Build extraction templates for the top 20 recurring vendors — same format every time, pushes accuracy to near 100% at zero extra cost.

**Always store**: Raw image + extracted JSON separately. Never discard the original.

**Integration note**: OCR creates a pre-filled draft that feeds into the **existing** expense approval workflow. Do not rebuild approval logic.

### 2.2 Cash Flow Forecasting (Sprint 4, Week 6)

**Model**: Facebook Prophet. XGBoost and Random Forest are the wrong tools here — they don't understand time-series seasonality.

**Three scenario tracks**:
- **Optimistic (P10)**: Current retention holds, all renewals convert
- **Base (P50)**: Average churn rate, normal delayed payment rate
- **Conservative (P90)**: Elevated churn, 30% late payment rate

**Alert triggers**:
- Cash projected below KES 500,000 in 14 days → CFO immediate alert
- MRR growth slowing — Q3 target at risk → Board-level alert
- Unusually high expense forecast vs. budget → Finance manager alert

**Data source**: Existing `PaymentTransaction`, `Expense`, and `RevenueStream` models. No new data collection needed. Requires minimum 12 months of history for reliable forecasts — show confidence intervals prominently if history is shorter.

### 2.3 Smart Reconciliation (Sprint 5, Week 7)

Three-tier matching designed for M-Pesa complexity:
1. **Tier 1 — Exact**: Amount + customer ID match
2. **Tier 2 — Fuzzy**: Amount ±2% + customer name (Levenshtein distance < 3)
3. **Tier 3 — Context**: Date range + MPESA phone number lookup

Unmatched items queue shows top 3 candidate matches with confidence scores — not a raw dump.

**Integration note**: Builds on existing `PaymentTransaction` and `BalanceTransaction` models. Do not rebuild transaction models.

### 2.4 Budget Intelligence (Sprint 5 add-on, Week 7)

Replace raw percentage alerts with smart utilization analysis:
- Utilization rate **vs. days remaining** — 80% spent with 60% of month elapsed = on track
- Variance analysis: "Marketing is KES 45K over — driven by 3 large events"
- Rolling 3-month spend trends per department

**Integration note**: Existing `Department` and `BudgetCategory` models are already built. This adds an analytical layer only.

### New API Endpoints
```
POST /api/finance/api/upload-invoice/          OCR extraction
GET  /api/finance/api/invoices/                ?status=review
PATCH /api/finance/api/invoices/{id}/approve/  Human approval → linked Expense created
GET  /api/finance/api/cash-flow-forecast/      ?horizon=30|90|180&scenario=base
POST /api/finance/api/reconcile/               Upload bank statement CSV/PDF
GET  /api/finance/api/reconcile/{id}/          Session results + match queue
PATCH /api/finance/api/reconcile/{id}/approve/ Finance sign-off
```

### New Frontend Components
- `InvoiceUpload.vue` — drag-drop, extraction preview, confidence display, one-click approve-to-expense
- `CashFlowForecast.vue` — 3-scenario ApexCharts line chart, threshold configuration, 30/90/180 toggle
- `Reconciliation.vue` — bank statement upload, match breakdown, ranked suggestion queue

---

## Phase 3: HIDS Financial Integration (Weeks 7–9)

TeralinkX's genuine competitive advantage. No standard finance system has network context. The discipline is being selective — only high-signal correlations trigger alerts.

### New Models Required

```python
class FinancialAnomaly(models.Model):
    transaction = models.ForeignKey('PaymentTransaction', on_delete=models.CASCADE, null=True)
    anomaly_type = models.CharField(max_length=50,
        choices=[('geo_mismatch','Geographic Mismatch'),
                 ('port_scan_correlation','Port Scan Correlation'),
                 ('shared_device_fraud','Shared Device Fraud'),
                 ('suspicious_dns','Suspicious DNS Correlation'),
                 ('amount_spike','Unusual Amount')])
    severity = models.CharField(max_length=20,
        choices=[('low','Low'),('medium','Medium'),('high','High'),('critical','Critical')])
    description = models.TextField()
    fraud_score = models.FloatField()
    network_correlation = models.JSONField(default=dict)  # Raw HIDS event data
    rule_triggered = models.CharField(max_length=100)
    detected_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)
    resolution = models.CharField(max_length=20,
        choices=[('false_positive','False Positive'),('actioned','Actioned'),('monitoring','Monitoring')],
        blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

class NetworkRevenueImpact(models.Model):
    hids_event_id = models.CharField(max_length=100)
    event_type = models.CharField(max_length=50)          # 'outage', 'packet_loss', 'node_failure'
    started_at = models.DateTimeField()
    resolved_at = models.DateTimeField(null=True)
    affected_customer_count = models.IntegerField(default=0)
    affected_mrr = models.DecimalField(max_digits=15, decimal_places=2)
    estimated_credit_liability = models.DecimalField(max_digits=15, decimal_places=2)
    credit_notes_drafted = models.IntegerField(default=0)
    credit_notes_issued = models.IntegerField(default=0)
```

### 3.1 Fraud Correlation Framework (Sprint 6, Week 8)

**Rule engine, not ML.** No labelled fraud data exists yet — an untrained anomaly detector will produce more false positives than a well-tuned rule engine.

**Four high-signal rules** (only these fire alerts):
1. Large payment from IP showing port-scan activity in same 5-minute window
2. Payment from IP geolocation >500km from account's registered location
3. Multiple customer accounts making payments from the same IP in the same hour
4. Payment within 2 minutes of DNS queries to known phishing or C2 domains

**Do not alert on**:
- Generic bandwidth anomaly at time of payment — too common, too noisy
- Payment after unusual hours where IP is a known VPN exit node
- Any single HIDS signal without a simultaneous financial event

**Threshold tuning**: Weekly false-positive rate review. If above 5%, raise thresholds before adding new rules.

**Future upgrade**: After 6–12 months of labelled cases, introduce Isolation Forest. Not before.

### 3.2 Network Health → Revenue Impact (Sprint 7, Week 9)

Every HIDS-detected outage automatically:
1. Identifies affected customer segment from network topology
2. Calculates combined MRR of affected customers
3. Estimates credit liability from SLA terms and outage duration
4. Displays to operations in real-time: "340 customers affected, combined MRR KES 280,000. Estimated credit claims: KES 14,000."

### 3.3 Proactive Credit Management

When HIDS detects significant degradation (configurable threshold — e.g. >30 min with packet loss >5%):
1. Identify affected customers automatically
2. Calculate credit per SLA terms
3. Draft credit notes — pending finance approval
4. Notify customers proactively before they file a ticket

This reduces support load and turns a service failure into a trust-building moment.

### New API Endpoints
```
GET  /api/finance/api/anomalies/              ?severity=high&resolved=false
PATCH /api/finance/api/anomalies/{id}/resolve/ Mark resolved with outcome
GET  /api/finance/api/network-revenue-impact/ Active outages with financial impact
POST /api/finance/api/credit-drafts/          Auto-draft credit notes from outage event
```

### New Frontend Tab
`AnomalyDetection.vue` — real-time anomaly feed via WebSocket, severity filtering, false-positive workflow, network impact financial summary panel.

---

## Phase 4: Executive Intelligence (Weeks 9–12)

### 4.1 KPI Command Centre (Sprint 8, Week 10)

Single screen for CEO/CFO morning review. Target load time under 2 seconds.

**Metric tiles** (wire existing endpoints first before building new ones):
- MRR: current vs. last month vs. annual target — from existing `/api/finance/api/metrics/`
- Active customers + month-over-month delta — from existing customer data
- Churn rate: trailing 30 days + trend — from existing churn calculation
- Cash position + 14-day projection — from Phase 2 forecast
- Outstanding receivables: total + 30/60/90-day aging buckets
- Network uptime trailing 7 days — from HIDS
- Revenue at risk: total MRR × churn probability — from Phase 1

**Weekly summary email** (Celery Beat, every Monday 7am):
- Top 3 business wins last week
- Top 3 risks this week with recommended actions
- Budget status per department
- High-risk customer count + revenue at risk

### 4.2 Automated Board Reporting (Sprint 10, Week 12)

Monthly board pack auto-generated from live data. Human reviews narrative before distribution.

Contents:
- Financial performance: revenue vs. budget, expense variance, margin trends
- Customer metrics: net new customers, churn rate, ARPU and CLV trends
- Operational metrics: uptime %, average ticket resolution time
- Risk register: active anomalies, at-risk customer summary, budget overruns
- Forward view: 90-day cash flow forecast, 3 scenarios

**Export formats**: PDF and PowerPoint. Narrative sections drafted via Claude API — flagged as AI-assisted, requiring human review before sending.

### 4.3 Pricing Intelligence (Sprint 10, Week 12)

Highest-leverage financial decision for ISPs after churn.

- Price elasticity by package: at what price point does meaningful churn increase appear?
- Package performance: revenue per GB, ARPU per tier, upgrade/downgrade flow
- Underperforming package identification
- Competitive gap input: manual entry of competitor pricing for positioning analysis

**Note**: Existing `/api/finance/api/package-performance/` provides base data. This adds the analytical layer on top. The system presents data only — humans make pricing decisions.

### 4.4 Supplier & Vendor Intelligence (Sprint 9, Week 11)

High-value for ISPs with multiple upstream providers:
- Bandwidth cost per upstream provider vs. usage delivered
- Cost-per-GB trend: are infrastructure costs rising faster than revenue?
- Invoice discrepancy flagging for vendors with consistent billing errors
- Contract expiry calendar with 90-day renewal alerts

**Note**: Builds on existing `Expense` model and vendor data.

### New API Endpoints
```
GET  /api/finance/api/kpi-summary/            Full executive dashboard payload
GET  /api/finance/api/pricing-intelligence/   Package performance + elasticity
GET  /api/finance/api/vendor-intelligence/    Supplier cost analysis
POST /api/finance/api/board-report/generate/  Trigger monthly report generation
GET  /api/finance/api/board-report/{id}/      Download PDF or PPTX
```

---

## Technology Stack

### Backend Additions
```
xgboost                  # Churn prediction (not Random Forest)
prophet                  # Cash flow forecasting (time-series — not XGBoost)
scikit-learn             # Logistic Regression for expense categorization
google-cloud-vision      # OCR — required for M-Pesa/local document accuracy
django-channels          # WebSocket for real-time anomaly alerts
celery-beat              # Scheduled ML retraining + weekly report generation
redis-streams            # Event bus for HIDS integration
psycopg2 + timescaledb   # Time-series performance — prerequisite for ML phases
anthropic                # Claude API for board report narrative generation
```

### Frontend Additions
```
apexcharts               # Financial dashboards (better suited than Chart.js for finance)
@tanstack/vue-query      # Data fetching with cache + background refresh
pinia                    # State management
socket.io-client         # Real-time anomaly and alert feeds
```

### New Vue Components (5 new tabs alongside existing 5)
```
ChurnPrevention.vue      # Risk dashboard + retention task queue
InvoiceUpload.vue        # OCR upload + extraction preview + approve-to-expense
CashFlowForecast.vue     # 3-scenario Prophet chart + alert configuration
AnomalyDetection.vue     # Real-time HIDS fraud alerts + resolution workflow
KPICommandCentre.vue     # Executive morning dashboard
```

Reconciliation, Pricing Intelligence, and Vendor Intelligence are sub-views within existing tabs where practical — to avoid tab overload in Finance.vue.

### Infrastructure
```
Celery workers: 3 dedicated queues (finance tasks, ML training, HIDS integration)
Redis: Separate instances for cache, task queue, WebSocket channels
PostgreSQL: TimescaleDB extension — install in Phase 0
Monitoring: Flower (Celery dashboard) + /api/health/ endpoint
```

---

## Complete Timeline

| Sprint | Weeks | Deliverable | Business Value | Depends On |
|--------|-------|-------------|----------------|------------|
| 0 | 1–2 | Data audit + TimescaleDB + Event bus + Model registry | Foundation only | Nothing |
| 1 | 3 | Churn v1 (rule-based) + revenue at risk dashboard | First retention alerts | Sprint 0 |
| 2 | 4 | Churn v2 (XGBoost, if AUC>0.75) + retention workflow | Measurable churn reduction | Sprint 1 |
| 3 | 5 | OCR pipeline (Cloud Vision) + invoice review queue | Expense entry time −60% | Sprint 0 |
| 4 | 6 | Cash flow forecast (Prophet) + threshold alerts | CFO forward visibility | Sprint 0 |
| 5 | 7 | Reconciliation engine + bank statement upload | Accounting hours saved | Sprint 0 |
| 6 | 8 | HIDS fraud correlation (rule engine, 4 rules) | Fraud detection live | Sprint 0 |
| 7 | 9 | Network health → revenue impact + proactive credits | Ops financial context | Sprint 6 |
| 8 | 10 | KPI Command Centre | Executive morning briefing | Sprints 1–7 |
| 9 | 11 | Budget intelligence + vendor analysis | Finance team efficiency | Existing models |
| 10 | 12 | Board report automation + pricing intelligence | Strategic decision support | All previous |

---

## What to Deprioritize

These features have poor ROI at the current stage:

- **Investment recommendations via ML** — The existing investment tracking model is sufficient. Cash surplus decisions belong to CFO and board, not an algorithm.
- **Compliance automation** — Kenya tax rules change. A rules engine you trust less than your accountant creates liability, not value.
- **Sentiment analysis on support tickets** — Requires labelled training data that doesn't exist yet. Revisit after 12 months.
- **Automated repricing** — Never automate without mandatory human approval. The pricing intelligence feature presents data only.
- **Random Forest for any feature** — XGBoost is strictly better for every classification task in this system.

---

## Success Metrics

Measure baselines before building. Without baselines you cannot demonstrate ROI.

| Metric | How to Baseline | 90-Day Target |
|--------|----------------|---------------|
| Monthly churn rate | Pull from existing RevenueStream churn calculation | Reduce by 20% |
| Expense entry time | Time 10 manual entries | Reduce by 50% |
| Cash forecast accuracy | N/A — new capability | Within 15% at 30-day horizon |
| Fraud false positive rate | N/A — new capability | Below 5% |
| Reconciliation hours/month | Finance team tracks for 2 weeks | Reduce by 40% |
| Monthly report prep time | Finance team tracks for 1 month | Reduce by 70% |
| Retention task completion rate | N/A — new capability | 80%+ of high-risk alerts actioned within 48h |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OCR accuracy too low on local documents | High | Medium | Cloud Vision over Tesseract. Human review queue for <80% confidence. Vendor templates for top 20 suppliers. |
| Churn model underperforms (AUC < 0.75) | Medium | High | Rule-based fallback always active. XGBoost only promoted if validated. |
| HIDS correlation generates alert fatigue | High | Medium | Only 4 high-signal rules. Conservative thresholds. Weekly false-positive review. |
| TimescaleDB migration disrupts queries | Low | High | Parallel migration. Full rollback tested before cutover. |
| Staff don't adopt new workflows | Medium | High | Train on 3 key screens only. Existing workflows remain as fallback. |
| Rebuilding features that already exist | Medium | Medium | Review existing models.py and Finance.vue before starting each sprint. |
| Prophet misleading due to insufficient history | Medium | Medium | Require 12+ months of PaymentTransaction data. Show confidence intervals prominently. |

---

## Complete API Contract

```
# Existing endpoints (already built — do not rebuild)
GET  /api/finance/api/revenue-streams/
GET  /api/finance/api/expenses/
GET  /api/finance/api/investments/
GET  /api/finance/api/departments/
GET  /api/finance/api/metrics/                    MRR, ARR, ARPU, LTV
GET  /api/finance/api/package-performance/
GET  /api/finance/api/transaction-stats/

# Phase 1 — Customer Intelligence
GET  /api/finance/api/churn-predictions/          ?risk_level=high&ordering=-predicted_revenue_at_risk
GET  /api/finance/api/revenue-at-risk/            Aggregate + week trend
POST /api/finance/api/retention-tasks/
PATCH /api/finance/api/retention-tasks/{id}/      Record outcome
GET  /api/finance/api/retention-tasks/            My open tasks

# Phase 2 — Financial Intelligence
POST /api/finance/api/upload-invoice/
GET  /api/finance/api/invoices/                   ?status=review
PATCH /api/finance/api/invoices/{id}/approve/
GET  /api/finance/api/cash-flow-forecast/         ?horizon=30|90|180&scenario=base
POST /api/finance/api/reconcile/
GET  /api/finance/api/reconcile/{id}/
PATCH /api/finance/api/reconcile/{id}/approve/

# Phase 3 — HIDS Integration
GET  /api/finance/api/anomalies/                  ?severity=high&resolved=false
PATCH /api/finance/api/anomalies/{id}/resolve/
GET  /api/finance/api/network-revenue-impact/
POST /api/finance/api/credit-drafts/

# Phase 4 — Executive Layer
GET  /api/finance/api/kpi-summary/
GET  /api/finance/api/pricing-intelligence/
GET  /api/finance/api/vendor-intelligence/
POST /api/finance/api/board-report/generate/
GET  /api/finance/api/board-report/{id}/
```

All endpoints: JWT authentication, response time target <500ms, cursor-based pagination where result sets exceed 100 records.

---

## Per-Sprint Checklist

**Before starting each sprint**:
1. Review "What Already Exists" — confirm you're not rebuilding something
2. Check Model Registry for any active models relevant to the feature
3. Verify TimescaleDB migration is complete (required for Sprints 1+)
4. Confirm event bus is wired (required for real-time features)
5. Measure and record success metric baseline if not already done

**Before marking each sprint complete**:
1. Feature tested with real production data, not fixtures
2. Fallback behaviour verified — what happens if the ML model is unavailable?
3. Error states handled in frontend: loading, empty state, error
4. New endpoint added to API contract above
5. Success metric measured and recorded against baseline

---

*Version 3.0 — Updated to incorporate dev AI review findings: ML engine clarification (XGBoost over Random Forest; Prophet for forecasting; rules engine for fraud), existing foundation acknowledgment (multi-currency, approvals, revenue streams, investments), sprint-based delivery structure, and per-sprint checklists. Review and update monthly as features ship.*
