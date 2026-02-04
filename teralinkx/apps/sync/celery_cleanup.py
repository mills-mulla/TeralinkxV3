# celery_cleanup.py - Add this to your Django management commands

from django.core.management.base import BaseCommand
from celery import current_app
import redis

class Command(BaseCommand):
    help = 'Clean up Celery result backend to prevent memory leaks'

    def handle(self, *args, **options):
        # Connect to Redis
        r = redis.Redis.from_url(current_app.conf.result_backend)
        
        # Clean up expired results
        keys = r.keys('celery-task-meta-*')
        if keys:
            r.delete(*keys)
            self.stdout.write(f'Cleaned up {len(keys)} expired task results')
        
        # Clean up expired groups
        group_keys = r.keys('celery-taskset-meta-*')
        if group_keys:
            r.delete(*group_keys)
            self.stdout.write(f'Cleaned up {len(group_keys)} expired group results')