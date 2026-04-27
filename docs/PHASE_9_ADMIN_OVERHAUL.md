# Phase 9: Admin Panel UI Overhaul

**Core Principle**: The frontend is a modern Vue interpreter of Django admin.
Every page = admin list_display (compact table) + fieldsets (modal) + actions (bulk/row) + filters.
Charts and insights are additions on top, not replacements.
Finance handles all financial data. Dashboard is the operational pulse. Analytics page is deleted.

**UI Rules**:
- Everything collapsible — every section can be collapsed/expanded
- Compact look — dense tables, small text, minimal padding
- Click row to spawn modal — no inline editing
- Dropdowns for quick links, not separate rows of buttons

---

## 9.1 Dashboard Overhaul

### Remove
- [x] Revenue metric card (the KSh number card in top 4) — Finance KPI owns this
- [x] Payment Methods pie chart — Finance Transactions owns this
- [x] Refund Metrics card — Finance Refunds owns this

### Keep
- [x] Revenue Analytics chart (area chart showing trend over time) — operational, stays

### New Layout Order (all sections collapsible)

**1. System Health** — FIRST, always visible, never collapsible
- [x] DB status | Redis status | Celery status | Disk usage | Internet connectivity
- [x] Color coded: green/amber/red dots
- [x] Auto-refreshes every 30s
- [ ] Add Celery queue depths (default, ml, notifications, cleanup queues)
- [ ] Add Redis memory usage

**2. Real-Time Monitor** — collapsible, default open
- [x] Live transactions, active sessions, current activity

**3. KPI Banner** — collapsible, default open, compact single row
- [x] Not metric cards — a slim horizontal banner with inline values
- [x] Format: MRR: KSh X | Churn: X% | Cash: KSh X | Pending Txns: X | Failed (24h): X
- [x] Each value is a link to the relevant page
- [x] Source: GET /api/finance/api/kpi/summary/ + suapi/transaction-queue/

**4. Operational Metric Cards** — collapsible, default open
- [x] Total Clients | New (7d) | Active Vouchers | Active Sessions
- [x] Revenue card replaced with Active Sessions

**5. Charts** — collapsible, default open

- [x] Revenue Analytics chart (kept)
- [x] Client Growth chart
- [x] Package Sales pie
- [x] Conversion Funnel

**6. Top Locations + Recent Activity** — collapsible, default open
- [x] Implemented

**7. Device Breakdown + Reward Tiers** — collapsible, default collapsed
- [x] Implemented

**8. Data Quality** — collapsible, default collapsed (moved from Analytics)
- [ ] Not moved yet

**9. Network Analytics** — collapsible, default collapsed (moved from Analytics)
- [ ] Not moved yet

**10. A/B Testing** — collapsible, default collapsed (moved from Analytics)
- [ ] Not moved yet

**11. Dashboard Builder** — accessible via button in page header, not a section
- [ ] Not implemented

### Quick Links
- [ ] Dropdown menu in header (not a row of buttons)
- [ ] Items: Pending Transactions, Failed Transactions, Expiring Vouchers, At-Risk Customers

**Status**: 🔄 In Progress | **Priority**: Critical

---

## 9.2 Analytics Page — DELETE ENTIRELY

All tabs relocated:
- [ ] Financial → Finance
- [ ] Customers RFM → Finance CLV Cohorts
- [ ] Retention → Finance Intelligence
- [ ] Predictive → Finance Intelligence + KPI
- [ ] Audit → Finance Audit Trail
- [ ] System Health → Dashboard section 1
- [ ] Data Quality → Dashboard section 8
- [ ] Network → Dashboard section 99.4
- [ ] A/B Testing → Dashboard section 10
- [ ] Dashboard Builder → Dashboard header button

### Tasks
- [ ] Delete Analytics.vue
- [ ] Remove Analytics import from App.vue
- [ ] Remove Analytics from Sidebar.vue (id: 2)
- [ ] Remove /analytics route from router

**Status**: ⬜ Not Started | **Priority**: Critical

---

## 9.3 Clients Page (ClientH)

### Compact Table Columns (from ClientHAdmin list_display)
- [ ] Full spec: account | display_name | phone_number | account_tier | status | balance | credit_limit | reward_tier | availability | active_devices | active_sessions | 2FA | last_seen | Actions
- Current has: account | contact | tier | balance | voucher | status | last_seen | actions
- Missing columns: credit_limit | reward_tier | availability | active_devices | active_sessions | 2FA

