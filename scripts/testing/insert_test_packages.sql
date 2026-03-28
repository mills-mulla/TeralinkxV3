-- Insert test packages with 1-3 KSH prices for payment testing
-- Run this with: sqlite3 db.sqlite3 < insert_test_packages.sql

-- First, ensure we have a default location
INSERT OR IGNORE INTO locations_location (
    name, location_code, is_default, is_active, created_at, updated_at
) VALUES (
    'Test Location', 'TEST001', 1, 1, datetime('now'), datetime('now')
);

-- Get the location ID (assuming it's 1, adjust if needed)
-- Insert test packages
INSERT OR REPLACE INTO packages_packagetype (
    name, code, price, duration, data_limit_mb, speed_limit_mbps, device_limit,
    description, is_active, is_visible, package_type, billing_cycle,
    location_id, created_at, updated_at
) VALUES 
-- 1 KSH packages
(
    'Test Mini 1KSH', 'TEST1KSH', 1.00, '00:05:00', 10, 1.0, 1,
    'Test package - 1 KSH for 5 minutes', 1, 1, 'internet', 'one_time',
    1, datetime('now'), datetime('now')
),
(
    'Test Micro 1KSH Alt', 'MICRO1', 1.00, '00:03:00', 5, 1.0, 1,
    'Alternative 1 KSH test package', 1, 1, 'internet', 'one_time',
    1, datetime('now'), datetime('now')
),

-- 2 KSH packages  
(
    'Test Basic 2KSH', 'TEST2KSH', 2.00, '00:10:00', 25, 2.0, 1,
    'Test package - 2 KSH for 10 minutes', 1, 1, 'internet', 'one_time',
    1, datetime('now'), datetime('now')
),
(
    'Test Quick 2KSH Alt', 'QUICK2', 2.00, '00:08:00', 20, 2.0, 1,
    'Alternative 2 KSH test package', 1, 1, 'internet', 'one_time',
    1, datetime('now'), datetime('now')
),

-- 3 KSH packages
(
    'Test Standard 3KSH', 'TEST3KSH', 3.00, '00:15:00', 50, 3.0, 2,
    'Test package - 3 KSH for 15 minutes', 1, 1, 'internet', 'one_time',
    1, datetime('now'), datetime('now')
);

-- Display the inserted packages
SELECT 
    name, code, price, duration, data_limit_mb, speed_limit_mbps, device_limit, is_active
FROM packages_packagetype 
WHERE price <= 3.00 AND is_active = 1
ORDER BY price, name;