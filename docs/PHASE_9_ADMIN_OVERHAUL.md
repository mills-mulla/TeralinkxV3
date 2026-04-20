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
- [ ] Revenue metric card (the KSh number card in top 4) — Finance KPI owns this
- [ ] Payment Methods pie chart — Finance Transactions owns this
- [ ] Refund Metrics card — Finance Refunds owns this

### Keep
- [ ] Revenue Analytics chart (area chart showing trend over time) — operational, stays

### New Layout Order (all sections collapsible)

**1. System Health** — FIRST, always visible, never collapsible
- DB status | Redis status | Celery status | Disk usage | Internet connectivity
- Color coded: green/amber/red dots
- Auto-refreshes every 30s
- Add Celery queue depths (default, ml, notifications, cleanup queues)
- Add Redis memory usage

**2. Real-Time Monitor** — collapsible, default open
- Live transactions, active sessions, current activity

**3. KPI Banner** — collapsible, default open, compact single row
- Not metric cards — a slim horizontal banner with inline values
- Format: MRR: KSh X | Churn: X% | Cash: KSh X | Pending Txns: X | Failed (24h): X
- Each value is a link to the relevant page
- Source: GET /api/finance/api/kpi/summary/ + suapi/transaction-queue/

**4. Operational Metric Cards** — collapsible, default open
- Total Clients | New (7d) | Active Vouchers | Active Sessions
- Revenue card replaced with Active Sessions

**5. Charts** — collapsible, default open
- Revenue Analytics chart (kept)
- Client Growth chart
- Package Sales pie
- Conversion Funnel

**6. Top Locations + Recent Activity** — collapsible, default open

**7. Device Breakdown + Reward Tiers** — collapsible, default collapsed

**8. Data Quality** — collapsible, default collapsed (moved from Analytics)

**9. Network Analytics** — collapsible, default collapsed (moved from Analytics)

**10. A/B Testing** — collapsible, default collapsed (moved from Analytics)

**11. Dashboard Builder** — accessible via button in page header, not a section

### Quick Links
- Dropdown menu in header (not a row of buttons)
- Items: Pending Transactions, Failed Transactions, Expiring Vouchers, At-Risk Customers

**Status**: ⬜ Not Started | **Priority**: Critical

---

## 9.2 Analytics Page — DELETE ENTIRELY

All tabs relocated:
- Financial → Finance
- Customers RFM → Finance CLV Cohorts
- Retention → Finance Intelligence
- Predictive → Finance Intelligence + KPI
- Audit → Finance Audit Trail
- System Health → Dashboard section 1
- Data Quality → Dashboard section 8
- Network → Dashboard section 9
- A/B Testing → Dashboard section 10
- Dashboard Builder → Dashboard header button

### Tasks
- [ ] Delete Analytics.vue
- [ ] Remove Analytics import from App.vue
- [ ] Remove Analytics from Sidebar.vue (id: 2)
- [ ] Remove /analytics route from router

**Status**: ⬜ Not Started | **Priority**: Critical

---

## 9.3 Clients Page (ClientH)

### Compact Table Columns (from ClientHAdmin list_display)
account | display_name | phone_number | account_tier | status | balance | credit_limit | reward_tier | availability | active_devices | active_sessions | 2FA | last_seen | Actions

### Filters (collapsible filter panel)
status | account_tier | reward_tier | two_factor_enabled | auto_renew | home_location | last_login

### Search
account | display_name | phone_number | username | email

### Row Actions (compact icon buttons)
- Suspend/Activate toggle
- Quick balance top-up
- Churn score badge (green/amber/red)
- Active voucher pill (code + time remaining)

### Click row → Detail Modal (tabbed, matching fieldsets)

Tab 1 — Client Information: user link, account, display_name, phone_number, profile_image
Tab 2 — Account Status: status, account_tier, balance, credit_limit, total_spent, lifetime_data_used, credit_eligible, available_credit
Tab 3 — Rewards: reward_points, reward_tier, total_points_earned, total_points_redeemed, reward_stats
Tab 4 — Security: failed_login_attempts, two_factor_enabled, reset password (superadmin only)
Tab 5 — Location: home_location, current_location, last_location_update
Tab 6 — Vouchers: active_voucher, voucher_expiry, all vouchers with extend/suspend actions
Tab 7 — Devices (inline): mac_address, device_name, type, status, last_seen, trusted, link
Tab 8 — Sessions (inline): session_id, device, type, is_active, login_time, has_voucher, link
Tab 9 — Transactions: all 4 types for this client (read-only)
Tab 10 — Intelligence: churn score, risk factors, retention tasks

### Bulk Actions
- Suspend selected | Activate selected | Reset failed logins | Terminate all sessions | Upgrade to Premium | Downgrade to Basic | Export CSV

### Metric Cards Update
- Replace Total Balance with At-Risk Clients (churn > 0.7)
- Add Suspended count card

**Status**: ⬜ Not Started | **Priority**: Critical

---

## 9.4 Users Page (Django Users + Role Permissions)

### Compact Table Columns
username | email | role badge | is_active | last_login | 2FA | date_joined | Actions

### Filters
role/group | is_active | is_staff | is_superuser

### Click row → Edit Modal

Section 1 — Identity: username, email, first_name, last_name
Section 2 — Role: Superadmin / Finance Manager / Support / Read Only (maps to Django groups)
Section 3 — Model Permissions: per-app View/Add/Edit/Delete checkboxes (Finance, Clients, Packages, Locations, Transactions)
Section 4 — Security: is_active toggle, force password reset, 2FA toggle, last_login (read-only), date_joined (read-only)
Section 5 — Activity Log: last 20 actions from AuditLog

### Metric Cards
Total Users | Active | Staff | Superusers

**Status**: ⬜ Not Started | **Priority**: High

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
| 9.1 Dashboard | ⬜ Not Started | Critical |
| 9.2 Analytics — Delete | ⬜ Not Started | Critical |
| 9.3 Clients (ClientH) | ⬜ Not Started | Critical |
| 9.4 Users + Role Permissions | ⬜ Not Started | High |
| 9.5 Vouchers Full CRUD | ⬜ Not Started | High |
| 9.6 Packages Full CRUD | ⬜ Not Started | High |
| 9.7 Sessions (UserSession) | ⬜ Not Started | Medium |
| 9.8 Devices (UserDevice) | ⬜ Not Started | Medium |
| 9.9 Locations | ⬜ Not Started | Medium |

**Implementation Order**: 9.1 → 9.2 → 9.3 → 9.4 → 9.5 → 9.6 → 9.7 → 9.8 → 9.9

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