### Filters (collapsible filter panel)
- [x] status | account_tier | churn
- [ ] reward_tier | two_factor_enabled | auto_renew | home_location | last_login

### Search
- [x] account | display_name | phone_number | username | email

### Row Actions (compact icon buttons)
- [x] Suspend/Activate toggle
- [x] Quick balance top-up
- [x] Churn score badge (green/amber/red)
- [x] Active voucher pill (code + time remaining)

### Click row → Detail Modal
- [x] Tab 1 — Client Information (Overview + inline edit: username, display_name, phone, email, tier, credit_limit)
- [x] Tab 2 — Account Status (sidebar KPIs: balance, points, spent, data, credit)
- [x] Tab 3 — Rewards (Rewards collapsible: points, earned, tier)
- [x] Tab 4 — Security (Security & Access: 2FA, status, joined, last_login, location, zone)
- [x] Tab 5 — Location (inside Security & Access collapsible)
- [x] Tab 6 — Vouchers (Vouchers collapsible)
- [x] Tab 7 — Devices (Devices collapsible)
- [x] Tab 8 — Sessions (Sessions collapsible)
- [x] Tab 9 — Transactions (Transactions collapsible)
- [x] Tab 10 — Intelligence (Intelligence collapsible: LTV, engagement, churn risk, avg txn)
- [x] Profile photo upload (click avatar in sidebar)
- [x] Adjust Balance | Award Points | Suspend/Activate | Force Logout actions

### Bulk Actions
- [x] Suspend selected
- [x] Activate selected
- [x] Reset failed logins
- [x] Export CSV
- [ ] Terminate all sessions
- [ ] Upgrade to Premium
- [ ] Downgrade to Basic

### Metric Cards Update
- [ ] Replace Total Balance with At-Risk Clients (churn > 0.7)
- [ ] Add Suspended count card

**Status**: 🔄 In Progress | **Priority**: Critical

---

## 9.4 Users Page (Django Users + Role Permissions)

### Compact Table Columns
- [x] username | email | role badge | is_active | last_login | 2FA | date_joined | Actions

### Filters
- [x] role/group | is_active | is_staff | is_superuser

### Click row → Edit Modal
- [x] Section 1 — Identity: username, email, first_name, last_name
- [x] Section 2 — Groups: dual-list available/chosen groups
- [x] Section 3 — User Permissions: per-app collapsible with View/Add/Change/Delete checkboxes
- [x] Section 4 — Permissions: is_active, is_staff, is_superuser toggles with descriptions
- [x] Section 5 — Password: hash info, new password, reset password inline
- [x] Section 6 — Important Dates: last_login, date_joined (read-only)
- [ ] Activity Log: last 20 actions from AuditLog

### Metric Cards
- [x] Total Users | Active | Staff | Superusers

### Backend
- [x] groups + user_permissions exposed in serializer
- [x] all_groups endpoint
- [x] all_permissions endpoint (grouped by app)
- [x] reset_password endpoint

**Status**: ✅ Complete | **Priority**: High

---

## 9.5 Vouchers Page (DispatchVoucher) — Full CRUD

### Compact Table Columns (from DispatchVoucherAdmin list_display)
voucher_code | account | package | status | price_paid | activated_at | expires_at | total_usage | usage % | is_roaming | Actions

### Filters
status | is_roaming | package | location | activated_at range | expiring soon (24h, 7d)

### Search
voucher_code | username | account | transaction_id

### Click row → Edit Modal (sections from fieldsets)

Section 1 — Voucher Information: voucher_code, package, user, location, status
Section 2 — Purchase Details: price_paid, activated_at, expires_at, transaction_id, payment_reference
Section 3 — Usage Tracking (read-only): download_bytes, upload_bytes, session_count, usage % progress bar, remaining_time
Section 4 — Device Management: allowed_mac_addresses (tag input), concurrent_sessions
Section 5 — Roaming: is_roaming toggle, home_location

### Bulk Actions
Suspend | Reactivate | Cancel | Export CSV

### Create New: full form with all fields

**Status**: ⬜ Not Started | **Priority**: High

---

## 9.6 Packages Page (PackageType) — Full CRUD

