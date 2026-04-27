# Phase 10: Admin Panel Completion

**Core Principle**: Close all Phase 9 loose ends, then build out every remaining backend-ready feature into the admin panel. Same pattern throughout — sidebar modal, compact table, bulk actions, optimistic updates, small parts.

**Pattern Rules**:
- Every page: pills stats row + search/filter bar + compact table + sidebar modal
- Every modal: collapsible sections matching Django admin fieldsets
- Every mutation: optimistic update + background re-fetch + rollback on failure
- Every new page: `useOptimistic` composable from day one
- Backend actions added/verified before frontend work begins

---

## 10.0 — Phase 9 Loose Ends

### 10.0.1 Analytics Page — Delete Entirely ✅
- [x] Delete `Analytics.vue`
- [x] Remove Analytics import from `App.vue`
- [x] Remove Analytics from `Sidebar.vue` nav sections
- [x] Remove `/analytics` route from `router/index.js`
- [x] Verify no broken references remain

### 10.0.2 Dashboard — Missing Sections
- [ ] Add Data Quality section (collapsible, default collapsed) — source: `suapi/dashboard-metrics/data-quality/`
- [ ] Add Network Analytics section (collapsible, default collapsed) — source: `suapi/dashboard-metrics/network-analytics/`
- [ ] Add A/B Testing section (collapsible, default collapsed) — source: `suapi/dashboard-metrics/ab-testing/`
- [ ] Add Dashboard quick-links dropdown in header (Pending Txns, Failed Txns, Expiring Vouchers, At-Risk Clients)
- [ ] Add Celery queue depths to System Health bar
- [ ] Add Redis memory usage to System Health bar

### 10.0.3 Clients Page — Missing Columns & Actions
- [x] `credit_limit` in modal form — present
- [x] Add `credit_limit` column to table
- [x] Add `reward_tier` column to table
- [x] Add `active_devices` column to table
- [x] Add `active_sessions` column to table
- [x] Add `2FA enabled` column to table
- [x] Add `reward_tier` filter to filter bar
- [x] Add `two_factor_enabled` filter to filter bar
- [ ] Add `home_location` filter to filter bar
- [x] Bulk action: Suspend selected — done
- [x] Bulk action: Activate selected — done
- [x] Bulk action: Reset failed logins — done
- [x] Add bulk action: Terminate all sessions for selected
- [x] Add bulk action: Upgrade to Premium tier
- [x] Add bulk action: Downgrade to Basic tier

---

## 10.1 — Notifications Center

### 10.1.1 Backend — Verify & Extend
- [ ] Verify `NotificationViewSet` exists at `suapi/notifications/` — if not, create it
- [ ] Verify `NotificationTemplateViewSet` exists at `suapi/notification-templates/` — if not, create it
- [ ] Add `stats` action to NotificationViewSet (total, unread, by type counts)
- [ ] Add `mark_read` action (detail)
- [ ] Add `mark_all_read` action (list)
- [ ] Add `bulk_action` action (mark_read, delete)
- [ ] Add `send` action to NotificationTemplateViewSet (send to user/group)
- [ ] Add serializers for both models with all fields

### 10.1.2 Notifications Page — Frontend
- [ ] Create `Notifications.vue`
- [ ] Stats pills: Total | Unread | SMS | Push | Email
- [ ] Search bar + filters: type | is_read | user | date range
- [ ] Compact table: recipient | type | title | message preview | sent_at | read | Actions
- [ ] Click row → sidebar modal (Core, Delivery, Metadata sections)
- [ ] Row actions: Mark read, Delete
- [ ] Bulk actions: Mark read, Delete
- [ ] Optimistic updates on all mutations
- [ ] Add to Sidebar nav under Communications section
- [ ] Add route to router

