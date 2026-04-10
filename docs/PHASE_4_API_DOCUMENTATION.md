# Phase 4 Executive Intelligence - API Documentation

## Overview
This document provides complete API documentation for Phase 4 Executive Intelligence features including Board Reporting, Pricing Intelligence, and Vendor Intelligence.

---

## Board Reporting APIs

### Generate Board Report
**Endpoint**: `POST /api/finance/board-reports/generate/`  
**Description**: Generate monthly board report for specified period  
**Authentication**: Required  

**Request Body**:
```json
{
  "year": 2025,
  "month": 1
}
```

**Response**:
```json
{
  "message": "Board report generated successfully",
  "report_id": 1,
  "report_period": "January 2025",
  "status": "draft",
  "generation_time_seconds": 3
}
```

---

### Get Latest Board Report
**Endpoint**: `GET /api/finance/board-reports/latest/`  
**Description**: Retrieve the most recent board report  
**Authentication**: Required  

**Response**:
```json
{
  "id": 1,
  "report_period": "January 2025",
  "status": "draft",
  "financial_performance": {
    "revenue": {
      "current": 1500000.00,
      "previous": 1400000.00,
      "growth_pct": 7.1
    },
    "expenses": {
      "current": 800000.00,
      "previous": 750000.00,
      "change_pct": 6.7
    },
    "net_profit": 700000.00,
    "profit_margin_pct": 46.7
  },
  "customer_metrics": {
    "active_customers": 450,
    "new_customers": 25,
    "churned_customers": 10,
    "churn_rate_pct": 2.2,
    "arpu": 3333.33
  },
  "key_highlights": [
    "Strong revenue growth of 7.1% month-over-month",
    "Net customer growth of 15 customers"
  ],
  "challenges": [],
  "recommendations": []
}
```

---

### Export Board Report as PDF
**Endpoint**: `GET /api/finance/board-reports/{report_id}/export/pdf/`  
**Description**: Download board report as PDF file  
**Authentication**: Required  

**Response**: PDF file download

---

### Export Board Report as PowerPoint
**Endpoint**: `GET /api/finance/board-reports/{report_id}/export/pptx/`  
**Description**: Download board report as PowerPoint presentation  
**Authentication**: Required  

**Response**: PPTX file download

---

### Email Board Report
**Endpoint**: `POST /api/finance/board-reports/{report_id}/email/`  
**Description**: Send board report via email with attachments  
**Authentication**: Required  

**Request Body**:
```json
{
  "recipients": ["ceo@teralinkx.com", "cfo@teralinkx.com"],
  "include_pdf": true,
  "include_pptx": true
}
```

**Response**:
```json
{
  "message": "Board report sent to 2 recipients",
  "recipients": ["ceo@teralinkx.com", "cfo@teralinkx.com"]
}
```

---

### Approve Board Report
**Endpoint**: `POST /api/finance/board-reports/{report_id}/approve/`  
**Description**: Mark board report as approved  
**Authentication**: Required  

**Response**:
```json
{
  "message": "Report approved successfully",
  "status": "approved",
  "approved_at": "2025-01-15T10:30:00Z"
}
```

---

### List Board Reports
**Endpoint**: `GET /api/finance/board-reports/list/`  
**Description**: Get list of all board reports (last 12 months)  
**Authentication**: Required  

**Response**:
```json
{
  "reports": [
    {
      "id": 1,
      "report_period": "January 2025",
      "status": "approved",
      "generated_at": "2025-02-01T06:00:00Z",
      "revenue": 1500000.00,
      "net_profit": 700000.00
    }
  ]
}
```

---

## Pricing Intelligence APIs

### Pricing Dashboard
**Endpoint**: `GET /api/finance/pricing/dashboard/`  
**Description**: Get complete pricing intelligence dashboard  
**Authentication**: Required  
**Cache**: 1 hour  

**Response**:
```json
{
  "summary": {
    "total_packages": 5,
    "total_revenue": 1500000.00,
    "average_arpu": 3333.33,
    "average_churn_rate": 2.5
  },
  "package_performance": [
    {
      "package_name": "Premium 50Mbps",
      "customer_count": 150,
      "total_revenue": 750000.00,
      "arpu": 5000.00,
      "churn_rate_pct": 1.5,
      "revenue_per_gb": 0,
      "market_share_pct": 33.3
    }
  ],
  "recommendations": [
    {
      "package": "Basic 10Mbps",
      "type": "retention_risk",
      "priority": "high",
      "recommendation": "Package has 8.5% churn - review pricing and value proposition",
      "estimated_impact": "Reducing churn by 3% could save KES 15,000/month"
    }
  ],
  "timestamp": "2025-01-15T10:00:00Z",
  "from_cache": false
}
```

