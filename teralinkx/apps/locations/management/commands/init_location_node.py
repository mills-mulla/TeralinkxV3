"""
Management command to initialize a multi-location node
Usage: python manage.py init_location_node --role central --node-id central
       python manage.py init_location_node --role location --node-id nairobi --location-name \"Nairobi Branch\"
"""

import os
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from apps.locations.models import Location, NodeIdentity


class Command(BaseCommand):
    help = 'Initialize multi-location node identity and configuration'

    def add_arguments(self, parser):
        parser.add_argument(
            '--role',
            type=str,
            choices=['central', 'location'],
            required=True,
            help='Node role: central or location'
        )
        parser.add_argument(
            '--node-id',
            type=str,
            required=True,
            help='Unique node identifier (e.g., central, nairobi, mombasa)'
        )
        parser.add_argument(
            '--location-name',
            type=str,
            help='Location name (required for location nodes)'
        )
        parser.add_argument(
            '--location-code',
            type=str,
            help='Location code (auto-generated if not provided)'
        )
        parser.add_argument(
            '--central-url',
            type=str,
            help='Central server API URL (required for location nodes)'
        )
        parser.add_argument(
            '--router-ip',
            type=str,
            default='192.168.88.1',
            help='Router IP address'
        )
        parser.add_argument(
            '--router-username',
            type=str,
            default='admin',
            help='Router username'
        )
        parser.add_argument(
            '--router-password',
            type=str,
            default='password',
            help='Router password'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force initialization even if node already exists'
        )

    def handle(self, *args, **options):
        role = options['role']
        node_id = options['node_id']
        location_name = options.get('location_name')
        location_code = options.get('location_code')
        central_url = options.get('central_url')
        router_ip = options['router_ip']
        router_username = options['router_username']
        router_password = options['router_password']
        force = options['force']

        self.stdout.write(f\"Initializing {role} node: {node_id}\")\n\n        # Validate inputs\n        if role == 'location' and not location_name:\n            raise CommandError(\"--location-name is required for location nodes\")\n        \n        if role == 'location' and not central_url:\n            raise CommandError(\"--central-url is required for location nodes\")\n\n        # Check if node already exists\n        existing_node = NodeIdentity.objects.filter(node_id=node_id).first()\n        if existing_node and not force:\n            raise CommandError(\n                f\"Node {node_id} already exists. Use --force to reinitialize.\"\n            )\n\n        try:\n            # Create or update location\n            location = None\n            if role == 'location':\n                location = self._create_or_update_location(\n                    location_name, location_code, node_id, router_ip, \n                    router_username, router_password\n                )\n            elif role == 'central':\n                # For central node, create a central location if it doesn't exist\n                location = self._create_or_update_central_location(node_id)\n\n            # Create or update node identity\n            node_identity = self._create_or_update_node_identity(\n                role, node_id, location, central_url, existing_node\n            )\n\n            # Update environment variables\n            self._update_environment_variables(role, node_id, central_url)\n\n            # Initialize sync configuration\n            self._initialize_sync_configuration(location)\n\n            self.stdout.write(\n                self.style.SUCCESS(\n                    f\"Successfully initialized {role} node '{node_id}'\"\n                )\n            )\n            \n            if location:\n                self.stdout.write(f\"Location: {location.name} ({location.code})\")\n            \n            self.stdout.write(f\"Node ID: {node_identity.node_id}\")\n            self.stdout.write(f\"Role: {node_identity.role}\")\n            \n            if role == 'location':\n                self.stdout.write(f\"Central URL: {node_identity.central_api_url}\")\n                self.stdout.write(f\"Router IP: {router_ip}\")\n\n        except Exception as e:\n            raise CommandError(f\"Failed to initialize node: {str(e)}\")\n\n    def _create_or_update_location(self, name, code, node_id, router_ip, username, password):\n        \"\"\"Create or update location\"\"\"\n        \n        # Generate code if not provided\n        if not code:\n            code = f\"LOC-{node_id.upper()}\"\n        \n        # Router configuration\n        router_config = {\n            'host': router_ip,\n            'username': username,\n            'password': password,\n            'port': 8728,\n            'ssl': False,\n            'webfig_url': f'http://{router_ip}',\n            'webfig_port': 80\n        }\n        \n        location, created = Location.objects.update_or_create(\n            node_id=node_id,\n            defaults={\n                'name': name,\n                'code': code,\n                'location_type': 'branch',\n                'router_ip': router_ip,\n                'router_config': router_config,\n                'is_active': True,\n                'allow_roaming_in': True,\n                'allow_roaming_out': True,\n                'offline_operation_enabled': True,\n                'offline_credit_limit': 500.00,  # KES 500 offline limit\n            }\n        )\n        \n        action = \"Created\" if created else \"Updated\"\n        self.stdout.write(f\"{action} location: {location.name}\")\n        \n        return location\n\n    def _create_or_update_central_location(self, node_id):\n        \"\"\"Create or update central location\"\"\"\n        location, created = Location.objects.update_or_create(\n            node_id=node_id,\n            defaults={\n                'name': 'Central Server',\n                'code': 'CENTRAL',\n                'location_type': 'headquarters',\n                'is_central': True,\n                'is_active': True,\n                'allow_roaming_in': True,\n                'allow_roaming_out': True,\n            }\n        )\n        \n        action = \"Created\" if created else \"Updated\"\n        self.stdout.write(f\"{action} central location: {location.name}\")\n        \n        return location\n\n    def _create_or_update_node_identity(self, role, node_id, location, central_url, existing_node):\n        \"\"\"Create or update node identity\"\"\"\n        \n        defaults = {\n            'role': role,\n            'location': location,\n            'is_registered': False,\n        }\n        \n        if role == 'location' and central_url:\n            defaults['central_api_url'] = central_url\n        \n        if existing_node:\n            # Update existing node\n            for key, value in defaults.items():\n                setattr(existing_node, key, value)\n            existing_node.save()\n            node_identity = existing_node\n            self.stdout.write(\"Updated existing node identity\")\n        else:\n            # Create new node\n            node_identity = NodeIdentity.objects.create(\n                node_id=node_id,\n                **defaults\n            )\n            self.stdout.write(\"Created new node identity\")\n        \n        return node_identity\n\n    def _update_environment_variables(self, role, node_id, central_url):\n        \"\"\"Update environment variables\"\"\"\n        env_file = os.path.join(settings.BASE_DIR, '.env')\n        \n        env_updates = {\n            'NODE_ROLE': role,\n            'NODE_ID': node_id,\n        }\n        \n        if role == 'location' and central_url:\n            env_updates['CENTRAL_API_URL'] = central_url\n        \n        # Read existing .env file\n        env_content = {}\n        if os.path.exists(env_file):\n            with open(env_file, 'r') as f:\n                for line in f:\n                    line = line.strip()\n                    if line and '=' in line and not line.startswith('#'):\n                        key, value = line.split('=', 1)\n                        env_content[key] = value\n        \n        # Update with new values\n        env_content.update(env_updates)\n        \n        # Write back to .env file\n        with open(env_file, 'w') as f:\n            for key, value in env_content.items():\n                f.write(f\"{key}={value}\\n\")\n        \n        self.stdout.write(\"Updated .env file with node configuration\")\n\n    def _initialize_sync_configuration(self, location):\n        \"\"\"Initialize sync configuration for the location\"\"\"\n        if not location:\n            return\n        \n        from apps.sync.models import SyncConfiguration\n        \n        sync_config, created = SyncConfiguration.objects.get_or_create(\n            location=location,\n            defaults={\n                'voucher_sync_interval': 5,\n                'user_sync_interval': 10,\n                'session_sync_interval': 2,\n                'transaction_sync_interval': 15,\n                'keep_sync_logs_days': 30,\n                'max_sync_retries': 3,\n                'max_sync_size_mb': 50,\n                'sync_batch_size': 100,\n                'timeout_seconds': 30,\n                'auto_sync_enabled': True,\n                'compression_enabled': True,\n                'encryption_enabled': True,\n                'conflict_resolution': 'newer_wins',\n            }\n        )\n        \n        action = \"Created\" if created else \"Found existing\"\n        self.stdout.write(f\"{action} sync configuration\")