### 10.1.3 Notification Templates Page — Frontend
- [ ] Create `NotificationTemplates.vue`
- [ ] Stats pills: Total | Active | SMS | Push | Email
- [ ] Compact table: name | type | subject | active | created | Actions
- [ ] Sidebar modal sections: Core (name, type, subject), Content (body, variables), Settings (is_active)
- [ ] Send test notification action (detail modal action button)
- [ ] Bulk actions: Activate, Deactivate, Delete
- [ ] Optimistic updates
- [ ] Add to Sidebar nav under Communications section
- [ ] Add route to router

---

## 10.2 — Ads Management

### 10.2.1 Backend — Verify & Extend
- [ ] Verify `AdvertisementViewSet` exists at `suapi/ads/` — if not, create it
- [ ] Add `stats` action (total, active, impressions, clicks, CTR)
- [ ] Add `activate` / `deactivate` detail actions
- [ ] Add `bulk_action` (activate, deactivate, delete)
- [ ] Add `form_options` (locations, packages for targeting dropdowns)
- [ ] Verify `AdMedia` is handled (upload endpoint)
- [ ] Add serializer with all Advertisement + AdMedia fields

### 10.2.2 Ads Management Page — Frontend
- [x] Stats cards exist (total, impressions, clicks, CTR, budget)
- [x] Table with edit/delete row actions exists
- [x] Create/Edit modal exists (flat form)
- [ ] Migrate stats cards → compact pills row
- [ ] Replace flat modal → sidebar collapsible modal
- [ ] Add bulk actions (activate, deactivate, delete)
- [ ] Add checkbox column + select-all
- [ ] Add search bar
- [ ] Add status/type filter
- [ ] Add optimistic updates
- [ ] Add to Sidebar nav if missing

---

## 10.3 — Finance Page Completion

### 10.3.1 Audit Current Finance.vue
- [x] Analytics tab — exists
- [x] KPI tab — exists
- [x] P&L tab — exists
- [x] Budget tab — exists
- [x] Invoices tab — exists
- [x] Revenue Streams tab — exists
- [x] Recurring Billing tab — exists
- [x] AR Collection tab — exists
- [x] Revenue at Risk tab — exists
- [x] Payment Reminders tab — exists
- [x] Payment Allocation tab — exists
- [x] CLV Cohorts tab — exists
- [x] Expenses tab — exists
- [x] Payroll tab — exists
- [x] Accounts Payable tab — exists
- [x] Asset Register tab — exists
- [x] Petty Cash tab — exists
- [x] Purchase Orders tab — exists
- [x] Loan Repayment tab — exists
- [ ] Audit each tab component for completeness vs stub

### 10.3.2 Payment Gateways Tab
- [ ] Table: name | provider | is_active | environment | success_rate | last_used | Actions
- [ ] Sidebar modal: Core (name, provider), Credentials (api_key, secret — blurred), Settings (is_active, environment, limits)
- [ ] Enable/Disable toggle action
- [ ] Test connection action

### 10.3.3 Budget Tab
- [ ] Departments list with BudgetCategories
- [ ] Expenses table: category | amount | date | description | approved | Actions
- [ ] Approve/reject expense actions
- [ ] Budget vs actual progress bars per category
- [ ] Bulk approve expenses

### 10.3.4 Investments Tab
- [ ] Table: name | type | amount | current_value | ROI | status | Actions
- [ ] Sidebar modal: Core, Financial Details, Performance sections
- [ ] Stats pills: Total Invested | Current Value | Total ROI | Active

### 10.3.5 Revenue Streams Tab
- [ ] Table: name | type | amount | period | growth | active | Actions
- [ ] Sidebar modal with all RevenueStream fields
- [ ] Revenue breakdown chart (donut by stream type)

### 10.3.6 Board Report Tab
- [ ] Read-only generated report view
- [ ] Export to PDF action
- [ ] Key metrics summary cards
- [ ] Period selector (monthly, quarterly, annual)

---

## 10.4 — Customer Intelligence Page

