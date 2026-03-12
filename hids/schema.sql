-- HIDS Database Schema

-- Suricata alerts
CREATE TABLE IF NOT EXISTS suricata_alerts (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    flow_id BIGINT,
    src_ip INET NOT NULL,
    src_port INTEGER,
    dest_ip INET NOT NULL,
    dest_port INTEGER,
    proto TEXT,
    alert_signature TEXT,
    alert_category TEXT,
    alert_severity INTEGER,
    raw_event JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_suricata_timestamp ON suricata_alerts(timestamp DESC);
CREATE INDEX idx_suricata_src_ip ON suricata_alerts(src_ip);
CREATE INDEX idx_suricata_dest_ip ON suricata_alerts(dest_ip);
CREATE INDEX idx_suricata_severity ON suricata_alerts(alert_severity);

-- Zeek connection logs
CREATE TABLE IF NOT EXISTS zeek_connections (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    uid TEXT,
    src_ip INET NOT NULL,
    src_port INTEGER,
    dest_ip INET NOT NULL,
    dest_port INTEGER,
    proto TEXT,
    service TEXT,
    duration FLOAT,
    orig_bytes BIGINT,
    resp_bytes BIGINT,
    conn_state TEXT,
    raw_event JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_zeek_timestamp ON zeek_connections(timestamp DESC);
CREATE INDEX idx_zeek_src_ip ON zeek_connections(src_ip);
CREATE INDEX idx_zeek_dest_ip ON zeek_connections(dest_ip);

-- ML predictions
CREATE TABLE IF NOT EXISTS ml_predictions (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    event_type TEXT NOT NULL,
    event_id BIGINT,
    prediction TEXT NOT NULL,
    confidence FLOAT,
    features JSONB,
    ground_truth TEXT
);

CREATE INDEX idx_ml_timestamp ON ml_predictions(timestamp DESC);
CREATE INDEX idx_ml_prediction ON ml_predictions(prediction);
CREATE INDEX idx_ml_ground_truth ON ml_predictions(ground_truth);

-- Correlated alerts
CREATE TABLE IF NOT EXISTS correlated_alerts (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    alert_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    src_ip INET,
    dest_ip INET,
    description TEXT,
    event_count INTEGER DEFAULT 1,
    first_seen TIMESTAMP WITH TIME ZONE,
    last_seen TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'open',
    metadata JSONB
);

CREATE INDEX idx_corr_timestamp ON correlated_alerts(timestamp DESC);
CREATE INDEX idx_corr_severity ON correlated_alerts(severity);
CREATE INDEX idx_corr_status ON correlated_alerts(status);

-- Blocked IPs
CREATE TABLE IF NOT EXISTS blocked_ips (
    id BIGSERIAL PRIMARY KEY,
    ip_address INET NOT NULL UNIQUE,
    blocked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    reason TEXT,
    blocked_by TEXT DEFAULT 'dashboard'
);

CREATE INDEX idx_blocked_ip ON blocked_ips(ip_address);
CREATE INDEX idx_blocked_at ON blocked_ips(blocked_at DESC);
