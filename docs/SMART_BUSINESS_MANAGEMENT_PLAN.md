# Smart Business Management System — Comprehensive Implementation Plan

**Version**: 2.0 — Enterprise-Grade Rebuild  
**Target**: ISP / Telecoms Operations (TeralinkX)  
**Horizon**: 90-Day Phased Rollout  
**Philosophy**: Ship value every week. Every feature must answer: *"What decision does this help someone make faster?"*

---

## Executive Summary

This plan transforms TeralinkX's finance module into a full **Smart Business Management (SBM)** platform — integrating AI-assisted finance, customer intelligence, operations awareness, and executive decision support into a unified system. The HIDS network layer is treated as a first-class data source, not a bolt-on.

The original 2-day sprint was a proof of concept. This plan is designed to be maintainable, scalable, and genuinely useful — not just technically impressive.

---

## Core Design Principles

1. **Accuracy over impressiveness** — A churn score you trust is worth more than a fancy ML model you can't validate.
2. **Explainability** — Every AI output must include *why*. No black-box recommendations.
3. **Graceful degradation** — If ML models aren't trained yet, fall back to rule-based logic. Never show empty dashboards.
4. **Operator-first UX** — Staff using this daily are not data scientists. Every screen should be actionable in under 30 seconds.
5. **HIDS as signal, not noise** — Network anomalies are correlated with financial events only when the correlation is statistically meaningful. No false urgency.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    TeralinkX SBM Platform                    │
├──────────────┬──────────────────┬───────────────────────────┤
│  Intelligence│   Operations     │    Executive Layer         │
│  Engine      │   Core           │                            │
│              │                  │  • KPI Command Centre      │
│  • Churn ML  │  • Billing       │  • Board-ready Reports     │
│  • Fraud Det.│  • Provisioning  │  • Cash Flow Forecast      │
│  • OCR/Docs  │  • Support Tkts  │  • Budget Optimizer        │
│  • Anomalies │  • Network (HIDS)│  • Pricing Intelligence    │
└──────┬───────┴──────────────────┴──────────┬────────────────┘
       │                                      │
       ▼                                      ▼
  Django REST API                       Vue.js Admin Panel
  Celery + Redis                        Real-time WebSocket
  PostgreSQL + TimescaleDB              ApexCharts / Chart.js
```

---

## Phase 0: Foundation Hardening (Week 1–2)

**Goal**: Fix what will break everything else if ignored.

### 0.1 Data Quality Audit
Before building ML models, audit existing data:
- Payment transaction completeness (null rates, duplicate transactions)
- Customer records hygiene (missing fields, orphaned accounts)
- Expense categorization consistency (current manual categories)
- Exchange rate update frequency (stale rates = wrong reporting)

**Deliverable**: Data quality dashboard showing completeness % per entity. Fix anything below 90%.

### 0.2 TimescaleDB Migration (5-Week Gradual Rollout)
Replace standard PostgreSQL time-series queries with TimescaleDB hypertables for:
- PaymentTransaction (query: last 12 months by customer — currently slow)
- NetworkAnomalies from HIDS
- Session data for churn features

**Why**: Cash flow forecasting and churn models query millions of time-series rows. Without this, forecasts will time out in production.

**Migration strategy** (gradual rollout with feature flags):
- Week 1: Install TimescaleDB extension, create hypertables, implement dual-write (write to both old + new tables)
- Week 2: Backfill historical data, validate row counts and data integrity
- Week 3: Enable dual-read for 10% of queries via feature flags, compare results
- Week 4: Ramp to 50%, monitor performance metrics and error rates
- Week 5: Full cutover to TimescaleDB, keep old tables for 2-week rollback window

**Feature flag implementation**:
```python
class FeatureFlag(models.Model):
    name = models.CharField(max_length=100)  # 'use_timescaledb_payments'
    enabled = models.BooleanField(default=False)
    rollout_percentage = models.IntegerField(default=0)  # 0-100

# Query layer with dual-read capability
def get_payment_history(customer_id, months=12):
    if FeatureFlag.is_enabled('use_timescaledb_payments'):
        return _query_timescale(customer_id, months)
    else:
        return _query_postgres(customer_id, months)
```

### 0.3 Event Bus
Install Django Signals + Celery event routing:
- `payment.completed` → trigger churn model refresh for that customer
- `expense.created` → trigger budget utilization recalc
- `hids.anomaly` → trigger fraud correlation check
- `invoice.uploaded` → trigger OCR pipeline

**Why**: Without this, all "smart" features are just batch jobs running on cron — not real-time intelligence.

### 0.4 Model Registry
Create `MLModel` table:
```python
class MLModel(models.Model):
    name = models.CharField(max_length=100)  # 'churn_v1', 'fraud_v2'
    version = models.CharField(max_length=20)
    trained_at = models.DateTimeField()
    accuracy_score = models.FloatField()
    feature_importance = models.JSONField()
    is_active = models.BooleanField(default=False)
    fallback_strategy = models.CharField(max_length=50)  # 'rules', 'previous_version'
