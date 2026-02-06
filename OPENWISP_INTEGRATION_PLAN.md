# OpenWISP Integration & Admin Panel Rebuild Plan

## Phase 1: OpenWISP RADIUS Integration

### 1.1 Install Dependencies
```bash
docker compose exec webv3 pip install -r requirements.txt
```

### 1.2 Configure OpenWISP Apps
Add to INSTALLED_APPS in settings.py:
- openwisp_users
- openwisp_radius
- openwisp_utils
- rest_framework.authtoken

### 1.3 Database Schema
- Create RADIUS tables (radcheck, radreply, radacct, radgroupcheck, radgroupreply, radusergroup)
- Integrate with existing ClientH model
- Map TeralinkX users to RADIUS users

### 1.4 FreeRADIUS Configuration
- Configure FreeRADIUS to use Django database
- Set up SQL queries for authentication
- Configure NAS (Network Access Server) clients
- Set up accounting

### 1.5 API Endpoints
Create endpoints for:
- User authentication (RADIUS)
- Session management
- Accounting data
- Bandwidth tracking
- Online users

## Phase 2: Admin Panel Rebuild

### 2.1 Technology Stack
**Backend:**
- Django REST Framework (already installed)
- OpenWISP Admin extensions

**Frontend Options:**
1. **Vue.js 3 + Vuetify** (Modern, component-based)
2. **React + Material-UI** (Popular, large ecosystem)
3. **Django Admin + Grappelli** (Quick, Django-native)

**Recommended: Vue.js 3 + Vuetify**
- Already using Vue for customer portal
- Consistent tech stack
- Modern UI components
- Easy integration with existing APIs

### 2.2 Admin Panel Features

#### Dashboard
- Real-time statistics
- Active users count
- Revenue metrics
- Network health
- Recent transactions
- System alerts

#### User Management
- Client list with search/filter
- User details view
- Account status management
- Balance management
- Device management
- Session history
- Transaction history

#### Package Management
- Package CRUD
- Pricing tiers
- Validity periods
- Data limits
- Speed limits

#### Voucher Management
- Generate vouchers
- Bulk generation
- Voucher status
- Redemption tracking
- Expiry management

#### Network Management (OpenWISP)
- Online users
- Active sessions
- Bandwidth usage
- Device tracking
- Location-based stats
- NAS management

#### Financial Management
- Transaction history
- Payment reconciliation
- Revenue reports
- M-Pesa integration status
- Balance adjustments
- Refunds

#### Reports & Analytics
- User growth
- Revenue trends
- Package popularity
- Location performance
- Device statistics
- Payment methods

#### System Settings
- Location management
- Payment gateway config
- RADIUS settings
- Email/SMS templates
- System parameters

### 2.3 Admin Panel Structure

```
/admin-panel/
├── src/
│   ├── components/
│   │   ├── Dashboard/
│   │   ├── Users/
│   │   ├── Packages/
│   │   ├── Vouchers/
│   │   ├── Network/
│   │   ├── Finance/
│   │   ├── Reports/
│   │   └── Settings/
│   ├── layouts/
│   │   ├── AdminLayout.vue
│   │   └── AuthLayout.vue
│   ├── router/
│   │   └── index.js
│   ├── store/
│   │   ├── modules/
│   │   │   ├── auth.js
│   │   │   ├── users.js
│   │   │   ├── network.js
│   │   │   └── finance.js
│   │   └── index.js
│   ├── services/
│   │   ├── api.js
│   │   ├── auth.js
│   │   └── websocket.js
│   └── App.vue
└── package.json
```

## Phase 3: Integration Points

### 3.1 Existing Models Integration
- ClientH → RADIUS users
- UserDevice → NAS clients
- UserSession → RADIUS sessions
- DispatchVoucher → RADIUS vouchers
- TransactionQueue → Payment tracking

### 3.2 API Endpoints to Create

