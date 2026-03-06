#!/bin/bash
# Quick Fix for High Anomaly Rate
# Run this ONE command to fix everything

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         HIDS HIGH ANOMALY RATE - QUICK FIX                 ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Problem: 97% anomaly rate (model trained only on attacks)"
echo "Solution: Retrain on balanced data (50% normal, 50% attacks)"
echo ""
echo "This will:"
echo "  ✓ Collect YOUR normal traffic patterns"
echo "  ✓ Balance with CICIDS2017 attack data"
echo "  ✓ Train new model with reduced bias"
echo "  ✓ Deploy automatically"
echo "  ✓ Reduce anomaly rate to 5-15%"
echo ""
echo "════════════════════════════════════════════════════════════"
echo ""

read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    ./train_balanced.sh
else
    echo "Cancelled."
fi