```

Every AI feature checks this registry and degrades gracefully when no active model exists.

---

## Phase 1: Customer Intelligence (Week 3–5)

**Business value**: Preventing one high-value customer from churning pays for this entire phase.

### 1.1 Churn Prediction — Production-Grade

**What the original plan got wrong**: Rule-based scoring is fine to start, but the features were too shallow. Late payment alone is a weak signal. What actually predicts churn in ISPs:

**Feature Set (importance ranked)**:
1. Days since last session (strongest signal)
2. Support tickets in last 90 days (especially billing disputes)
3. Average session duration trend (declining = disengaging)
4. Payment method changes (sign of financial stress)
5. Package downgrade history
6. Peer comparison (is their usage below their package tier?)
7. Seasonal adjustment (long silence in Dec ≠ churn; in March = problem)

**Model**: Start with Gradient Boosted Trees (XGBoost), not Random Forest. Better with imbalanced datasets (churners are rare). Retrain weekly.

**Validation requirement**: Before going live, model must achieve AUC > 0.75 on held-out test set. If not, stay on rule-based.

**Output schema**:
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

Note: `predicted_revenue_at_risk` = CLV × churn_probability. This is the number that gets an executive to act.

### 1.2 Retention Workflow

The prediction is useless without execution. Build an automated retention workflow:

**Task creation with automated workflow** (no manual outreach):
1. Churn alert fires → calculate priority score (revenue × probability × urgency)
2. Check for duplicate open tasks (skip if customer already has active task)
3. **Automated retention actions** (no human contact needed):
   - High-value customers (>KES 5,000/month): Auto-apply 20% loyalty discount for 3 months
   - Medium-value customers: Send automated SMS with 10% discount offer
   - Low-value customers: Send re-engagement SMS (no discount)
4. Track outcome automatically:
   - **Retained**: Customer makes payment within 14 days of offer
   - **Churned**: No activity for 60 days after offer
   - **Relocated**: No sessions + outside coverage area (detected via last known location)
5. Tasks only escalate to human review if high-value customer (>KES 10,000/month) doesn't respond to automated offer

**Priority scoring algorithm**:
```python
Priority = Revenue at Risk × Churn Probability × Urgency Factor
Urgency = max(1, 7 - days_until_due)  # Higher score for sooner deadlines
```

**Outcome tracking** (adjusted for ISP operations):
- **Retained**: Customer resumed service, record retention offer used
- **Churned**: Customer confirmed inactive (no sessions for 60+ days)
- **Relocated**: Customer moved outside coverage area (not actionable)
- **Auto-resolved**: Customer resumed service before outreach needed

**Note**: Given small coverage area, "contacted but no response" likely means customer relocated. System auto-marks as "relocated" if no session activity for 90 days + no response to automated SMS.

**Dashboard view**: Tasks sorted by priority score (not chronologically), showing revenue at risk and automated action taken.

Without the feedback loop, the model never improves. Outcomes feed back into weekly model retraining.

### 1.3 Revenue at Risk Dashboard

Weekly view showing:
- Total MRR at risk (sum of monthly revenue × churn probability for all high-risk customers)
- Trend vs last week
- Automated retention offers sent this week / outcomes
- Top 10 highest-value accounts at risk (auto-flagged for discount offers)
- Relocated customers (removed from at-risk calculation — not actionable)

---

## Phase 2: Financial Intelligence (Week 5–8)

### 2.1 Document Processing — Digital-First Approach

**Operational reality**: TeralinkX deals primarily with digital documents:
- M-Pesa transaction confirmations (SMS/email format — already structured)
- Bank statements (CSV/PDF downloads — parseable)
- Vendor invoices (mostly email PDFs with consistent formats)
- System-generated receipts (already in database)
- Physical receipts (rare — stored as images/scanned PDFs for record-keeping only)

**Simplified approach** (no OCR needed for 90% of documents):

**1. Structured data ingestion** (primary path):
- M-Pesa: Already captured via callback API → PaymentTransaction
- Bank statements: CSV upload → auto-match to invoices via reconciliation engine
- Vendor invoices: Email forwarding → parse PDF text (not OCR) → extract amount/date/vendor
- System receipts: Already in TransactionQueue/PaymentTransaction

**2. Manual entry with templates** (for exceptions):
- Pre-filled expense forms for common vendors (fuel, utilities, maintenance)
- Attach image/PDF as supporting document (stored, not processed)
- No OCR — staff enters data, system validates against budget

**3. Optional OCR for future expansion** (deprioritized):
- Only if physical receipt volume increases (unlikely for ISP operations)
- Use Tesseract for basic text extraction on scanned receipts
- No Cloud Vision API needed — cost not justified for rare use case

**Implementation priority**: Low (Week 10-12, only if time permits)
**Cost**: $0 (no external API, use existing PDF parsing libraries)

### 2.2 Cash Flow Forecasting

**Model**: Facebook Prophet (handles Kenyan business seasonality — month-end payment spikes, school term patterns for home internet, etc.)

**Three forecast tracks**:
1. **Optimistic** (P10): assumes current retention holds, all renewals convert
2. **Base** (P50): accounts for average churn rate, delayed payments
3. **Conservative** (P90): assumes elevated churn, 30% late payment rate

**Alert triggers**:
- "Cash position projected to drop below KES 500,000 in 14 days" → Notify CFO
- "Unusually high expense forecast for next month" → Flag for review
- "MRR growth rate slowing — Q3 target at risk" → Board-level alert

### 2.3 Automated Reconciliation

**What the original plan got wrong**: Fuzzy matching alone produces too many false matches. ISPs have complex scenarios:
- One payment → multiple customer accounts (family plan payer)
- Payment slightly different from invoice (bank charges deducted)
- M-Pesa payment reference doesn't match invoice number

**Matching strategy with confidence scoring**:

Calculate confidence score (0-100) based on weighted factors:
- **Amount match**: 50 points (exact) / 35 points (±2%) / 20 points (±5%)
- **Customer match**: 30 points (ID exact) / 20 points (name fuzzy, Levenshtein < 3)
- **Date proximity**: 15 points (±3 days) / 5 points (±7 days)
- **Phone match**: 5 points (MPESA number matches customer phone)

**Action thresholds**:
- **≥85 confidence**: Auto-match, create transaction link, notify user
- **60-84 confidence**: Create suggested match, flag for review with explanation
- **<60 confidence**: Manual queue, show top 3 candidates with scores

**Human review queue sorted by**:
1. Payment amount (largest first — highest financial impact)
2. Days since payment (oldest first — aging matters)
3. Confidence of best candidate (highest first — easier decisions)

**Implementation**:
```python
class ReconciliationMatch:
    def calculate_confidence(self, payment, invoice):
        score = 0.0
        
        # Amount matching
        if payment.amount == invoice.amount:
            score += 50
        elif abs(payment.amount - invoice.amount) / invoice.amount < 0.02:
            score += 35
        elif abs(payment.amount - invoice.amount) / invoice.amount < 0.05:
            score += 20
        
        # Customer matching
        if payment.customer_id == invoice.customer_id:
            score += 30
        elif self.fuzzy_match(payment.customer_name, invoice.customer_name) < 3:
            score += 20
        
        # Date proximity
        if abs((payment.date - invoice.date).days) <= 3:
            score += 15
        elif abs((payment.date - invoice.date).days) <= 7:
            score += 5
        
        # Phone number
        if payment.mpesa_phone == invoice.customer_phone:
            score += 5
        
        return min(score, 100)
    
    def get_match_action(self, confidence):
        if confidence >= 85:
            return 'auto_match'
        elif confidence >= 60:
            return 'suggest_review'
        else:
            return 'manual_queue'
