#!/bin/bash

cd "$(dirname "$0")"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Starting Jupyter Notebook for HIDS Training       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "✅ Datasets found:"
ls -lh datasets/KDDTrain+.txt datasets/cicids2017_cleaned.csv datasets/*2018*.csv 2>/dev/null | awk '{print "   "$9" ("$5")"}'
echo ""
echo "Starting Jupyter..."
echo ""
echo "The notebook will open in your browser automatically."
echo "Look for: train_comprehensive.ipynb"
echo ""
echo "Press Ctrl+C to stop Jupyter when done."
echo ""

# Start Jupyter
jupyter notebook notebooks/train_comprehensive.ipynb
