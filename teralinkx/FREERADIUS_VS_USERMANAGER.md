# MikroTik User Manager vs FreeRADIUS - Complete Comparison

## Architecture Comparison

### MikroTik User Manager:
```
MikroTik Router
├── User Manager (built-in)
│   ├── Users Database
│   ├── Profiles
│   ├── Sessions
│   └── RADIUS Server
└── Hotspot/PPPoE uses User Manager
```

### FreeRADIUS:
```
Separate Server
├── FreeRADIUS (RADIUS Server)
│   ├── PostgreSQL/MySQL Database
│   ├── Groups (Profiles)
│   ├── Accounting
│   └── Authentication
└── MikroTik → Queries FreeRADIUS
```

---

## Key Concepts Mapping

| MikroTik User Manager | FreeRADIUS | Description |
|----------------------|------------|-------------|
| **User** | **radcheck** table | Username + Password |
| **Profile** | **Group** | Speed limits, quotas, expiry |
| **Limitation** | **radgroupcheck/radgroupreply** | Profile restrictions |
| **Session** | **radacct** table | Active/past connections |
| **User → Profile** | **radusergroup** table | Assign user to group |

---

## Database Tables Explained

### 1. radcheck - User Credentials
```sql
-- Like User Manager "Users" table
username | attribute          | op | value
---------|-------------------|----|---------
voucher1 | Cleartext-Password| := | pass123
voucher2 | Cleartext-Password| := | abc456
```

### 2. radreply - User-Specific Attributes
```sql
-- Individual user overrides (not from profile)
username | attribute           | op | value
---------|--------------------|----|-------
voucher1 | Mikrotik-Rate-Limit| := | 10M/20M
```

### 3. radgroupcheck - Profile Requirements
```sql
-- Like User Manager "Profile Limitations"
groupname  | attribute      | op | value
-----------|---------------|----|-----------
5mbps-plan | Expiration    | := | 2026-03-06
5mbps-plan | Simultaneous-Use| := | 1
```

### 4. radgroupreply - Profile Attributes
```sql
-- Like User Manager "Profile" settings
groupname  | attribute           | op | value
-----------|--------------------|----|-------
5mbps-plan | Mikrotik-Rate-Limit| := | 2M/5M
5mbps-plan | Session-Timeout    | := | 86400
```

### 5. radusergroup - User to Profile Assignment
```sql
-- Assign user to profile/group
username | groupname  | priority
---------|-----------|----------
voucher1 | 5mbps-plan| 1
voucher2 | 10mbps-plan| 1
```

### 6. radacct - Session Tracking
```sql
-- Like User Manager "Sessions"
username | acctsessionid | acctstarttime | acctinputoctets | acctoutputoctets
---------|--------------|---------------|-----------------|------------------
voucher1 | sess123      | 2026-02-06... | 52428800        | 104857600
```

---

## Common Tasks Comparison

### 1. Create User with Profile

**MikroTik User Manager:**
```
/user-manager/user add name=voucher1 password=pass123 profile=5mbps-plan
```

**FreeRADIUS:**
```sql
-- Create user
INSERT INTO radcheck (username, attribute, op, value) 
VALUES ('voucher1', 'Cleartext-Password', ':=', 'pass123');

-- Assign to profile
INSERT INTO radusergroup (username, groupname, priority) 
VALUES ('voucher1', '5mbps-plan', 1);
```

---

### 2. Create Profile with Speed Limit

**MikroTik User Manager:**
```
/user-manager/profile add name=5mbps-plan rate-limit=2M/5M
```

**FreeRADIUS:**
```sql
INSERT INTO radgroupreply (groupname, attribute, op, value) 
VALUES ('5mbps-plan', 'Mikrotik-Rate-Limit', ':=', '2M/5M');
```

---

### 3. Set Expiry Date

**MikroTik User Manager:**
```
/user-manager/user set voucher1 valid-until="mar/06/2026"
```

**FreeRADIUS:**
```sql
INSERT INTO radgroupcheck (groupname, attribute, op, value) 
VALUES ('5mbps-plan', 'Expiration', ':=', 'Mar 06 2026');
```

---

### 4. View Active Sessions

**MikroTik User Manager:**
```
/user-manager/session print
```

**FreeRADIUS:**
```sql
SELECT username, acctsessionid, acctstarttime, 
       acctinputoctets, acctoutputoctets 
FROM radacct 
WHERE acctstoptime IS NULL;
```

---

### 5. Disconnect User

**MikroTik User Manager:**
```
/user-manager/session remove [find user=voucher1]
```

**FreeRADIUS:**
```bash
# Send CoA (Change of Authorization) to MikroTik
echo "User-Name=voucher1" | radclient 192.168.88.1:3799 disconnect secret123
```

---

## RADIUS Attributes for MikroTik

### Speed Limits:
```
Mikrotik-Rate-Limit = "upload/download"
Examples:
  "512k/1M"   = 512kbps up / 1Mbps down
  "2M/5M"     = 2Mbps up / 5Mbps down
  "10M/20M"   = 10Mbps up / 20Mbps down
```

### Time Limits:
```
Session-Timeout = 3600          # Max 1 hour per session
Expiration = "Mar 06 2026"      # Account expires
Login-Time = "Al0800-1800"      # Only 8am-6pm daily
Max-Daily-Session = 86400       # Max 24 hours per day
```

