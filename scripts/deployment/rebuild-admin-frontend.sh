#!/bin/bash

echo "🔧 Rebuilding Admin Frontend..."

cd /home/ghost/Desktop/TeralinkxV3/teralinkx/admteralinkx/adminstration

echo "📦 Installing dependencies..."
npm install

echo "🏗️ Building production bundle..."
npm run build

echo "✅ Frontend rebuilt successfully!"
echo "🌐 Access at: https://su.teralinkxwaves.uk"
