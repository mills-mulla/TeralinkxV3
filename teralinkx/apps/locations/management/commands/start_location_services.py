"""
Management command to start multi-location services
Usage: python manage.py start_location_services
"""

import asyncio
import signal
import sys
from django.core.management.base import BaseCommand
from django.conf import settings

from apps.locations.models import NodeIdentity
from apps.locations.sync_services import sync_service
from apps.locations.health_monitor import health_monitor


class Command(BaseCommand):
    help = 'Start multi-location services (sync, health monitoring, etc.)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--sync-only',
            action='store_true',
            help='Start only sync services'
        )
        parser.add_argument(
            '--health-only',
            action='store_true',
            help='Start only health monitoring'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Enable debug logging'
        )

    def handle(self, *args, **options):
        sync_only = options['sync_only']
        health_only = options['health_only']
        debug = options['debug']

        # Configure logging
        if debug:
            import logging
            logging.basicConfig(level=logging.DEBUG)

        # Check if node is initialized
        node_identity = NodeIdentity.get_current_node()
        if not node_identity:
            self.stdout.write(
                self.style.ERROR(
                    \"Node not initialized. Run 'python manage.py init_location_node' first.\"\n                )\n            )\n            return\n\n        self.stdout.write(\n            self.style.SUCCESS(\n                f\"Starting services for {node_identity.role} node: {node_identity.node_id}\"\n            )\n        )\n\n        # Setup signal handlers for graceful shutdown\n        def signal_handler(signum, frame):\n            self.stdout.write(\"\\nReceived shutdown signal. Stopping services...\")\n            sys.exit(0)\n\n        signal.signal(signal.SIGINT, signal_handler)\n        signal.signal(signal.SIGTERM, signal_handler)\n\n        # Start services\n        try:\n            asyncio.run(self._start_services(sync_only, health_only))\n        except KeyboardInterrupt:\n            self.stdout.write(\"\\nServices stopped.\")\n        except Exception as e:\n            self.stdout.write(\n                self.style.ERROR(f\"Failed to start services: {str(e)}\")\n            )\n\n    async def _start_services(self, sync_only, health_only):\n        \"\"\"Start the appropriate services\"\"\"\n        tasks = []\n\n        if not health_only:\n            # Start sync services\n            self.stdout.write(\"Starting sync services...\")\n            tasks.append(asyncio.create_task(sync_service.start_sync_worker()))\n\n        if not sync_only:\n            # Start health monitoring\n            self.stdout.write(\"Starting health monitoring...\")\n            tasks.append(asyncio.create_task(health_monitor.start_monitoring()))\n\n        if not tasks:\n            self.stdout.write(\n                self.style.ERROR(\"No services to start. Check your options.\")\n            )\n            return\n\n        self.stdout.write(\n            self.style.SUCCESS(\n                f\"All services started. Running {len(tasks)} background tasks.\"\n            )\n        )\n        self.stdout.write(\"Press Ctrl+C to stop services.\")\n\n        # Wait for all tasks to complete (they run indefinitely)\n        try:\n            await asyncio.gather(*tasks)\n        except asyncio.CancelledError:\n            self.stdout.write(\"Services cancelled.\")\n        except Exception as e:\n            self.stdout.write(\n                self.style.ERROR(f\"Service error: {str(e)}\")\n            )