#!/bin/bash

# Production Deployment Script for Teralinkx Frontend
# This script builds and deploys the frontend for production

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: package.json not found. Please run this script from the project root."
    exit 1
fi

# Clean previous builds
echo "🧹 Cleaning previous builds..."
rm -rf dist/
rm -rf node_modules/.vite/

# Install dependencies
echo "📦 Installing dependencies..."
npm ci --production=false

# Run linting and type checking
echo "🔍 Running code quality checks..."
npm run lint || echo "⚠️  Linting warnings found, continuing..."
npm run type-check || echo "⚠️  Type checking warnings found, continuing..."

# Build for production
echo "🏗️  Building for production..."
npm run build:production

# Verify build output
if [ ! -d "dist" ]; then
    echo "❌ Error: Build failed - dist directory not found"
    exit 1
fi

echo "✅ Production build completed successfully!"
echo "📁 Build output is in the 'dist' directory"
echo "🌐 Ready for deployment to production server"

# Optional: Show build size
if command -v du &> /dev/null; then
    echo "📊 Build size: $(du -sh dist | cut -f1)"
fi

echo "🎉 Production deployment preparation complete!"