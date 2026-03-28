#!/bin/bash

# MikroTik Hotspot Deployment Script
# This script builds the Vue app for MikroTik hotspot deployment

echo "🚀 Building TeralinkX for MikroTik Hotspot..."

# Build for hotspot environment
npm run build:hotspot

# Check if build was successful
if [ $? -eq 0 ]; then
    echo "✅ Build successful!"
    echo "📁 Files are in: hotspot-dist/"
    echo ""
    echo "📋 Deployment Instructions:"
    echo "1. Copy all files from hotspot-dist/ to your MikroTik hotspot folder"
    echo "2. Ensure login.html redirects to index.html#/"
    echo "3. Update your backend URL in .env.hotspot if needed"
    echo "4. Test the hotspot login flow"
    echo ""
    echo "🔧 MikroTik Configuration:"
    echo "- Use hash routing (already configured)"
    echo "- IP/MAC variables will be processed by MikroTik"
    echo "- Backend API calls will go to: $(grep VITE_API_BASE_URL .env.hotspot | cut -d'=' -f2)"
else
    echo "❌ Build failed!"
    exit 1
fi