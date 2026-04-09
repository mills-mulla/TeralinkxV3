# Smart Business Management System - Implementation Checklist

**Project**: TeralinkX Smart Business Management Platform  
**Timeline**: 90 Days (12 Weeks)  
**Last Updated**: 2025-01-XX

---

## Phase 0: Foundation Hardening (Week 1-2)

### 0.1 Data Quality Audit ✅ COMPLETED
- [x] Run data completeness audit on PaymentTransaction table
- [x] Run data completeness audit on Customer (ClientH) table
- [x] Run data completeness audit on Expense table
- [x] Check for duplicate transactions in PaymentTransaction
- [x] Check for orphaned customer accounts
- [x] Audit expense categorization consistency
- [x] Check exchange rate update frequency
- [x] Create data quality dashboard view
- [x] Fix any data completeness issues below 90%
- [x] Document data quality baseline metrics

**Deliverable**: ✅ Data quality report showing >90% completeness per entity (93% achieved)
**Completion Date**: 2025-01-XX
**Files Created**: 
- `/apps/finance/management/commands/audit_data_quality.py`
- `/docs/PHASE_0_1_COMPLETION.md`

---

### 0.2 TimescaleDB Migration (Week 1-5) ⏳ IN PROGRESS

#### Week 1: Setup & Dual-Write ✅ COMPLETED
- [x] Install TimescaleDB extension on PostgreSQL
- [x] Create FeatureFlag model in Django
- [x] Update docker-compose.yml to use TimescaleDB image
- [x] Add TimescaleDB database configuration to settings.py
- [x] Create TimescaleDB router for gradual migration
- [x] Create monitoring command for performance comparison
- [x] Create feature flag initialization command
- [x] Restart database container with TimescaleDB image
- [x] Run setup_timescaledb command to create hypertables
- [x] Initialize feature flag with 0% rollout
- [x] Validate data migration with checksums

**Progress Notes**:
- ✅ FeatureFlag model created in `/apps/core/models.py`
- ✅ Migration applied: `core.0002_featureflag`
- ✅ TimescaleDB setup command: `/apps/finance/management/commands/setup_timescaledb.py`
- ✅ TimescaleDB router: `/apps/finance/timescale_router.py`
- ✅ Performance monitor: `/apps/finance/management/commands/monitor_timescale.py`
- ✅ Feature flag init: `/apps/finance/management/commands/init_timescale_flag.py`
- ✅ Updated docker-compose.yml to use `timescale/timescaledb:latest-pg15`
- ✅ Added TimescaleDB database config and router to settings.py
- ✅ Hypertables created with automatic data migration (50 PaymentTransaction, 50 TransactionQueue)
- ✅ Feature flag initialized at 0% rollout
- ✅ Performance baseline: 5-25% improvement over PostgreSQL
- ✅ Data validation: 100% integrity confirmed

**Files Created**:
- `/apps/core/models.py` (FeatureFlag model)
- `/apps/core/migrations/0002_featureflag.py`
- `/apps/finance/management/commands/setup_timescaledb.py`
- `/apps/finance/management/commands/monitor_timescale.py`
- `/apps/finance/management/commands/init_timescale_flag.py`
- `/apps/finance/management/commands/validate_timescale.py`
- `/apps/finance/timescale_router.py`
- `/docker-compose.yml` (updated to TimescaleDB image)
- `/teralinkx/settings.py` (added TimescaleDB config)

**Completion Date**: 2025-01-XX
**Week 1 Status**: ✅ COMPLETE (11/11 tasks)

#### Week 2: Backfill & Validation ✅ COMPLETED
- [x] Backfill historical PaymentTransaction data (auto-migrated with hypertable creation)
- [x] Backfill historical TransactionQueue data (auto-migrated with hypertable creation)
- [x] Validate row counts match between old and new tables
- [x] Validate data integrity (checksums, sample queries)
- [x] Document data validation results
- [x] Confirm hypertable chunk configuration

**Validation Results**:
- PaymentTransaction: 50 rows, 100% match, checksum verified
- TransactionQueue: 50 rows, 100% match, checksum verified
- Hypertables: 7-day chunks, compression ready
- Performance: 5-25% improvement confirmed