### Compact Table Columns (from PackageTypeAdmin list_display)
name | code | category | tier | price | duration | speed | data_limit | devices | QoS | active | public | featured | sales | Actions

### Filters
category | tier | is_active | is_public | is_featured | allow_roaming | auto_renew | qos_priority

### Search
name | code | description | radius_group | tags

### Click row → Edit Modal (sections from fieldsets)

Section 1 — Basic: name, code, description, category, tier
Section 2 — Pricing and Duration: price, original_price, duration, auto_renew
Section 3 — Technical: speed_limit_mbps, data_limit_mb, device_limit, qos_priority
Section 4 — Network: radius_group, allow_roaming
Section 5 — Display: is_active, is_public, is_featured, display_order, color_code, tags
Section 6 — Promotions: promotion_start, promotion_end, promotion_status (read-only)
Section 7 — Inventory: total_quantity, sold_quantity (read-only), available_quantity (read-only)
Section 8 — Locations (inline): multi-select locations

### Bulk Actions
Activate | Deactivate | Feature | Unfeature

### Extra Row Actions
Duplicate package | View vouchers using this package

**Status**: ⬜ Not Started | **Priority**: High

---

## 9.7 Sessions Page (UserSession) — Full CRUD

### Compact Table Columns (from UserSessionAdmin list_display)
session_id (short) | client | device | type | status | owner | transferred | voucher | duration | data_used | ip | location | login_time | Actions

### Filters
is_active | session_type | is_owner | was_transferred | location | login_time

### Search
session_id | account | mac_address | device_name | active_voucher | ip_address

### Click row → Detail Modal (sections from fieldsets)

Section 1 — Session: session_id, user, device, type, is_active, is_owner, was_transferred
Section 2 — Network: ip_address, location, user_agent
Section 3 — Voucher: active_voucher, voucher_activated, voucher_expires, time_remaining (read-only)
Section 4 — Timing: duration (read-only), auto_logout_minutes (editable), is_expired (read-only)
Section 5 — Usage: data_used (formatted), request_metadata (JSON preview)
Section 6 — Summary: full session_summary panel (read-only)

### Bulk Actions
Terminate selected | Extend voucher 1 hour | Deactivate vouchers

**Status**: ⬜ Not Started | **Priority**: Medium

---

## 9.8 Devices Page (UserDevice) — Full CRUD

### Compact Table Columns (from UserDeviceAdmin list_display)
mac_address | device_name | owner | type | platform | model | status | trusted | online | has_voucher | connections | last_seen | Actions

### Filters
status | device_type | device_platform | is_trusted | auto_connect | last_seen

### Search
mac_address | device_name | model | manufacturer | account | phone_number

### Click row → Edit Modal (sections from fieldsets)

Section 1 — Device: user, mac_address, device_name, type, platform, model, manufacturer
Section 2 — Config: status, is_trusted, auto_connect, max_concurrent_sessions
Section 3 — Location: last_seen_location, favorite_location
Section 4 — Activity (read-only): last_seen, total_connections, is_online, current_session, session limit
Section 5 — Vouchers (read-only): has_active_voucher, active_voucher_session link
Section 6 — History (read-only): previous_owners, device_identification JSON
Section 7 — Statistics (read-only): 30-day stats panel

### Bulk Actions
Trust | Untrust | Block (terminates sessions) | Unblock

**Status**: ⬜ Not Started | **Priority**: Medium

---

## 9.9 Locations Page (Location) — Full CRUD

### Compact Table Columns (from LocationAdmin list_display)
code | name | type | city | active | central | online | users (current/max) | capacity % | roaming | maintenance | Actions

### Filters
location_type | is_active | is_central | is_online | maintenance_mode | allow_roaming_in | allow_roaming_out | city

### Search
code | name | node_id | city | address | nas_identifier

### Click row → Edit Modal (sections from fieldsets)

