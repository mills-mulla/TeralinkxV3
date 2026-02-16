#!/bin/bash

echo "🚀 Building TeralinkX Admin for Production..."

# Clean previous builds
rm -rf dist

# Build with production optimizations
npm run build

# Check build size
echo "📊 Build Size Analysis:"
du -sh dist/
du -sh dist/assets/

echo "✅ Production build complete!"
echo "📦 Files are ready in the 'dist' directory"
echo "🌐 Deploy with: npm run preview"