### Data Quotas:
```
Max-Octets = 10737418240        # 10GB total (upload + download)
Max-Input-Octets = 5368709120   # 5GB upload only
Max-Output-Octets = 5368709120  # 5GB download only
```

### Concurrent Sessions:
```
Simultaneous-Use = 1            # Only 1 device at a time
Simultaneous-Use = 3            # Max 3 devices
```

### IP Assignment:
```
Framed-IP-Address = "192.168.1.100"  # Static IP
Framed-Pool = "pool1"                # IP pool name
```

---

## Authentication Flow

### MikroTik User Manager:
```
1. User connects to Hotspot
2. MikroTik checks User Manager database
3. User Manager validates credentials
4. MikroTik applies profile limits
5. Session tracked in User Manager
```

### FreeRADIUS:
```
1. User connects to Hotspot
2. MikroTik sends RADIUS Access-Request to FreeRADIUS
3. FreeRADIUS queries database (radcheck + radgroupreply)
4. FreeRADIUS sends Access-Accept with attributes
5. MikroTik applies attributes (speed, timeout, etc.)
6. MikroTik sends Accounting updates to FreeRADIUS
7. FreeRADIUS logs to radacct table
```

---

## Accounting (Session Tracking)

### Accounting Packets:

**Start:**
```
Acct-Status-Type = Start
→ Creates new row in radacct
```

**Interim-Update (Real-time):**
```
Acct-Status-Type = Interim-Update
Acct-Session-Time = 300
Acct-Input-Octets = 52428800
Acct-Output-Octets = 104857600
→ Updates existing row in radacct
```

**Stop:**
```
Acct-Status-Type = Stop
Acct-Terminate-Cause = User-Request
→ Sets acctstoptime in radacct
```

---

## Advantages of FreeRADIUS over User Manager

### ✅ Pros:
1. **Centralized** - One RADIUS server for multiple MikroTik routers
2. **Scalable** - Handle thousands of users
3. **Real-time stats** - Interim updates every 60 seconds
4. **Flexible** - Custom attributes, complex policies
5. **Database** - PostgreSQL/MySQL for advanced queries
6. **API-friendly** - Easy to integrate with billing systems
7. **Multi-vendor** - Works with Ubiquiti, Cisco, etc.

### ❌ Cons:
1. **Complexity** - Steeper learning curve
2. **Separate server** - Need dedicated machine/container
3. **Manual setup** - No GUI by default
4. **Database knowledge** - Need SQL skills

---

## MikroTik Configuration for FreeRADIUS

### 1. Add RADIUS Server:
```
/radius add service=hotspot,login address=192.168.88.10 secret=testing123
```

### 2. Enable RADIUS for Hotspot:
```
/ip hotspot profile set default use-radius=yes
```

### 3. Enable Interim Updates (Real-time):
```
/radius set [find] accounting=yes interim-update=60s
```

### 4. Enable CoA (Disconnect):
```
/radius incoming set accept=yes port=3799
```

---

## Testing Commands

### Test Authentication:
```bash
radtest username password radius-server-ip 0 secret
```

### Test Accounting:
```bash
echo "User-Name=test,Acct-Status-Type=Start" | radclient radius-ip:1813 acct secret
```

### Test Disconnect (CoA):
```bash
echo "User-Name=test" | radclient mikrotik-ip:3799 disconnect secret
```

---

## Common Issues & Solutions

### Issue: Access-Reject
**Cause:** User not in database or wrong password
**Fix:** Check radcheck table

### Issue: No speed limit applied
**Cause:** Missing Mikrotik-Rate-Limit attribute
**Fix:** Add to radreply or radgroupreply

### Issue: Sessions not tracked
**Cause:** Accounting not enabled on MikroTik
**Fix:** Enable accounting in /radius settings

### Issue: Can't disconnect users
**Cause:** CoA not enabled on MikroTik
**Fix:** Enable /radius incoming accept=yes

---

## Next Steps to Learn:

1. **Practice SQL queries** - Get comfortable with radcheck, radreply, radacct
2. **Test with MikroTik** - Configure your router to use FreeRADIUS
3. **Monitor logs** - Watch FreeRADIUS debug output: `radiusd -X`
4. **Build API** - Create REST API to manage users/sessions
5. **Integrate with V3** - Replace User Manager API calls

---

## Useful SQL Queries

### View all users and their groups:
```sql
SELECT r.username, r.value as password, g.groupname 
FROM radcheck r 
LEFT JOIN radusergroup g ON r.username = g.username 
WHERE r.attribute = 'Cleartext-Password';
```

### View active sessions:
```sql
SELECT username, acctsessionid, acctstarttime, 
       acctinputoctets/1048576 as mb_uploaded,
       acctoutputoctets/1048576 as mb_downloaded
FROM radacct 
WHERE acctstoptime IS NULL;
```

### View user's total data usage:
```sql
SELECT username, 
       SUM(acctinputoctets)/1073741824 as gb_uploaded,
       SUM(acctoutputoctets)/1073741824 as gb_downloaded
FROM radacct 
WHERE username = 'voucher1'
GROUP BY username;
```

### View profile attributes:
```sql
SELECT groupname, attribute, value 
FROM radgroupreply 
WHERE groupname = '5mbps-plan';
```

---

## Resources:
- FreeRADIUS Wiki: https://wiki.freeradius.org/
- MikroTik RADIUS: https://wiki.mikrotik.com/wiki/Manual:RADIUS_Client
- SQL HOWTO: https://wiki.freeradius.org/config/SQL-HOWTO