**Week 2 Status**: ✅ COMPLETE (6/6 tasks)
**Note**: Backfill completed automatically during hypertable creation with `migrate_data => TRUE`

#### Week 3: 10% Rollout
- [ ] Enable dual-read for 10% of payment queries
- [ ] Monitor query performance (response times)
- [ ] Compare results between old and new queries
- [ ] Log any discrepancies found
- [ ] Fix any issues discovered

#### Week 4: 50% Rollout
- [ ] Ramp feature flag to 50% of queries
- [ ] Monitor error rates and performance
- [ ] Compare aggregate metrics (MRR, revenue totals)
- [ ] Tune TimescaleDB configuration if needed
- [ ] Document performance improvements

#### Week 5: Full Cutover
- [ ] Enable TimescaleDB for 100% of queries
- [ ] Monitor for 48 hours with rollback plan ready
- [ ] Mark old tables as deprecated (keep for 2 weeks)
- [ ] Update all query functions to use TimescaleDB
- [ ] Remove dual-write logic after 2-week stability period
- [ ] Drop old tables after 2-week rollback window

**Deliverable**: TimescaleDB fully operational with 2x-5x query performance improvement

---

### 0.3 Event Bus Setup ✅ COMPLETED
- [x] Install Django Signals framework (built-in)
- [x] Create `payment.completed` signal
- [x] Create `expense.created` signal
- [x] Create `hids.anomaly` signal
- [x] Create `invoice.uploaded` signal
- [x] Create `budget.threshold_exceeded` signal
- [x] Create event handler for churn model refresh
- [x] Create event handler for budget utilization recalc
- [x] Create event handler for fraud correlation check
- [x] Create event handler for retention SMS trigger
- [x] Create Celery tasks for async event processing
- [x] Test signal firing and handler execution
- [x] Add logging for all event triggers
- [x] Register signal handlers in AppConfig

**Deliverable**: ✅ Event-driven architecture with real-time triggers
**Completion Date**: 2025-01-XX
**Files Created**:
- `/apps/finance/signals.py` (15 event signals)
- `/apps/finance/handlers.py` (5 signal handlers)
- `/apps/finance/tasks.py` (8 Celery tasks)
- `/apps/finance/apps.py` (AppConfig with handler registration)
- `/apps/finance/management/commands/test_event_bus.py`

---

### 0.4 Model Registry ✅ COMPLETED
- [x] Create MLModel Django model
- [x] Add migrations for MLModel table
- [x] Create model registration helper function
- [x] Create model activation/deactivation logic
- [x] Create model version management system
- [x] Add feature_importance JSON field handling
- [x] Create fallback_strategy logic
- [x] Test model registry with sample data

**Deliverable**: ✅ ML model registry with version control and graceful degradation
**Completion Date**: 2025-01-XX
**Files Created**:
- `/apps/finance/models.py` (MLModel added)
- `/apps/finance/migrations/0012_mlmodel.py`

---

## Phase 1: Customer Intelligence (Week 3-5)

### 1.1 Churn Prediction - Rule-Based (Week 3)

#### Data Preparation
- [ ] Create churn feature extraction function
- [ ] Extract days_since_last_session for all customers
- [ ] Extract support ticket counts (90 days)
- [ ] Extract payment history (late payments)
- [ ] Extract session duration trends
- [ ] Extract package downgrade history
- [ ] Create customer feature dataset

#### Rule-Based Model
- [ ] Create ChurnPrediction model in Django
- [ ] Implement rule-based scoring algorithm
- [ ] Add scoring for days_since_last_session
- [ ] Add scoring for support tickets
- [ ] Add scoring for late payments
- [ ] Add scoring for package downgrades
- [ ] Create explanation generator (top factors)
- [ ] Test rule-based model on sample customers
- [ ] Validate scores make business sense

#### API & Dashboard
- [ ] Create `/api/finance/churn-predictions/` endpoint
- [ ] Add filtering by risk_level (high/medium/low)
- [ ] Add pagination support
- [ ] Create churn dashboard view (backend)
- [ ] Test API with Postman/curl
- [ ] Document API endpoint

**Deliverable**: Rule-based churn prediction with actionable alerts

---

### 1.2 Churn Prediction - ML Model (Week 4)