```

**Output**: Reconciliation report showing matched %, unmatched items by priority, average confidence score, and estimated time to clear.

### 2.4 Budget Intelligence

Replace static budget alerts with dynamic intelligence:
- Budget utilization rate vs. days remaining in period (80% spent with 60% of month gone = on track, not alarming)
- Variance analysis: "Marketing overspent by KES 45K vs plan — driven by 3 large events"
- Rolling 3-month spend trends per department
- Budget request assistant: department head fills simple form, system generates business case draft

---

## Phase 3: HIDS Financial Integration (Week 7–9)

This is where TeralinkX has a genuine competitive advantage. No standard finance system has network context.

### 3.1 Fraud Correlation Framework

**What the original plan got wrong**: Correlating any network anomaly with any transaction is too noisy. You need specific correlation rules:

**High-signal correlations**:
- Large payment from IP showing port-scan behavior in same 5-minute window → fraud flag
- Payment from IP geolocation inconsistent with account's registered location → review
- Multiple payments from different accounts on same IP address → shared device, potential fraud
- Payment immediately after suspicious DNS queries (phishing domains) → block and alert

**Low-signal correlations** (don't alert on these):
- Generic bandwidth anomaly at time of payment → too common, too noisy
- Payment after unusual hours + IP is a known VPN exit node → probably fine, log only

**Implementation**: Rule engine with configurable thresholds, not pure ML. Transparency matters for fraud decisions.

### 3.2 Network Health → Revenue Impact

Link network events to revenue metrics:
- Outage duration → estimated revenue at risk (customers likely to request credits)
- Packet loss spikes → correlate with support ticket volume 24h later
- Node failures → map to affected customer segments + their ARPU

This gives operations a financial lens: "This outage affects 340 customers with combined MRR of KES 280,000. Estimated credit claims: KES 14,000."

### 3.3 Proactive Credit Management

When HIDS detects significant service degradation:
1. Identify affected customers automatically
2. Calculate service credits per SLA terms
3. Draft credit notes, pending finance approval
4. Notify customers proactively (before they complain)

This reduces support load and churn risk from outages.

---

## Phase 4: Executive Intelligence (Week 9–12)

### 4.1 KPI Command Centre

Single screen for CEO/CFO morning review (loads in < 100ms via pre-computed cache):

**Real-time tiles** (refreshed every 5 minutes):
- MRR (current vs. last month vs. target)
- Active customers (vs. last month)
- Churn rate (trailing 30 days)
- Cash position (vs. 30 days ago)
- Outstanding receivables (aging buckets)
- Network uptime (trailing 7 days)

**Caching implementation**:
```python
# models.py
class KPISnapshot(models.Model):
    """Pre-computed KPI values, refreshed every 5 minutes"""
    timestamp = models.DateTimeField(auto_now_add=True)
    mrr_current = models.DecimalField(max_digits=12, decimal_places=2)
    mrr_last_month = models.DecimalField(max_digits=12, decimal_places=2)
    mrr_target = models.DecimalField(max_digits=12, decimal_places=2)
    active_customers = models.IntegerField()
    churn_rate_30d = models.FloatField()
    cash_position = models.DecimalField(max_digits=12, decimal_places=2)
    outstanding_receivables = models.JSONField()  # Aging buckets
    network_uptime_7d = models.FloatField()
    computed_in_ms = models.IntegerField()  # Track computation time
    
    class Meta:
        indexes = [models.Index(fields=['-timestamp'])]

