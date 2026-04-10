# Phase 0.2 Week 3: TimescaleDB 10% Rollout

**Status**: Ready to Execute  
**Date**: 2025-01-XX  
**Duration**: 1 week  
**Rollout Target**: 10% of payment queries

---

## Pre-Rollout Checklist

- [ ] Week 1-2 completed (hypertables created, data migrated, validated)
- [ ] Feature flag exists and is at 0%
- [ ] Data integrity confirmed (100% match)
- [ ] Monitoring tools ready
- [ ] Rollback plan documented

---

## Step 1: Validate Current State (Day 1 Morning)

```bash
# Check feature flag status
python manage.py shell -c "from core.models import FeatureFlag; print(FeatureFlag.objects.get(name='timescaledb_migration'))"

# Validate data integrity
python manage.py validate_timescale

# Run baseline performance test
python manage.py monitor_timescale --days 30 --iterations 5
```

**Expected Results**:
- Feature flag at 0%, enabled=False
- Data integrity: 100% match
- Performance baseline established

---

## Step 2: Run Dual-Read Consistency Tests (Day 1 Afternoon)

```bash
# Test query consistency
python manage.py test_dual_read --verbose

# Expected: All tests PASS
```

**If any tests fail**: Do NOT proceed. Investigate and fix issues first.

---

## Step 3: Enable 10% Rollout (Day 2 Morning)

```bash
# Enable 10% rollout with safety checks
python manage.py enable_timescale_rollout --percentage 10

# Verify rollout
python manage.py shell -c "from core.models import FeatureFlag; f=FeatureFlag.objects.get(name='timescaledb_migration'); print(f'Enabled: {f.enabled}, Rollout: {f.rollout_percentage}%')"
```

**Expected Output**:
```
=== TimescaleDB Rollout: 10% ===
Running safety checks...
  ✓ Row counts match: 50 transactions
  ✓ TimescaleDB connection OK
✓ Safety checks passed

✓ Rollout updated: 0% → 10%

Estimated affected queries: ~5 transactions

⚠ Monitor performance with: python manage.py monitor_timescale
```

---

## Step 4: Continuous Monitoring (Day 2-7)

### Immediate Monitoring (First 2 Hours)

```bash
# Run continuous monitor for 2 hours, checking every 5 minutes
python manage.py monitor_rollout --duration 120 --interval 5
```

**Watch for**:
- Health: OK (row counts match)
- Performance: Improvement > -50% (allow up to 50% slower)
- Errors: 0

### Daily Monitoring (Day 2-7)

Run these checks **twice daily** (morning and evening):

```bash
# Quick health check
python manage.py test_dual_read

# Performance comparison
python manage.py monitor_timescale --days 7 --iterations 3

# Check for discrepancies
python manage.py validate_timescale
```

---

## Step 5: Log Analysis (Daily)

Check application logs for TimescaleDB-related errors:

```bash
# Check Django logs
docker-compose logs teralinkx | grep -i timescale | tail -50

# Check PostgreSQL logs
docker-compose logs postgres | grep -i error | tail -20
```

**Red flags**:
- Connection timeouts
- Query errors
- Data inconsistencies
- Performance degradation > 50%

---

## Emergency Rollback Procedure

If any critical issues detected:

```bash
# Immediate rollback to 0%
python manage.py rollback_timescale --to-percentage 0 --confirm

# Verify rollback
python manage.py shell -c "from core.models import FeatureFlag; print(FeatureFlag.objects.get(name='timescaledb_migration'))"
```

**Rollback triggers**:
- Data integrity mismatch
- Error rate > 1%
- Performance degradation > 100% (2x slower)
- Database connection failures

---

## Success Criteria (End of Week 3)

- [ ] 10% rollout stable for 5+ days
- [ ] Zero data integrity issues
- [ ] Performance within acceptable range (-50% to +100%)
- [ ] Zero critical errors
- [ ] All dual-read tests passing

---

## Week 3 Completion Report

**Date**: _____________  
**Rollout Percentage**: 10%  
**Duration**: 7 days  

### Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Data Integrity | 100% match | ___% | ☐ Pass ☐ Fail |
| Performance Change | -50% to +100% | ___% | ☐ Pass ☐ Fail |
| Error Rate | 0% | ___% | ☐ Pass ☐ Fail |
| Uptime | 100% | ___% | ☐ Pass ☐ Fail |

### Issues Encountered

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Resolutions

1. _____________________________________________
2. _____________________________________________
3. _____________________________________________

### Recommendation

☐ **Proceed to Week 4 (50% rollout)**  
☐ **Extend Week 3 monitoring**  
☐ **Rollback and investigate**

**Approved by**: _____________  
**Date**: _____________

---

## Next Steps (Week 4)

If Week 3 successful:
- Increase rollout to 50%
- Continue monitoring
- Prepare for full cutover

See: `/docs/PHASE_0_2_WEEK_4_GUIDE.md`

---

## Troubleshooting

### Issue: Row count mismatch

```bash
# Check for pending writes
python manage.py shell -c "from finance.models import PaymentTransaction; print(f'PG: {PaymentTransaction.objects.using(\"default\").count()}, TS: {PaymentTransaction.objects.using(\"timescale\").count()}')"

# Re-sync if needed
python manage.py setup_timescaledb --sync-only
```

### Issue: Performance degradation

```bash
# Check TimescaleDB chunk configuration
python manage.py shell -c "from django.db import connections; cursor = connections['timescale'].cursor(); cursor.execute('SELECT show_chunks(\\\'payment_transaction\\\');'); print(cursor.fetchall())"

# Analyze query plans
python manage.py monitor_timescale --days 7 --iterations 10
```

### Issue: Connection errors

```bash
# Check database connectivity
docker-compose ps postgres
docker-compose logs postgres | tail -50

# Restart if needed
docker-compose restart postgres
```

---

## Commands Reference

| Command | Purpose |
|---------|---------|
| `enable_timescale_rollout --percentage 10` | Enable 10% rollout |
| `monitor_rollout --duration 60` | Monitor for 60 minutes |
| `test_dual_read` | Test query consistency |
| `monitor_timescale` | Compare performance |
| `validate_timescale` | Check data integrity |
| `rollback_timescale --to-percentage 0 --confirm` | Emergency rollback |

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-XX  
**Owner**: DevOps Team