### 10.4.1 Audit Current CustomerIntelligence.vue
- [x] Churn Prediction tab — exists (ChurnDashboard component)
- [x] Retention tab — exists (RetentionDashboard component)
- [x] Revenue at Risk tab — exists (RevenueAtRisk component)
- [ ] RFM Segmentation tab — missing
- [ ] Cohort Analysis tab — missing
- [ ] LTV Distribution tab — missing

### 10.4.2 RFM Segmentation Section
- [ ] Table: client | recency_score | frequency_score | monetary_score | segment | Actions
- [ ] Segment badges: Champions, Loyal, At Risk, Lost, New
- [ ] Filter by segment
- [ ] Export CSV
- [ ] Source: `suapi/dashboard-metrics/rfm-segmentation/`

### 10.4.3 Cohort Analysis Section
- [ ] Cohort retention heatmap table (month × cohort)
- [ ] Period selector
- [ ] Source: `suapi/dashboard-metrics/cohort-analysis/`

### 10.4.4 Churn Prediction Section
- [ ] Table: client | churn_score | risk_level | last_seen | voucher_status | Actions
- [ ] Risk badges: High (>0.7) / Medium (0.3-0.7) / Low (<0.3)
- [ ] Quick actions: Send retention offer, Suspend, View profile
- [ ] Source: `suapi/dashboard-metrics/churn-prediction/`

### 10.4.5 LTV Distribution Section
- [ ] Histogram chart of client LTV distribution
- [ ] Top 10 clients by LTV table
- [ ] Average LTV by tier breakdown

---

## 10.5 — Refunds Page Completion

### 10.5.1 Backend — Verify & Extend
- [x] `RefundViewSet` exists at `suapi/refunds/`
- [x] `stats` action exists
- [x] `eligible_clients` action exists
- [x] `process_individual` action exists
- [x] `batch_refund` action exists
- [x] `history` action exists
- [ ] Add `approve` / `reject` detail actions (individual refund approve/reject)
- [ ] Add `bulk_action` (approve, reject)

