# services/client_service.py
from django.contrib.auth.models import User
from django.db import transaction
from rest_framework.authtoken.models import Token
from ..models import ClientH, ClientMAC

class ClientService:

    @staticmethod
    @transaction.atomic
    def create_user_and_client(validated_data):
        """
        Creates a User and corresponding ClientH atomically.
        Returns: (User instance, ClientH instance, is_new_user: bool, auth_token)
        """
        phone = validated_data['phone']
        current_ip = validated_data['current_ip']
        current_mac = validated_data['current_mac']

        user, created = User.objects.get_or_create(
            username=phone,
            defaults={
                'first_name': '',
                'last_name': phone[-4:],
                'email': f"{phone}@teralinkx.net",
            }
        )

        client, ch_created = ClientH.objects.update_or_create(
            user=user,
            defaults={
                'account': phone,
                'current_ip_address': current_ip,
                'status': 'active'
            }
        )

        mac, _ = ClientMAC.objects.update_or_create(
            mac_address=current_mac,
            defaults={
                'ip_address': current_ip,
                'status': 'active'
            }
        )

        if not client.mac_addresses.filter(pk=mac.pk).exists():
            client.mac_addresses.add(mac)

        token, _ = Token.objects.get_or_create(user=user)

        return user, client, (created or ch_created), token.key

    @staticmethod
    def update_mac_address(validated_data, client):
        mac, _ = ClientMAC.objects.update_or_create(
            mac_address=validated_data.get('current_mac'),
            defaults={
                'ip_address': validated_data['current_ip'],
                'status': 'active'
            }
        )

        if not client.mac_addresses.filter(pk=mac.pk).exists():
            client.mac_addresses.add(mac)

        return mac

    @staticmethod
    def update_client_legacy(validated_data):
        """Creates or updates the client record"""
        client, _ = ClientH.objects.update_or_create(
            account=validated_data['phone'],
            defaults={
                'current_ip_address': validated_data['current_ip'],
                'status': 'active'
            }
        )
        return client