#### ML Infrastructure
- [ ] Install xgboost library
- [ ] Install scikit-learn for train/test split
- [ ] Create model training script
- [ ] Create feature engineering pipeline
- [ ] Implement stratified train/test split (80/20)
- [ ] Add class imbalance handling (scale_pos_weight)

#### Model Training
- [ ] Collect historical churn data (last 90 days)
- [ ] Label churned customers (no sessions 60+ days)
- [ ] Train XGBoost model
- [ ] Validate model (AUC > 0.75 threshold)
- [ ] Calculate feature importance
- [ ] Register model in MLModel registry
- [ ] Save model to /models/ directory

#### Model Deployment
- [ ] Create model loading function
- [ ] Implement predict_with_ml() function
- [ ] Add graceful degradation to rule-based
- [ ] Update API to use ML model when available
- [ ] Create Celery task for weekly retraining
- [ ] Test model predictions on live data
- [ ] Monitor model accuracy over time

**Deliverable**: Production ML churn model with AUC > 0.75

---

### 1.3 Retention Workflow (Week 4-5)

#### Automated Retention System
- [ ] Create RetentionTask model
- [ ] Add priority_score calculation
- [ ] Implement automated discount logic (high-value customers)
- [ ] Implement automated SMS sending (medium-value)
- [ ] Implement re-engagement SMS (low-value)
- [ ] Create outcome tracking system
- [ ] Add "relocated" detection logic
- [ ] Create Celery task for retention task creation
- [ ] Create Celery task for outcome monitoring

#### Retention Dashboard
- [ ] Create retention task list view
- [ ] Add priority sorting
- [ ] Add revenue_at_risk display
- [ ] Add automated action history
- [ ] Create outcome statistics view
- [ ] Add filters (status, value tier)
- [ ] Test retention workflow end-to-end

**Deliverable**: Automated retention system with SMS integration

---

### 1.4 Revenue at Risk Dashboard (Week 5)
- [ ] Create revenue_at_risk calculation function
- [ ] Calculate total MRR at risk
- [ ] Calculate week-over-week trend
- [ ] Create top 10 at-risk accounts view
- [ ] Add relocated customer filtering
- [ ] Create automated offers sent counter
- [ ] Create outcome breakdown (retained/churned/relocated)
- [ ] Build dashboard API endpoint
- [ ] Test with real customer data
- [ ] Document dashboard metrics

**Deliverable**: Executive dashboard showing revenue at risk

---

## Phase 2: Financial Intelligence (Week 5-8)

### 2.1 Document Processing (Week 10-12 - Deprioritized)

#### Structured Data Ingestion
- [ ] Create bank statement CSV upload endpoint
- [ ] Parse CSV and extract transactions
- [ ] Create vendor invoice email forwarding
- [ ] Parse PDF text (pypdf2 library)
- [ ] Extract amount/date/vendor from PDF
- [ ] Create expense template system
- [ ] Add image/PDF attachment storage
- [ ] Test with sample bank statements
- [ ] Test with sample vendor invoices

#### Manual Entry Templates
- [ ] Create expense form templates for common vendors
- [ ] Add fuel expense template
- [ ] Add utilities expense template
- [ ] Add maintenance expense template
- [ ] Add budget validation on form submission
- [ ] Test manual entry workflow

**Deliverable**: Digital document processing (no OCR)

---

### 2.2 Cash Flow Forecasting (Week 6)

#### Prophet Setup
- [ ] Install fbprophet library
- [ ] Create CashFlowForecast model
- [ ] Extract historical revenue data (12 months)
- [ ] Extract historical expense data (12 months)
- [ ] Prepare time-series data for Prophet

#### Forecast Generation
- [ ] Train Prophet model on historical data
- [ ] Generate optimistic forecast (P10)
- [ ] Generate base forecast (P50)
- [ ] Generate conservative forecast (P90)
- [ ] Add seasonality adjustments (month-end spikes)
- [ ] Create forecast visualization data