---

### Package Performance
**Endpoint**: `GET /api/finance/pricing/package-performance/`  
**Description**: Get detailed performance metrics for all packages  
**Authentication**: Required  

**Response**:
```json
{
  "packages": [
    {
      "package_name": "Premium 50Mbps",
      "customer_count": 150,
      "total_revenue": 750000.00,
      "arpu": 5000.00,
      "churn_rate_pct": 1.5,
      "market_share_pct": 33.3
    }
  ],
  "count": 5
}
```

---

### Price Elasticity Analysis
**Endpoint**: `GET /api/finance/pricing/price-elasticity/?package=Premium%2050Mbps&months=6`  
**Description**: Analyze price elasticity for specific package  
**Authentication**: Required  

**Query Parameters**:
- `package` (required): Package name
- `months` (optional): Analysis period in months (default: 6)

**Response**:
```json
{
  "package_name": "Premium 50Mbps",
  "current_customers": 150,
  "churn_rate_pct": 1.5,
  "elasticity_score": 0.5,
  "recommendation": "Low price sensitivity - opportunity for price increase"
}
```

---

### Pricing Recommendations
**Endpoint**: `GET /api/finance/pricing/recommendations/`  
**Description**: Get data-driven pricing recommendations  
**Authentication**: Required  

**Response**:
```json
{
  "recommendations": [
    {
      "package": "Basic 10Mbps",
      "type": "retention_risk",
      "priority": "high",
      "recommendation": "Package has 8.5% churn - review pricing and value proposition",
      "estimated_impact": "Reducing churn by 3% could save KES 15,000/month"
    }
  ],
  "count": 3
}
```

---

### Upgrade/Downgrade Analysis
**Endpoint**: `GET /api/finance/pricing/upgrade-downgrade/`  
**Description**: Analyze package upgrade and downgrade patterns  
**Authentication**: Required  

**Response**:
```json
{
  "upgrades": {
    "count": 0,
    "revenue_impact": 0,
    "common_paths": []
  },
  "downgrades": {
    "count": 0,
    "revenue_impact": 0,
    "common_paths": []
  },
  "net_revenue_change": 0
}
```

---

### Competitive Positioning
**Endpoint**: `GET /api/finance/pricing/competitive-positioning/`  
**Description**: Get competitive positioning data (requires manual input)  
**Authentication**: Required  

**Response**:
```json
{
  "message": "Competitive pricing data requires manual input",
  "structure": {
    "competitor_name": "string",
    "package_name": "string",
    "price": "decimal",
    "features": "list",
    "last_updated": "datetime"
  },
  "recommendation": "Create CompetitorPricing model to track market positioning"
}
```

---

## Vendor Intelligence APIs

### Vendor Dashboard
**Endpoint**: `GET /api/finance/vendors/dashboard/`  
**Description**: Get complete vendor intelligence dashboard  
**Authentication**: Required  
**Cache**: 1 hour  

**Response**:
```json
{
  "summary": {
    "total_vendors": 15,
    "total_spend_12m": 5000000.00,
    "avg_spend_per_vendor": 333333.33,
    "alert_count": 2
  },
  "vendor_performance": [
    {
      "vendor_name": "Bandwidth Provider A",
      "total_spend_12m": 1200000.00,
      "invoice_count": 12,
      "avg_invoice_amount": 100000.00,
      "last_month_spend": 105000.00,
      "trend_pct": 5.0,
      "discrepancy_count": 0,
      "spend_share_pct": 24.0
    }
  ],
  "bandwidth_analysis": [
    {
      "provider": "Bandwidth Provider A",
      "total_cost_12m": 1200000.00,
      "bandwidth_gb": 0,
      "cost_per_gb": 0,
      "invoice_count": 12
    }
  ],
  "alerts": [
    {
      "vendor": "Bandwidth Provider A",
      "alert_type": "concentration_risk",
      "severity": "low",
      "message": "Vendor represents 24.0% of total spend",
      "spend_share": 24.0
    }
  ],
  "recommendations": [
    {
      "vendor": "Bandwidth Provider A",
      "type": "cost_optimization",
      "priority": "high",
      "recommendation": "Top vendor with KES 1,200,000 annual spend - negotiate volume discount",
      "estimated_savings": "5-10% discount could save KES 90,000/year"
    }
  ],
  "timestamp": "2025-01-15T10:00:00Z",
  "from_cache": false
}
```

---

### Vendor Performance
**Endpoint**: `GET /api/finance/vendors/performance/`  
**Description**: Get detailed vendor performance metrics  
**Authentication**: Required  