**RADIUS Management:**
- POST /api/radius/authenticate
- POST /api/radius/authorize
- POST /api/radius/accounting
- GET /api/radius/sessions/active
- POST /api/radius/disconnect

**Admin APIs:**
- GET /api/admin/dashboard/stats
- GET /api/admin/users/
- GET /api/admin/users/{id}/
- PATCH /api/admin/users/{id}/
- GET /api/admin/network/online
- GET /api/admin/finance/transactions
- GET /api/admin/reports/revenue

### 3.3 Real-time Features
- WebSocket for live updates
- Active sessions monitoring
- Transaction notifications
- System alerts

## Phase 4: Implementation Steps

### Step 1: OpenWISP Setup (Week 1)
1. Install OpenWISP packages
2. Run migrations
3. Configure RADIUS settings
4. Test RADIUS authentication
5. Integrate with FreeRADIUS

### Step 2: Admin Backend APIs (Week 2)
1. Create admin serializers
2. Build admin viewsets
3. Add permissions/authentication
4. Create dashboard stats endpoint
5. Test all endpoints

### Step 3: Admin Frontend Setup (Week 3)
1. Initialize Vue.js project
2. Set up Vuetify
3. Create layout structure
4. Implement authentication
5. Build navigation

### Step 4: Core Admin Features (Week 4)
1. Dashboard with stats
2. User management
3. Package management
4. Voucher management
5. Basic reports

### Step 5: Network Management (Week 5)
1. Online users view
2. Session management
3. Bandwidth monitoring
4. Device tracking
5. NAS management

### Step 6: Financial Features (Week 6)
1. Transaction history
2. Revenue reports
3. Payment reconciliation
4. Balance management
5. Refund processing

### Step 7: Testing & Deployment (Week 7)
1. Integration testing
2. Performance optimization
3. Security audit
4. Documentation
5. Production deployment

## Phase 5: Configuration Files

### FreeRADIUS SQL Configuration
```sql
# /etc/freeradius/3.0/mods-available/sql

sql {
    driver = "rlm_sql_postgresql"
    dialect = "postgresql"
    
    server = "postgres"
    port = 5432
    login = "teralinkx"
    password = "justboot"
    radius_db = "teralinkx"
    
    # Use Django tables
    read_clients = yes
    
    # Custom queries for Django models
    authorize_check_query = "SELECT ..."
    authorize_reply_query = "SELECT ..."
    accounting_start_query = "INSERT INTO ..."
    accounting_stop_query = "UPDATE ..."
}
```

### Django RADIUS Settings
```python
# settings.py

OPENWISP_RADIUS_ENABLED = True
OPENWISP_RADIUS_API_URLCONF = 'openwisp_radius.urls'
OPENWISP_RADIUS_API_BASEURL = '/api/radius/'

OPENWISP_RADIUS_FREERADIUS_ALLOWED_HOSTS = ['127.0.0.1', 'freeradius']
OPENWISP_RADIUS_API_AUTHORIZE_REJECT = True

# Custom user model integration
OPENWISP_USERS_AUTH_API = True
```

## Phase 6: Security Considerations

1. **Admin Authentication:**
   - JWT tokens for admin users
   - Role-based access control (RBAC)
   - Two-factor authentication
   - Session timeout

2. **RADIUS Security:**
   - Shared secrets for NAS
   - Encrypted passwords
   - Rate limiting
   - IP whitelisting

3. **API Security:**
   - HTTPS only
   - CORS configuration
   - Rate limiting
   - Input validation

## Next Steps

1. Review and approve this plan
2. Decide on admin panel frontend (Vue.js recommended)
3. Start with OpenWISP installation
4. Set up development environment
5. Begin Phase 1 implementation

## Questions to Answer

1. Do you want to use existing Django admin or build custom Vue.js admin?
2. Should we integrate with existing FreeRADIUS or set up new one?
3. What are the priority features for admin panel?
4. Do you need multi-tenancy (multiple organizations)?
5. What level of customization do you need for RADIUS?