# tasks.py
@shared_task
def refresh_kpi_cache():
    start = time.time()
    
    snapshot = KPISnapshot.objects.create(
        mrr_current=calculate_mrr(),
        mrr_last_month=calculate_mrr(month_offset=1),
        mrr_target=get_mrr_target(),
        active_customers=Customer.objects.filter(status='active').count(),
        churn_rate_30d=calculate_churn_rate(days=30),
        cash_position=get_cash_position(),
        outstanding_receivables=get_receivables_aging(),
        network_uptime_7d=get_network_uptime(days=7),
        computed_in_ms=int((time.time() - start) * 1000)
    )
    
    # Keep only last 24 hours of snapshots
    KPISnapshot.objects.filter(
        timestamp__lt=timezone.now() - timedelta(hours=24)
    ).delete()
    
    return snapshot.id

# views.py
class KPISummaryView(APIView):
    def get(self, request):
        snapshot = KPISnapshot.objects.latest('timestamp')
        
        # If snapshot is > 10 minutes old, trigger refresh async
        if timezone.now() - snapshot.timestamp > timedelta(minutes=10):
            refresh_kpi_cache.delay()
        
        return Response({
            'mrr': {
                'current': snapshot.mrr_current,
                'last_month': snapshot.mrr_last_month,
                'target': snapshot.mrr_target,
                'vs_last_month_pct': calculate_change_pct(
                    snapshot.mrr_current, snapshot.mrr_last_month
                )
            },
            'customers': {
                'active': snapshot.active_customers,
                'churn_rate_30d': snapshot.churn_rate_30d
            },
            'cash': {
                'position': snapshot.cash_position,
                'receivables': snapshot.outstanding_receivables
            },
            'network': {
                'uptime_7d': snapshot.network_uptime_7d
            },
            'meta': {
                'computed_at': snapshot.timestamp,
                'computation_time_ms': snapshot.computed_in_ms,
                'age_seconds': (timezone.now() - snapshot.timestamp).total_seconds()
            }
        })
```

**Weekly summary** (auto-generated every Monday at 7am):
- Top 3 wins last week
- Top 3 risks this week
- Budget status (on track / at risk / over)
- Customers at high churn risk (count + revenue at risk)

### 4.2 Automated Board Reporting

Monthly board pack auto-generated from live data:
- Financial performance vs. budget
- Customer metrics (acquisition, churn, ARPU trends)
- Operational metrics (uptime, ticket resolution time)
- Risk register (financial anomalies, at-risk customers)
- 90-day cash flow forecast with scenarios

Format: Exportable to PDF and PowerPoint. Data refreshes automatically; narrative sections are AI-drafted but human-reviewed before distribution.

### 4.3 Pricing Intelligence

**For ISPs, pricing is the highest-leverage financial decision**:
- Price elasticity analysis: at what price point does package X see meaningful churn increase?
- Competitive positioning: where are you vs. market (requires periodic manual input of competitor pricing)
- Package performance: revenue per GB, ARPU per package tier, upgrade/downgrade rates
- Recommendation: "Package B customers have 40% lower churn than Package A at similar price — consider consolidating"

**Important caveat**: Pricing recommendations require business judgment. The system presents data and options; humans decide.

### 4.4 Supplier & Vendor Intelligence

Often neglected but high-value for ISPs:
- Track bandwidth costs per upstream provider vs. usage
- Flag vendors with consistent invoice discrepancies
- Contract expiry calendar with renewal recommendations
- Cost per GB trend analysis (are infrastructure costs rising faster than revenue?)

---

## Technology Stack

### Backend Additions
```
django-channels          # WebSocket for real-time alerts
celery[redis]           # Task queue + beat scheduler (includes celery-beat)
xgboost                 # Churn prediction
prophet                 # Cash flow forecasting
google-cloud-vision     # OCR (replace Tesseract)
redis                   # Cache + queue + streams (single instance, multiple DBs)
psycopg2-binary         # PostgreSQL adapter
django-celery-beat      # Database-backed periodic tasks
```

### Celery Configuration
```python
# settings.py
CELERY_BROKER_URL = 'redis://redis:6379/0'
CELERY_RESULT_BACKEND = 'redis://redis:6379/0'

