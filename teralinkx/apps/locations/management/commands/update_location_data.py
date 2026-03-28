"""
Data migration script to update existing Location records with new fields
Run this after the schema migration
"""

from django.core.management.base import BaseCommand
from apps.locations.models import Location
import uuid


class Command(BaseCommand):
    help = 'Update existing Location records with new multi-location fields'

    def handle(self, *args, **options):
        self.stdout.write("Updating existing Location records...")
        
        updated_count = 0
        for location in Location.objects.all():
            # Generate node_id if missing
            if not location.node_id:
                if location.code:
                    location.node_id = location.code.lower().replace('-', '_')
                else:
                    location.node_id = f"node_{uuid.uuid4().hex[:6]}"
                
                # Ensure uniqueness
                base_node_id = location.node_id
                counter = 1
                while Location.objects.filter(node_id=location.node_id).exclude(pk=location.pk).exists():
                    location.node_id = f"{base_node_id}_{counter}"
                    counter += 1
                
                location.save()
                updated_count += 1
                self.stdout.write(f"Updated {location.name}: node_id = {location.node_id}")
        
        self.stdout.write(
            self.style.SUCCESS(f"Successfully updated {updated_count} location records")
        )