**Response**:
```json
{
  "vendors": [
    {
      "vendor_name": "Bandwidth Provider A",
      "total_spend_12m": 1200000.00,
      "invoice_count": 12,
      "avg_invoice_amount": 100000.00,
      "last_month_spend": 105000.00,
      "trend_pct": 5.0,
      "spend_share_pct": 24.0
    }
  ],
  "count": 15
}
```

---

### Bandwidth Cost Analysis
**Endpoint**: `GET /api/finance/vendors/bandwidth-costs/`  
**Description**: Analyze bandwidth costs by upstream provider  
**Authentication**: Required  

**Response**:
```json
{
  "providers": [
    {
      "provider": "Bandwidth Provider A",
      "total_cost_12m": 1200000.00,
      "bandwidth_gb": 0,
      "cost_per_gb": 0,
      "invoice_count": 12
    }
  ],
  "count": 3
}
```

---

### Contract Expiry Calendar
**Endpoint**: `GET /api/finance/vendors/contract-calendar/`  
**Description**: Get upcoming contract renewals (requires VendorContract model)  
**Authentication**: Required  

**Response**:
```json
{
  "message": "Contract tracking requires VendorContract model",
  "structure": {
    "vendor_name": "string",
    "contract_type": "string",
    "start_date": "date",
    "end_date": "date",
    "monthly_cost": "decimal",
    "auto_renew": "boolean",
    "notice_period_days": "integer"
  },
  "upcoming_renewals": [],
  "recommendation": "Create VendorContract model to track contract lifecycle"
}
```

---

### Invoice Discrepancy Alerts
**Endpoint**: `GET /api/finance/vendors/invoice-alerts/`  
**Description**: Get invoice discrepancy and spending alerts  
**Authentication**: Required  

**Response**:
```json
{
  "alerts": [
    {
      "vendor": "Vendor X",
      "alert_type": "spending_spike",
      "severity": "medium",
      "message": "Spending increased 55.0% last month",
      "last_month_spend": 155000.00
    }
  ],
  "count": 2
}
```

---

### Vendor Recommendations
**Endpoint**: `GET /api/finance/vendors/recommendations/`  
**Description**: Get vendor management recommendations  
**Authentication**: Required  

**Response**:
```json
{
  "recommendations": [
    {
      "vendor": "Bandwidth Provider A",
      "type": "cost_optimization",
      "priority": "high",
      "recommendation": "Top vendor with KES 1,200,000 annual spend - negotiate volume discount",
      "estimated_savings": "5-10% discount could save KES 90,000/year"
    }
  ],
  "count": 3
}
```

---

## Scheduled Tasks

### Monthly Board Report Generation
**Task**: `finance.generate_monthly_board_report`  
**Schedule**: 1st of each month at 6:00 AM  
**Queue**: default  
**Description**: Automatically generates board report for previous month  

---

## Testing Commands

### Test Board Report Export
```bash
python manage.py test_board_report_export
python manage.py test_board_report_export --report-id=1
python manage.py test_board_report_export --test-email=admin@teralinkx.com
```

---

## Installation Requirements

Add to `requirements.txt`:
```
reportlab==4.0.7
python-pptx==0.6.23
```

Install:
```bash
pip install reportlab python-pptx
```

---

## URL Configuration

Add to main `urls.py`:
```python
from django.urls import path, include

urlpatterns = [
    # ... existing patterns
    path('api/finance/board-reports/', include('apps.finance.urls_board_report')),
    path('api/finance/pricing/', include('apps.finance.urls_pricing')),
    path('api/finance/vendors/', include('apps.finance.urls_vendor')),
]
```

---

## Notes

1. **Caching**: Pricing and Vendor dashboards are cached for 1 hour to improve performance
2. **Authentication**: All endpoints require JWT authentication
3. **Permissions**: Currently using IsAuthenticated, consider adding role-based permissions
4. **Email Configuration**: Ensure Django email settings are configured for board report distribution
5. **File Storage**: PDF/PPTX exports are generated in-memory and served as downloads
6. **Data Requirements**: Some features require additional models (VendorContract, CompetitorPricing) for full functionality

---

## Future Enhancements

1. Create `VendorContract` model for contract lifecycle management
2. Create `CompetitorPricing` model for competitive analysis
3. Create `PackageChangeHistory` model for upgrade/downgrade tracking
4. Add bandwidth usage tracking for cost-per-GB calculations
5. Implement invoice validation workflow for discrepancy detection
6. Add role-based permissions (CEO, CFO, Finance Manager)
7. Create frontend dashboards for all Phase 4 features