CELERY_BEAT_SCHEDULE = {
    'retrain-churn-model': {
        'task': 'finance.tasks.retrain_churn_model',
        'schedule': crontab(day_of_week=1, hour=2, minute=0),  # Monday 2am
    },
    'generate-cash-forecast': {
        'task': 'finance.tasks.generate_cash_forecast',
        'schedule': crontab(hour=1, minute=0),  # Daily 1am
    },
    'refresh-kpi-cache': {
        'task': 'finance.tasks.refresh_kpi_cache',
        'schedule': crontab(minute='*/5'),  # Every 5 minutes
    },
    'process-pending-ocr': {
        'task': 'finance.tasks.process_pending_ocr',
        'schedule': crontab(minute='*/10'),  # Every 10 minutes
    },
    'check-hids-correlations': {
        'task': 'finance.tasks.check_hids_correlations',
        'schedule': crontab(minute='*/2'),  # Every 2 minutes
    },
}

# Separate queues for different priorities
CELERY_TASK_ROUTES = {
    'finance.tasks.process_ocr': {'queue': 'ocr'},
    'finance.tasks.retrain_churn_model': {'queue': 'ml'},
    'finance.tasks.train_fraud_model': {'queue': 'ml'},
    'finance.tasks.check_hids_correlation': {'queue': 'hids'},
    'finance.tasks.*': {'queue': 'default'},
}
```

### Frontend Additions
```
apexcharts              # Better than Chart.js for financial dashboards
vue-query               # Data fetching with cache + background refresh
pinia                   # State management (replace manual reactive)
socket.io-client        # Real-time anomaly alerts
```

### Infrastructure

**Redis configuration** (single instance, multiple databases):
```yaml
redis:
  image: redis:7-alpine
  command: redis-server --maxmemory 2gb --maxmemory-policy allkeys-lru
  volumes:
    - redis_data:/data
  ports:
    - "6379:6379"

# Database allocation:
# DB 0: Celery broker + results
# DB 1: Django cache
# DB 2: Session storage
# DB 3: Real-time streams (HIDS events)
```

**Celery workers** (4 queues, 11 total workers):
```yaml
celery-default:
  command: celery -A teralinkx worker -Q default -c 4 --loglevel=info
  deploy:
    replicas: 1
  
celery-ml:
  command: celery -A teralinkx worker -Q ml -c 2 --loglevel=info
  deploy:
    replicas: 1
  
celery-ocr:
  command: celery -A teralinkx worker -Q ocr -c 3 --loglevel=info
  deploy:
    replicas: 1
  
celery-hids:
  command: celery -A teralinkx worker -Q hids -c 2 --loglevel=info
  deploy:
    replicas: 1
  
celery-beat:
  command: celery -A teralinkx beat --scheduler django_celery_beat.schedulers:DatabaseScheduler --loglevel=info
  deploy:
    replicas: 1
```

**PostgreSQL with TimescaleDB**:
```yaml
postgres:
  image: timescale/timescaledb:latest-pg15
  environment:
    POSTGRES_DB: teralinkx
    POSTGRES_USER: teralinkx
    POSTGRES_PASSWORD: ${DB_PASSWORD}
    TIMESCALEDB_TELEMETRY: off
  volumes:
    - postgres_data:/var/lib/postgresql/data
  command: postgres -c shared_preload_libraries=timescaledb -c max_connections=200
  shm_size: 256mb