#### Alerts & API
- [ ] Create alert for cash position < KES 500K
- [ ] Create alert for unusual expense forecast
- [ ] Create alert for MRR growth slowdown
- [ ] Create `/api/finance/cash-flow-forecast/` endpoint
- [ ] Add horizon parameter (30/90/180 days)
- [ ] Add scenario parameter (optimistic/base/conservative)
- [ ] Test forecasts against actual data
- [ ] Create Celery task for daily forecast generation

**Deliverable**: Multi-scenario cash flow forecasting with alerts

---

### 2.3 Automated Reconciliation (Week 7)

#### Reconciliation Engine
- [ ] Create ReconciliationMatch model
- [ ] Implement confidence scoring algorithm
- [ ] Add amount matching logic (exact/±2%/±5%)
- [ ] Add customer matching logic (ID/name fuzzy)
- [ ] Add date proximity matching (±3/±7 days)
- [ ] Add phone number matching (MPESA)
- [ ] Create match action logic (auto/review/manual)

#### Review Queue
- [ ] Create unmatched items queue
- [ ] Sort by payment amount (largest first)
- [ ] Sort by days since payment (oldest first)
- [ ] Sort by confidence score (highest first)
- [ ] Create manual review interface
- [ ] Add match confirmation workflow
- [ ] Test with sample bank statements

#### API & Reporting
- [ ] Create `/api/finance/reconcile/` endpoint
- [ ] Create `/api/finance/reconcile/{job_id}/results/` endpoint
- [ ] Generate reconciliation report
- [ ] Show matched % and unmatched items
- [ ] Show average confidence score
- [ ] Create Celery task for async reconciliation
- [ ] Test end-to-end reconciliation workflow

**Deliverable**: Automated reconciliation with 85%+ auto-match rate

---

### 2.4 Budget Intelligence (Week 8)

#### Dynamic Budget Tracking
- [ ] Create budget utilization rate calculation
- [ ] Add days remaining in period tracking
- [ ] Create variance analysis function
- [ ] Calculate rolling 3-month spend trends
- [ ] Add department-level budget tracking
- [ ] Create budget alert thresholds

#### Budget Dashboard
- [ ] Create budget utilization dashboard
- [ ] Add variance analysis view
- [ ] Add spend trend charts
- [ ] Add department comparison view
- [ ] Create budget alert notifications
- [ ] Test with real expense data

**Deliverable**: Dynamic budget intelligence with variance analysis

---

## Phase 3: HIDS Financial Integration (Week 7-9)

### 3.1 Fraud Correlation Framework (Week 8)

#### HIDS Data Integration
- [ ] Create NetworkAnomaly model (if not exists)
- [ ] Create HIDS event consumer
- [ ] Parse HIDS anomaly data
- [ ] Store anomalies in database
- [ ] Create anomaly-transaction correlation table

#### Fraud Detection Rules
- [ ] Implement port-scan + payment correlation
- [ ] Implement geolocation mismatch detection
- [ ] Implement multiple accounts same IP detection
- [ ] Implement suspicious DNS + payment correlation
- [ ] Create fraud alert system
- [ ] Add configurable threshold management
- [ ] Create fraud dashboard

#### Testing & Tuning
- [ ] Test with historical HIDS data
- [ ] Measure false positive rate
- [ ] Tune correlation thresholds
- [ ] Document fraud detection rules
- [ ] Create fraud alert notifications

**Deliverable**: Real-time fraud detection with <5% false positive rate

---

### 3.2 Network Health → Revenue Impact (Week 9)

#### Network Event Mapping
- [ ] Create NetworkEvent model
- [ ] Map outages to affected customers
- [ ] Calculate revenue at risk per outage
- [ ] Map packet loss to support tickets
- [ ] Map node failures to customer segments
- [ ] Calculate ARPU per affected segment

#### Revenue Impact Dashboard
- [ ] Create network event impact view
- [ ] Show affected customer count
- [ ] Show combined MRR at risk
- [ ] Show estimated credit claims
- [ ] Add historical impact trends
- [ ] Create impact alert notifications

**Deliverable**: Network events with financial context

---

### 3.3 Proactive Credit Management (Week 9)

#### SLA Credit Automation
- [ ] Define SLA credit calculation rules
- [ ] Create ServiceCredit model
- [ ] Detect service degradation from HIDS
- [ ] Identify affected customers automatically
- [ ] Calculate credit amounts per SLA
- [ ] Generate draft credit notes
- [ ] Create approval workflow
- [ ] Send proactive customer notifications
- [ ] Test with simulated outage

