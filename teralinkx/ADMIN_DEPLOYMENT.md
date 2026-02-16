# Admin Panel Deployment Guide

## Quick Deploy

```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx
./deploy-admin.sh
```

## Manual Steps

### 1. Build Admin Panel
```bash
cd admteralinkx/adminstration
npm install
npm run build
```

### 2. Restart Docker Stack
```bash
cd /home/ghost/Desktop/TeralinkxV3/teralinkx
docker-compose restart nginx
```

### 3. Access Admin Panel
- URL: https://service.teralinkxwaves.uk/su/
- Backend API: https://service.teralinkxwaves.uk/suapi/

## Architecture

```
service.teralinkxwaves.uk
├── /                    → Client Frontend (Vue)
├── /su/                 → Admin Panel (Vue) ✨ NEW
├── /api/                → Client API
├── /suapi/              → Admin API
├── /admin/              → Django Admin
├── /static/             → Static files
└── /media/              → Media files
```

## Docker Stack

- **nginx**: Serves admin panel + proxies API
- **web**: Django backend (port 8009)
- **celery**: Background tasks
- **redis**: Cache & broker
- **postgres**: Database
- **freeradius**: RADIUS server

## Troubleshooting

### Admin panel not loading
```bash
# Check nginx logs
docker logs teralinkx_nginx

# Verify dist exists
ls -la admteralinkx/adminstration/dist/

# Rebuild
cd admteralinkx/adminstration
npm run build
docker-compose restart nginx
```

### API connection issues
- Check `.env.production` has correct API URL
- Verify CORS settings in Django backend
- Check nginx proxy configuration

## Performance

- Gzip compression enabled
- Static assets cached for 1 year
- Code splitting active
- Lazy route loading