```

**Monitoring**:
- Flower (Celery monitoring): http://localhost:5555
- Django health endpoint: /api/health/ (checks DB, Redis, Celery queues)
- Custom metrics exposed:
  - Task queue depth per queue
  - ML model accuracy scores
  - OCR confidence distribution
  - HIDS correlation hit rate
  - KPI cache age

---

## Realistic Timeline

| Week | Deliverable | Business Value |
|------|-------------|----------------|
| 1–2 | Data audit + TimescaleDB + Event bus | Foundation only |
| 3 | Churn model v1 (rule-based) + dashboard | First actionable retention alerts |
| 4 | Churn model v2 (XGBoost) + retention workflow | Measurable churn reduction begins |
| 5 | OCR pipeline (Cloud Vision) + review queue | Expense entry time cut by 60% |
| 6 | Cash flow forecast (Prophet) + alerts | CFO gets forward visibility |
| 7 | Reconciliation engine + bank statement upload | Accounting hours saved weekly |
| 8 | HIDS fraud correlation (rule engine) | Fraud detection goes live |
| 9 | Network health → revenue impact | Ops gets financial context |
| 10 | KPI Command Centre | Executive morning briefing |
| 11 | Budget intelligence + variance analysis | Finance team efficiency |
| 12 | Board report automation + pricing intel | Strategic decision support |

---

## What to Deprioritize

These features are in the original plan but have poor ROI for now:

- **Investment recommendations**: TeralinkX is an ISP, not an investment firm. Cash surplus decisions need human judgment, not ML.
- **Compliance automation**: Kenya tax compliance rules change. A rules engine you trust less than your accountant creates liability, not value.
- **Sentiment analysis on support tickets**: Useful eventually, but requires sufficient ticket volume and labelled training data you don't have yet.
- **Real-time pricing optimization**: Price changes are strategic decisions, not algorithmic ones. Automated repricing without human review is dangerous for customer relationships.

---

## Success Metrics

Define these before building, measure from day one:

| Metric | Baseline | 90-Day Target |
|--------|----------|---------------|
| Monthly churn rate | Measure now | Reduce by 20% |
| Expense entry time | Measure now | Reduce by 50% |
| Cash forecast accuracy | N/A | Within 15% at 30-day horizon |
| Fraud detection (false positive rate) | N/A | < 5% |
| Finance staff hours on reconciliation | Measure now | Reduce by 40% |
| Time to generate monthly report | Measure now | Reduce by 70% |

---

## Risk Register

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OCR accuracy too low on local documents | High | Medium | Use Cloud Vision; build manual review queue |
| Churn model biased (insufficient training data) | Medium | High | Validate before deploying; keep rule-based fallback |
| HIDS correlation generates alert fatigue | High | Medium | Conservative thresholds; weekly tuning reviews |
| TimescaleDB migration breaks existing queries | Medium | Critical | Feature flags + dual-write + 5-week gradual rollout + 2-week rollback window |
| Staff don't adopt new workflows | Medium | High | Train on 3 key screens only; keep old workflow as fallback |
| Reconciliation false positives overwhelm review queue | Medium | Medium | Confidence scoring + priority sorting + auto-match threshold at 85% |
| Retention task overload (too many alerts) | Medium | Medium | Cap at 5 tasks per manager + team queue overflow + priority scoring |
| KPI endpoint timeouts under load | High | Medium | Pre-computed snapshots every 5 min + async refresh triggers |

---

## Appendix A: API Contract Summary

```
POST /api/finance/api/upload-invoice/
     Description: OCR + extraction with confidence scoring
     Response time: < 3s (async processing)
     Returns: extraction_id, confidence, status

GET  /api/finance/api/churn-predictions/
     Description: Paginated churn predictions
     Filters: ?risk_level=high|medium|low&assigned=true|false
     Response time: < 300ms
     Returns: customer, probability, factors, recommended_actions

GET  /api/finance/api/cash-flow-forecast/
     Description: Multi-scenario cash flow projection
     Params: ?horizon=30|90|180&scenario=optimistic|base|conservative
     Response time: < 500ms
     Returns: daily projections, alerts, confidence intervals

POST /api/finance/api/reconcile/
     Description: Upload bank statement for auto-matching
     Response time: < 5s (async processing)
     Returns: job_id, estimated_completion

GET  /api/finance/api/reconcile/{job_id}/results/
     Description: Get reconciliation results
     Response time: < 200ms
     Returns: matched_count, unmatched_items with confidence scores

GET  /api/finance/api/anomalies/
     Description: Financial + network anomalies
     Filters: ?severity=high&resolved=false&type=fraud|network
     Response time: < 300ms
     Returns: anomaly details, correlation data, suggested actions

GET  /api/finance/api/revenue-at-risk/
     Description: Aggregate revenue at risk from churn
     Response time: < 200ms
     Returns: total_mrr_at_risk, trend, top_accounts

GET  /api/finance/api/kpi-summary/
     Description: Executive dashboard KPIs (pre-computed, refreshed every 5 min)
     Response time: < 100ms (cached)
     Returns: mrr, customers, cash, network, meta (includes data age)

GET  /api/finance/api/network-revenue-impact/
     Description: HIDS event correlation with revenue
     Filters: ?event_type=outage|anomaly&start_date=YYYY-MM-DD
     Response time: < 400ms
     Returns: affected_customers, revenue_impact, credit_estimates

POST /api/finance/api/retention-tasks/
     Description: Create retention outreach task
     Response time: < 200ms
     Returns: task_id, assigned_to, priority_score, due_date

PATCH /api/finance/api/retention-tasks/{id}/
     Description: Update task status and record outcome
     Response time: < 200ms
     Body: {status, outcome, notes, offer_used}
     Returns: updated task