**Deliverable**: Automated SLA credit management

---

## Phase 4: Executive Intelligence (Week 9-12)

### 4.1 KPI Command Centre (Week 10)

#### KPI Snapshot System
- [ ] Create KPISnapshot model
- [ ] Implement MRR calculation function
- [ ] Implement active customers count
- [ ] Implement churn rate calculation (30 days)
- [ ] Implement cash position calculation
- [ ] Implement receivables aging calculation
- [ ] Implement network uptime calculation (7 days)
- [ ] Add computation time tracking

#### Caching & API
- [ ] Create Celery task for KPI refresh (every 5 min)
- [ ] Implement snapshot cleanup (keep 24h)
- [ ] Create `/api/finance/kpi-summary/` endpoint
- [ ] Add async refresh trigger (if stale)
- [ ] Add data age metadata
- [ ] Test cache hit rate (target >99%)
- [ ] Monitor endpoint response time (<100ms)

#### Weekly Summary
- [ ] Create weekly summary generator
- [ ] Auto-generate top 3 wins
- [ ] Auto-generate top 3 risks
- [ ] Add budget status summary
- [ ] Add churn risk summary
- [ ] Schedule Monday 7am generation
- [ ] Test summary generation

**Deliverable**: Executive KPI dashboard with <100ms load time

---

### 4.2 Automated Board Reporting (Week 11)

#### Report Generation
- [ ] Create BoardReport model
- [ ] Generate financial performance section
- [ ] Generate customer metrics section
- [ ] Generate operational metrics section
- [ ] Generate risk register section
- [ ] Generate cash flow forecast section
- [ ] Add month-over-month comparisons

#### Export & Distribution
- [ ] Create PDF export function
- [ ] Create PowerPoint export function
- [ ] Add narrative section templates
- [ ] Create report review workflow
- [ ] Schedule monthly generation (1st of month)
- [ ] Test report generation
- [ ] Add email distribution

**Deliverable**: Automated monthly board pack

---

### 4.3 Pricing Intelligence (Week 11)

#### Price Elasticity Analysis
- [ ] Extract package pricing history
- [ ] Extract churn rates per package
- [ ] Calculate price elasticity per package
- [ ] Identify optimal price points
- [ ] Create package performance comparison

#### Pricing Dashboard
- [ ] Create revenue per GB calculation
- [ ] Create ARPU per package tier
- [ ] Track upgrade/downgrade rates
- [ ] Add competitive positioning view
- [ ] Generate pricing recommendations
- [ ] Test with historical data

**Deliverable**: Data-driven pricing recommendations

---

### 4.4 Supplier & Vendor Intelligence (Week 12)

#### Vendor Tracking
- [ ] Create Vendor model (if not exists)
- [ ] Track bandwidth costs per provider
- [ ] Track cost per GB trends
- [ ] Flag invoice discrepancies
- [ ] Create contract expiry calendar
- [ ] Add renewal recommendations

#### Vendor Dashboard
- [ ] Create vendor performance view
- [ ] Show cost trends per vendor
- [ ] Show invoice discrepancy alerts
- [ ] Show upcoming contract renewals
- [ ] Add vendor comparison view
- [ ] Test with real vendor data

**Deliverable**: Vendor intelligence dashboard

---

## Infrastructure & DevOps

### Celery Configuration
- [ ] Configure Celery Beat scheduler
- [ ] Set up celery-default queue (4 workers)
- [ ] Set up celery-ml queue (2 workers)
- [ ] Set up celery-ocr queue (3 workers)
- [ ] Set up celery-hids queue (2 workers)
- [ ] Configure task routing
- [ ] Set up Flower monitoring (port 5555)
- [ ] Test all scheduled tasks
- [ ] Document Celery architecture

### Redis Configuration
- [ ] Configure Redis DB 0 (Celery broker)
- [ ] Configure Redis DB 1 (Django cache)
- [ ] Configure Redis DB 2 (Session storage)
- [ ] Configure Redis DB 3 (HIDS streams)
- [ ] Set maxmemory policy (allkeys-lru)
- [ ] Set maxmemory limit (2GB)
- [ ] Test Redis connectivity
- [ ] Monitor Redis memory usage

