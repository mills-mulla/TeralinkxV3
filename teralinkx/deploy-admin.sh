#!/bin/bash

echo "🚀 Deploying TeralinkX Admin Panel..."

# Navigate to admin directory
cd /home/ghost/Desktop/TeralinkxV3/teralinkx/admteralinkx/adminstration

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Build for production
echo "🔨 Building admin panel..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    echo "❌ Build failed - dist directory not found"
    exit 1
fi

# Restart nginx to pick up new files
echo "🔄 Restarting nginx..."
cd /home/ghost/Desktop/TeralinkxV3/teralinkx
docker-compose restart nginx

echo "✅ Admin panel deployed successfully!"
echo "🌐 Access at: https://service.teralinkxwaves.uk/su/"