GET  /api/finance/api/retention-tasks/
     Description: List retention tasks
     Filters: ?status=pending&assigned_to=me&sort=priority
     Response time: < 300ms
     Returns: paginated tasks sorted by priority
```

All endpoints: JWT auth, paginated where > 100 records possible, include rate limiting (100 req/min per user).

---

*Plan authored: 2026. Review and update monthly as features ship and data quality improves.*


## Appendix B: Celery Task Reference

### Scheduled Tasks (Celery Beat)

| Task | Schedule | Queue | Purpose | Avg Duration |
|------|----------|-------|---------|--------------|
| `retrain_churn_model` | Monday 2am | ml | Retrain XGBoost model with last week's outcomes | 15-20 min |
| `generate_cash_forecast` | Daily 1am | ml | Run Prophet forecast for next 30/90/180 days | 5-10 min |
| `refresh_kpi_cache` | Every 5 min | default | Pre-compute KPI dashboard values | 30-60 sec |
| `process_pending_ocr` | Every 10 min | ocr | Process queued invoice uploads | 2-5 min |
| `check_hids_correlations` | Every 2 min | hids | Correlate network anomalies with transactions | 10-30 sec |
| `cleanup_old_snapshots` | Daily 3am | default | Delete KPI snapshots > 24h old | 5 sec |
| `escalate_stale_tasks` | Every hour | default | Escalate retention tasks not contacted in 24h | 10 sec |
| `update_exchange_rates` | Daily 6am | default | Fetch latest KES exchange rates | 5 sec |

### Event-Driven Tasks (Triggered by Signals)

| Task | Trigger | Queue | Purpose |
|------|---------|-------|----------|
| `calculate_churn_score` | payment.completed | ml | Update customer churn probability |
| `process_ocr_document` | invoice.uploaded | ocr | Extract data from uploaded document |
| `check_fraud_correlation` | hids.anomaly | hids | Check if anomaly correlates with recent payment |
| `recalc_budget_utilization` | expense.created | default | Update department budget status |
| `create_retention_task` | churn.high_risk | default | Create task for account manager |
| `notify_account_manager` | retention_task.assigned | default | Send notification to assigned manager |
| `update_revenue_at_risk` | churn.score_changed | default | Recalculate MRR at risk |

### Manual Tasks (API-Triggered)

| Task | Endpoint | Queue | Purpose |
|------|----------|-------|----------|
| `reconcile_bank_statement` | POST /api/finance/api/reconcile/ | default | Match payments to invoices |
| `generate_board_report` | POST /api/finance/api/reports/board/ | default | Create monthly board pack |
| `export_financial_data` | POST /api/finance/api/export/ | default | Export to Excel/CSV |
| `recalculate_all_churn` | POST /api/finance/api/churn/recalculate-all/ | ml | Force recalc for all customers |

---

## Appendix C: Caching Strategy

### Cache Layers

**1. Pre-computed Snapshots (Database)**
- **What**: KPI dashboard values, cash flow forecasts, revenue at risk aggregates
- **TTL**: 5 minutes (refreshed by Celery Beat)
- **Storage**: PostgreSQL (KPISnapshot, CashFlowSnapshot models)
- **Invalidation**: Time-based only (no manual invalidation)
- **Why**: Complex aggregations that timeout if computed on-request

**2. Redis Cache (Application Layer)**
- **What**: Customer churn scores, ML model predictions, OCR results
- **TTL**: Varies by data type
  - Churn scores: 1 hour (invalidated on payment/session events)
  - ML model metadata: 24 hours (invalidated on model retrain)
  - OCR results: 7 days (never invalidated, historical record)
- **Storage**: Redis DB 1
- **Invalidation**: Event-driven (Django signals)

**3. Query Result Cache (ORM Level)**
- **What**: Customer lists, package definitions, vendor lists
- **TTL**: 15 minutes
- **Storage**: Redis DB 1
- **Invalidation**: Manual (on model save/delete)
- **Implementation**: `@cache_page(900)` decorator

**4. Session Cache**
- **What**: User sessions, authentication tokens
- **TTL**: 24 hours (sliding window)
- **Storage**: Redis DB 2
- **Invalidation**: On logout or token refresh

### Cache Warming Strategy

**Cold start prevention**:
- On deployment, trigger `refresh_kpi_cache` immediately
- Pre-compute churn scores for top 100 customers by revenue
- Load ML models into memory on worker startup

**Cache hit rate targets**:
- KPI dashboard: > 99% (only misses on first request after deployment)
- Churn predictions: > 85% (misses on new customers or after events)
- Customer lists: > 90%

### Monitoring Cache Health

```python
# Custom management command: python manage.py check_cache_health
from django.core.management.base import BaseCommand
from django.core.cache import cache
import redis

