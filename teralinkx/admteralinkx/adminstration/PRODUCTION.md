# Production Deployment Guide

## Performance Optimizations Applied

### 1. Build Optimizations
- ✅ Code splitting with manual chunks (vue-vendor, charts, utils)
- ✅ Terser minification with console removal
- ✅ Gzip and Brotli compression
- ✅ CSS code splitting
- ✅ Tree shaking enabled
- ✅ Source maps disabled in production

### 2. Runtime Optimizations
- ✅ Request caching (60s TTL)
- ✅ Lazy loading for all routes
- ✅ Component lazy loading
- ✅ Image lazy loading
- ✅ Reduced motion support
- ✅ Font smoothing
- ✅ Smooth scrolling

### 3. API Optimizations
- ✅ Request deduplication
- ✅ Response caching
- ✅ Automatic cache cleanup
- ✅ Silent error handling in production

### 4. Bundle Size
- Vue vendor chunk: ~150KB (gzipped)
- Charts chunk: ~80KB (gzipped)
- Utils chunk: ~40KB (gzipped)
- Main app: ~60KB (gzipped)

## Build for Production

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Or use the build script
./build-prod.sh

# Preview production build
npm run preview
```

## Deployment Steps

### Option 1: Nginx (Recommended)

1. Build the application:
```bash
npm run build
```

2. Copy nginx configuration:
```bash
sudo cp nginx.conf /etc/nginx/sites-available/teralinkx-admin
sudo ln -s /etc/nginx/sites-available/teralinkx-admin /etc/nginx/sites-enabled/
```

3. Deploy files:
```bash
sudo mkdir -p /var/www/teralinkx-admin
sudo cp -r dist/* /var/www/teralinkx-admin/
```

4. Restart nginx:
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Option 2: Docker

```dockerfile
FROM nginx:alpine
COPY dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

Build and run:
```bash
docker build -t teralinkx-admin .
docker run -d -p 80:80 teralinkx-admin
```

### Option 3: Static Hosting (Vercel/Netlify)

```bash
npm run build
# Upload dist/ folder to your hosting provider
```

## Performance Targets

- First Contentful Paint (FCP): < 1.8s
- Largest Contentful Paint (LCP): < 2.5s
- Time to Interactive (TTI): < 3.8s
- Cumulative Layout Shift (CLS): < 0.1
- First Input Delay (FID): < 100ms

## Monitoring

The app includes built-in performance monitoring. Check browser console in development mode for metrics.

## Environment Variables

Create `.env.production`:
```
VITE_SUAPI_HTTPS_URL=https://service.teralinkxwaves.uk
NODE_ENV=production
```

## Security Checklist

- ✅ HTTPS enabled
- ✅ Security headers configured
- ✅ XSS protection enabled
- ✅ CSRF tokens implemented
- ✅ JWT authentication
- ✅ API rate limiting
- ✅ Input validation

## Browser Support

- Chrome/Edge: Last 2 versions
- Firefox: Last 2 versions
- Safari: Last 2 versions
- Mobile browsers: iOS Safari 12+, Chrome Android

## Troubleshooting

### Build fails
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Large bundle size
Check bundle analysis:
```bash
npm run build -- --mode analyze
```

### Slow API responses
- Check network tab in DevTools
- Verify API caching is working
- Check backend performance

## Support

For issues, contact the development team or check the main README.md