### Monitoring & Health Checks
- [ ] Create `/api/health/` endpoint
- [ ] Add database connectivity check
- [ ] Add Redis connectivity check
- [ ] Add Celery queue depth check
- [ ] Create cache health check command
- [ ] Set up Prometheus metrics export
- [ ] Configure Grafana dashboards
- [ ] Set up alert notifications

### Frontend Integration
- [ ] Install apexcharts
- [ ] Install vue-query
- [ ] Install pinia
- [ ] Install socket.io-client
- [ ] Create KPI dashboard component
- [ ] Create churn prediction component
- [ ] Create revenue at risk component
- [ ] Create budget intelligence component
- [ ] Test real-time updates via WebSocket

---

## Testing & Validation

### Unit Tests
- [ ] Write tests for churn prediction
- [ ] Write tests for reconciliation matching
- [ ] Write tests for cash flow forecasting
- [ ] Write tests for fraud correlation
- [ ] Write tests for KPI calculations
- [ ] Achieve >80% code coverage

### Integration Tests
- [ ] Test payment → churn score update flow
- [ ] Test expense → budget recalc flow
- [ ] Test HIDS anomaly → fraud check flow
- [ ] Test end-to-end retention workflow
- [ ] Test end-to-end reconciliation workflow

### Performance Tests
- [ ] Load test KPI endpoint (target <100ms)
- [ ] Load test churn prediction endpoint (target <300ms)
- [ ] Load test cash flow forecast (target <500ms)
- [ ] Test TimescaleDB query performance
- [ ] Test cache hit rates

### User Acceptance Testing
- [ ] UAT: Churn prediction dashboard
- [ ] UAT: Retention workflow
- [ ] UAT: Budget intelligence
- [ ] UAT: KPI command centre
- [ ] UAT: Board reporting
- [ ] Collect user feedback
- [ ] Fix critical issues

---

## Documentation

### Technical Documentation
- [ ] Document API endpoints (OpenAPI/Swagger)
- [ ] Document database schema
- [ ] Document Celery tasks
- [ ] Document event bus architecture
- [ ] Document ML model training process
- [ ] Document deployment process

### User Documentation
- [ ] Create user guide for churn dashboard
- [ ] Create user guide for retention workflow
- [ ] Create user guide for budget intelligence
- [ ] Create user guide for KPI dashboard
- [ ] Create admin guide for model management
- [ ] Create troubleshooting guide

### Operational Documentation
- [ ] Document monitoring procedures
- [ ] Document backup procedures
- [ ] Document disaster recovery plan
- [ ] Document scaling guidelines
- [ ] Document security procedures

---

## Success Metrics Tracking

### Baseline Measurements (Week 1)
- [ ] Measure current monthly churn rate
- [ ] Measure current expense entry time
- [ ] Measure current reconciliation time
- [ ] Measure current report generation time
- [ ] Document baseline metrics

### 90-Day Target Validation (Week 12)
- [ ] Measure final monthly churn rate (target: -20%)
- [ ] Measure final expense entry time (target: -50%)
- [ ] Measure cash forecast accuracy (target: ±15%)
- [ ] Measure fraud false positive rate (target: <5%)
- [ ] Measure reconciliation time (target: -40%)
- [ ] Measure report generation time (target: -70%)
- [ ] Document final metrics
- [ ] Calculate ROI

---

## Project Milestones

- [ ] **Week 2**: Foundation complete (TimescaleDB, Event Bus, Model Registry)
- [ ] **Week 5**: Customer Intelligence live (Churn prediction + Retention)
- [ ] **Week 8**: Financial Intelligence live (Forecasting + Reconciliation)
- [ ] **Week 9**: HIDS Integration live (Fraud detection + Network impact)
- [ ] **Week 12**: Executive Intelligence live (KPI Centre + Board reports)
- [ ] **Week 12**: Project complete - Go live celebration! 🎉

---

**Progress Tracking**: Update this checklist weekly during sprint planning.  
**Blockers**: Document any blockers in project management tool.  
**Sign-off**: Each phase requires stakeholder approval before proceeding.