class Command(BaseCommand):
    def handle(self, *args, **options):
        r = redis.Redis(host='redis', port=6379, db=1)
        info = r.info('stats')
        
        hit_rate = info['keyspace_hits'] / (info['keyspace_hits'] + info['keyspace_misses'])
        
        self.stdout.write(f"Cache hit rate: {hit_rate:.2%}")
        self.stdout.write(f"Total keys: {r.dbsize()}")
        self.stdout.write(f"Memory used: {info['used_memory_human']}")
        
        # Check KPI snapshot freshness
        latest_snapshot = KPISnapshot.objects.latest('timestamp')
        age = (timezone.now() - latest_snapshot.timestamp).total_seconds()
        
        if age > 600:  # 10 minutes
            self.stdout.write(self.style.ERROR(f"KPI snapshot stale: {age}s old"))
        else:
            self.stdout.write(self.style.SUCCESS(f"KPI snapshot fresh: {age}s old"))
```

---

## Appendix D: Model Training & Validation

### Churn Model Training Pipeline

**Data preparation**:
```python
# Runs every Monday at 2am
@shared_task
def retrain_churn_model():
    # 1. Extract features for all customers with outcomes from last 90 days
    training_data = extract_churn_features(
        start_date=timezone.now() - timedelta(days=90),
        include_outcomes=True
    )
    
    # 2. Split: 80% train, 20% test (stratified by churn outcome)
    X_train, X_test, y_train, y_test = train_test_split(
        training_data.drop('churned', axis=1),
        training_data['churned'],
        test_size=0.2,
        stratify=training_data['churned'],
        random_state=42
    )
    
    # 3. Train XGBoost with class imbalance handling
    model = xgb.XGBClassifier(
        scale_pos_weight=len(y_train[y_train==0]) / len(y_train[y_train==1]),
        max_depth=6,
        learning_rate=0.1,
        n_estimators=100,
        eval_metric='auc'
    )
    model.fit(X_train, y_train)
    
    # 4. Validate on test set
    y_pred_proba = model.predict_proba(X_test)[:, 1]
    auc_score = roc_auc_score(y_test, y_pred_proba)
    
    # 5. Only deploy if AUC > 0.75
    if auc_score >= 0.75:
        # Save model
        model_path = f'/models/churn_v{get_next_version()}.pkl'
        joblib.dump(model, model_path)
        
        # Register in database
        MLModel.objects.create(
            name='churn_prediction',
            version=get_next_version(),
            trained_at=timezone.now(),
            accuracy_score=auc_score,
            feature_importance=dict(zip(
                training_data.columns[:-1],
                model.feature_importances_
            )),
            is_active=True,
            fallback_strategy='rules'
        )
        
        # Deactivate old model
        MLModel.objects.filter(
            name='churn_prediction',
            is_active=True
        ).exclude(version=get_next_version()).update(is_active=False)
        
        return f"Model deployed: AUC={auc_score:.3f}"
    else:
        return f"Model rejected: AUC={auc_score:.3f} < 0.75 threshold"
```

**Feature importance tracking**:
- Store feature importance in MLModel.feature_importance JSON field
- Display in admin panel to understand what drives predictions
- Alert if top features change significantly between versions (model drift)

**Validation metrics tracked**:
- AUC-ROC (primary metric, must be > 0.75)
- Precision at top 10% (how accurate are high-risk predictions?)
- Recall at 50% threshold (what % of actual churners do we catch?)
- False positive rate (how many false alarms?)

### Graceful Degradation

If no active ML model exists (first deployment or all models rejected):

```python
def get_churn_prediction(customer_id):
    # Try ML model first
    active_model = MLModel.objects.filter(
        name='churn_prediction',
        is_active=True
    ).first()
    
    if active_model:
        return predict_with_ml(customer_id, active_model)
    else:
        # Fall back to rule-based scoring
        return predict_with_rules(customer_id)

def predict_with_rules(customer_id):
    """Rule-based fallback when ML model unavailable"""
    customer = Customer.objects.get(id=customer_id)
    score = 0.0
    factors = []
    
    # Days since last session
    if customer.days_since_last_session > 30:
        score += 0.4
        factors.append({"factor": "No session in 30+ days", "impact": "+40%"})
    elif customer.days_since_last_session > 14:
        score += 0.2
        factors.append({"factor": "No session in 14+ days", "impact": "+20%"})
    
    # Late payments
    late_payments = customer.payments.filter(
        status='late',
        created_at__gte=timezone.now() - timedelta(days=90)
    ).count()
    if late_payments >= 2:
        score += 0.3
        factors.append({"factor": f"{late_payments} late payments (90d)", "impact": "+30%"})
    
    # Support tickets
    tickets = customer.support_tickets.filter(
        created_at__gte=timezone.now() - timedelta(days=90),
        category='billing'
    ).count()
    if tickets >= 3:
        score += 0.2
        factors.append({"factor": f"{tickets} billing disputes (90d)", "impact": "+20%"})
    
    return {
        "customer_id": customer_id,
        "churn_probability": min(score, 0.95),
        "confidence": "medium",
        "model_version": "rules_v1",
        "explanation": {"top_factors": factors}
    }
```