### 10.5.2 Refunds Page — Frontend
- [ ] Audit existing `Refunds.vue` (324 lines — check what's complete)
- [ ] Stats pills: Total | Pending | Approved | Rejected | Total Amount (blurred)
- [ ] Search + filters: status | payment_method | date range | amount range
- [ ] Compact table: ref | client | amount | reason | status | requested_at | processed_at | Actions
- [ ] Sidebar modal sections: Core, Transaction, Processing, Timeline
- [ ] Row actions: Approve, Reject, View transaction
- [ ] Bulk actions: Approve selected, Reject selected
- [ ] Optimistic status updates

---

## 10.6 — System Settings Page (New)

### 10.6.1 Backend
- [ ] Create `SystemSettingsViewSet` at `suapi/settings/`
- [ ] Endpoint: GET/PATCH platform settings (maintenance_mode, registration_open, etc.)
- [ ] Endpoint: GET/PATCH RADIUS server config
- [ ] Endpoint: GET/PATCH email provider config
- [ ] Endpoint: GET/PATCH SMS provider config
- [ ] Endpoint: test connection for each provider

### 10.6.2 System Settings Page — Frontend
- [ ] Create `SystemSettings.vue`
- [ ] Section: Platform (maintenance_mode toggle, registration_open toggle, platform name, logo)
- [ ] Section: Payment Gateways (link to Finance → Gateways tab)
- [ ] Section: RADIUS Server (host, port, secret — blurred, timeout, test connection button)
- [ ] Section: Email Provider (provider, host, port, username, password — blurred, from_email, test send button)
- [ ] Section: SMS Provider (provider, api_key — blurred, sender_id, test send button)
- [ ] Section: Security (session timeout, max login attempts, 2FA enforcement toggle)
- [ ] All sections collapsible
- [ ] Save per-section (not one global save)
- [ ] Add to Sidebar nav (bottom, settings icon)
- [ ] Add route to router

---

## 10.7 — Audit Log Page (New)

### 10.7.1 Backend
- [ ] Verify `AuditLogView` exists at `suapi/dashboard-metrics/audit-logs/`
- [ ] Add pagination, search, filters to audit log endpoint
- [ ] Fields: user | action | model | object_id | changes (JSON diff) | ip_address | timestamp

### 10.7.2 Audit Log Page — Frontend
- [ ] Create `AuditLog.vue`
- [ ] Stats pills: Total Actions | Today | By User count | Critical Actions
- [ ] Search + filters: user | action_type | model | date range
- [ ] Compact table: timestamp | user | action | model | object | ip | Details
- [ ] Click row → expand inline JSON diff viewer (no modal needed)
- [ ] Export CSV
- [ ] No create/edit/delete — read-only page
- [ ] Add to Sidebar nav under Security section

---

## Execution Order

```
10.0.1  →  Delete Analytics page (quick cleanup)
10.0.2  →  Dashboard missing sections
10.0.3  →  Clients missing columns & bulk actions
10.1    →  Notifications Center (backend ready)
10.2    →  Ads Management (backend ready, stub exists)
10.5    →  Refunds completion (quick win, mostly frontend)
10.3    →  Finance page completion (largest scope)
10.4    →  Customer Intelligence completion
10.6    →  System Settings (new backend + frontend)
10.7    →  Audit Log (new frontend, backend mostly ready)
```

---

## Progress Tracking

| Section | Backend | Frontend | Status |
|---------|---------|----------|--------|
| 10.0.1 Analytics Delete | N/A | ✅ | Complete |
| 10.0.2 Dashboard Sections | ✅ | ⬜ | Not Started |
| 10.0.3 Clients Columns | ✅ | 🔄 | Partial (home_location filter remaining) |
| 10.1.1 Notifications Backend | ⬜ | N/A | Not Started |
| 10.1.2 Notifications Page | ⬜ | ⬜ | Not Started |
| 10.1.3 Notification Templates | ⬜ | ⬜ | Not Started |
| 10.2.1 Ads Backend | ⬜ | N/A | Not Started |
| 10.2.2 Ads Page | ⬜ | 🔄 | Partial (stats+table+modal exist, needs overhaul) |
| 10.3.1 Finance Audit | N/A | 🔄 | Partial (all tabs exist, need depth audit) |
| 10.3.2 Payment Gateways Tab | ✅ | ⬜ | Not Started |
| 10.3.3 Budget Tab | ✅ | ✅ | Exists |
| 10.3.4 Investments Tab | ✅ | ⬜ | Not Started |
| 10.3.5 Revenue Streams Tab | ✅ | ✅ | Exists |
| 10.3.6 Board Report Tab | ✅ | ⬜ | Not Started |
| 10.4.1 Intelligence Audit | N/A | 🔄 | Partial (churn+retention+RAR exist, RFM/cohort/LTV missing) |
| 10.4.2 RFM Segmentation | ✅ | ⬜ | Not Started |
| 10.4.3 Cohort Analysis | ✅ | ⬜ | Not Started |
| 10.4.4 Churn Prediction | ✅ | ✅ | Exists |
| 10.4.5 LTV Distribution | ✅ | ⬜ | Not Started |
| 10.5.1 Refunds Backend | 🔄 | N/A | Partial (needs approve/reject/bulk) |
| 10.5.2 Refunds Page | 🔄 | 🔄 | Partial (324 lines — needs audit) |
| 10.6.1 Settings Backend | ⬜ | N/A | Not Started |
| 10.6.2 Settings Page | ⬜ | ⬜ | Not Started |
| 10.7.1 Audit Log Backend | ✅ | N/A | Exists (AuditLogView) |
| 10.7.2 Audit Log Page | ✅ | ⬜ | Not Started |