Section 1 — Core: code, name, location_type, is_active, description, priority
Section 2 — Node Identity: node_id, is_central, central_api_url, sync_api_key
Section 3 — Physical: address, city, coordinates
Section 4 — Network Config: router_config (JSON editor), router_ip, nas_identifier, router_config_preview (read-only)
Section 5 — Health (read-only): is_online, last_seen_online, health_check_interval, offline_duration
Section 6 — Capacity: max_concurrent_users, current_user_count (read-only), capacity % bar, bandwidth_limit_mbps, is_operational, is_overloaded
Section 7 — Operational: maintenance_mode toggle, maintenance_message
Section 8 — Roaming: allow_roaming_in, allow_roaming_out, price_multiplier, max_roaming_locations, time_restrictions, roaming_locations_list (read-only)
Section 9 — Offline: offline_operation_enabled, offline_credit_limit

### Bulk Actions
Activate | Deactivate | Enable Roaming | Disable Roaming

### Chart additions (on top of admin data)
Active clients per location | Revenue per location (30d) | Capacity utilization bar

**Status**: ⬜ Not Started | **Priority**: Medium

---

## Progress Tracker

| Page | Status | Priority |
|------|--------|----------|
| 9.1 Dashboard | 🔄 In Progress | Critical |
| 9.2 Analytics — Delete | ✅ Complete | Critical |
| 9.3 Clients (ClientH) | ✅ Complete | Critical |
| 9.4 Users + Role Permissions | ✅ Complete | High |
| 9.5 Vouchers Full CRUD | ✅ Complete | High |
| 9.6 Packages Full CRUD | ✅ Complete | High |
| 9.7 Sessions (UserSession) | ✅ Complete | Medium |
| 9.8 Devices (UserDevice) | ✅ Complete | Medium |
| 9.9 Locations | ✅ Complete | Medium |
| 9.10 UI Polish (Login, Sidebar, Cards) | 🔄 In Progress | High |

**Implementation Order**: 9.1 → 9.2 → 9.3 → 9.4 → 9.5 → 9.6 → 9.7 → 9.8 → 9.9

---

## 9.10 UI Polish — Login Page, Sidebar & Metric Cards

### Login Page
- [ ] 3D globe background needs improvement — continents not clear enough, satellites need better graphics
- [ ] Globe interaction (drag/rotate) works but needs refinement
- [ ] Form layout needs to feel more premium — typography, spacing, micro-animations on focus
- [ ] Consider adding live stats below the form (active sessions, uptime) fetched pre-login from a public endpoint
- [ ] Mobile responsive — form should stack full-width on small screens
- **Current state**: Globe renders, form works, layout acceptable but not premium quality

### Sidebar Redesign Options
Three candidate designs to evaluate:

**Option A — Icon Rail + Flyout (current style improved)**
- Collapsed: 56px icon-only rail with tooltips
- Expanded: 220px with icon + label + badge counts
- Active item: colored left border + subtle bg highlight
- Section groupings with small uppercase labels
- Bottom: user avatar + role badge + logout

**Option B — Floating Card Sidebar**
- Detached from edge — floats with rounded corners and shadow
- Semi-transparent `bg-slate-900/80 backdrop-blur`
- Icons with colored backgrounds (each section different color)
- Collapses to icon-only pill
- Feels more modern/app-like

**Option C — Top Nav + Left Mini Rail (hybrid)**
- Top bar: logo + search + notifications + user
- Left rail: icon-only, 48px, always visible
- No labels — relies on tooltips and top bar context
- Maximum content space
- Best for dense data pages

### Metric Cards
- [ ] Replace all ModernMetricCard components with compact pill/badge style
- [ ] Clients, Users, Vouchers, Dashboard pages
- [ ] Colorful, small, inline — not large cards taking up vertical space
- [ ] Show trend arrow + % change where data is available

**Status**: 🔄 In Progress | **Priority**: High

---

## Phase 10: Sync / Operations Dashboard (Celery + Background Tasks)

**Goal**: A dedicated sidebar section for operational monitoring of background tasks, queues, and sync operations — like Flower but embedded in the admin panel.

**Sidebar entry**: Operations (or Sync) — new section separate from Finance and Clients

**Details to be planned**: More information to follow.

### Known requirements so far
- Celery task monitoring (like Flower) — active tasks, scheduled tasks, failed tasks
- Queue depths per queue (default, ml, notifications, cleanup)
- Task history with status, duration, result
- Manual trigger for key tasks (refresh KPI, retrain churn model, send reminders, etc.)
- Sync app operations visibility
- Worker status (how many workers online per queue)
- Beat schedule viewer (what runs when)

**Status**: ⬜ Planning | **Priority**: High (after Phase 9 complete)
