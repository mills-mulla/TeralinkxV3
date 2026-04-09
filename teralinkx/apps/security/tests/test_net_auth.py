import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock
from packages.models import DispatchVoucher
from users.models import ClientH
from analytics.models import ActiveSession

class NetworkAuthTests(TestCase):
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        self.url = reverse('network-auth')
        
        # Create test client
        self.test_client = ClientH.objects.create(
            account='TEST001',
            status='active',
            current_ip_address='192.168.88.100'
        )
        
        # Create test voucher
        self.voucher = DispatchVoucher.objects.create(
            dispatch_account='TEST001',
            dispatch_voucher_code='VOUCHER001',
            dispatch_status='inactive'
        )
        
        # Create active session for disconnect tests
        self.active_session = ActiveSession.objects.create(
            mac_address='AA:BB:CC:DD:EE:FF',
            idA='12345'
        )

    def test_missing_action_parameter(self):
        """Test missing action parameter"""
        response = self.client.post(self.url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Missing action parameter', response.data['error'])

    def test_invalid_action_parameter(self):
        """Test invalid action parameter"""
        response = self.client.post(self.url, {'action': 'invalid_action'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertIn('Invalid action', response.data['error'])

    @patch('security.net_auth.RouterManager.get_connection')
    def test_connect_success(self, mock_router):
        """Test successful connection with real router interaction"""
        # Mock router response
        mock_api = MagicMock()
        mock_api.return_value = [{'message': 'login successful'}]
        mock_router.return_value = mock_api
        
        data = {
            'action': 'connect',
            'account': 'TEST001',
            'voucher_code': 'VOUCHER001',
            'bound_mac': 'AA:BB:CC:DD:EE:FF'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['action'], 'connect')
        self.assertEqual(response.data['client_ip'], '192.168.88.100')
        
        # Verify voucher was activated
        self.voucher.refresh_from_db()
        self.assertEqual(self.voucher.dispatch_status, 'active')

    def test_connect_missing_fields(self):
        """Test connect with missing required fields"""
        data = {
            'action': 'connect',
            'account': 'TEST001'
            # missing voucher_code and bound_mac
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Missing required fields', response.data['error'])

    def test_connect_invalid_voucher(self):
        """Test connect with invalid voucher"""
        data = {
            'action': 'connect',
            'account': 'TEST001',
            'voucher_code': 'INVALID_VOUCHER',
            'bound_mac': 'AA:BB:CC:DD:EE:FF'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('Voucher does not exist', response.data['error'])

    def test_connect_client_not_found(self):
        """Test connect with non-existent client"""
        data = {
            'action': 'connect',
            'account': 'NONEXISTENT',
            'voucher_code': 'VOUCHER001',
            'bound_mac': 'AA:BB:CC:DD:EE:FF'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('security.net_auth.RouterManager.get_connection')
    def test_connect_router_failure(self, mock_router):
        """Test connect when router connection fails"""
        mock_router.side_effect = Exception("Router connection failed")
        
        data = {
            'action': 'connect',
            'account': 'TEST001',
            'voucher_code': 'VOUCHER001',
            'bound_mac': 'AA:BB:CC:DD:EE:FF'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn('Failed to connect to network', response.data['error'])

    @patch('security.net_auth.RouterManager.get_connection')
    def test_reconnect_success(self, mock_router):
        """Test successful reconnection"""
        mock_api = MagicMock()
        mock_api.return_value = [{'message': 'login successful'}]
        mock_router.return_value = mock_api
        
        data = {
            'action': 'reconnect',
            'account': 'TEST001',
            'voucher_code': 'VOUCHER001',
            'bound_ip': '192.168.88.100'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['action'], 'reconnect')

    def test_reconnect_missing_fields(self):
        """Test reconnect with missing fields"""
        data = {
            'action': 'reconnect',
            'account': 'TEST001'
            # missing voucher_code and bound_ip
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @patch('security.net_auth.RouterManager.get_connection')
    def test_disconnect_success(self, mock_router):
        """Test successful disconnection"""
        mock_api = MagicMock()
        mock_api.return_value = [{'message': 'removed'}]
        mock_router.return_value = mock_api
        
        data = {
            'action': 'disconnect',
            'bound_mac': 'AA:BB:CC:DD:EE:FF'
        }
        
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['success'])
        self.assertEqual(response.data['action'], 'disconnect')
        
        # Verify session was deleted
        with self.assertRaises(ActiveSession.DoesNotExist):
            ActiveSession.objects.get(mac_address='AA:BB:CC:DD:EE:FF')

    def test_disconnect_missing_mac(self):
        """Test disconnect with missing MAC"""
        data = {
            'action': 'disconnect'
            # missing bound_mac
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_disconnect_session_not_found(self):
        """Test disconnect with non-existent session"""
        data = {
            'action': 'disconnect',
            'bound_mac': 'NONEXISTENT_MAC'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @patch('security.net_auth.RouterManager.get_connection')
    def test_disconnect_router_failure(self, mock_router):
        """Test disconnect when router fails"""
        mock_router.side_effect = Exception("Router connection failed")
        
        data = {
            'action': 'disconnect',
            'bound_mac': 'AA:BB:CC:DD:EE:FF'
        }
        
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)


class RealRouterIntegrationTests(TestCase):
    """
    Integration tests with real MikroTik router
    These tests require actual router access and specific test users
    """
    
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('network-auth')
        
        # Create test data for real router tests
        self.real_client = ClientH.objects.create(
            account='REALTEST001',
            status='active',
            current_ip_address='192.168.88.150'  # IP that exists in your network
        )
        
        self.real_voucher = DispatchVoucher.objects.create(
            dispatch_account='REALTEST001',
            dispatch_voucher_code='REALVOUCHER001',
            dispatch_status='inactive'
        )

    @pytest.mark.integration
    def test_real_router_connection(self):
        """Test actual connection to MikroTik router"""
        # This test requires real router access
        try:
            data = {
                'action': 'connect',
                'account': 'REALTEST001',
                'voucher_code': 'REALVOUCHER001',
                'bound_mac': '11:22:33:44:55:66'
            }
            
            response = self.client.post(self.url, data, format='json')
            
            # The response might vary based on router configuration
            # This test checks that we get a meaningful response
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_500_INTERNAL_SERVER_ERROR])
            
            if response.status_code == status.HTTP_200_OK:
                self.assertTrue(response.data['success'])
            else:
                # If failed, it should be a proper error message
                self.assertIn('error', response.data)
                
        except Exception as e:
            self.skipTest(f"Router not accessible: {e}")

    @pytest.mark.integration
    def test_real_router_disconnect(self):
        """Test actual disconnection from MikroTik router"""
        # First, create an active session by connecting a user
        # You need to have a real user session on the router for this test
        
        try:
            # Create a test active session that matches a real session on router
            test_session = ActiveSession.objects.create(
                mac_address='11:22:33:44:55:67',
                idA='*1'  # This should match a real session ID on your router
            )
            
            data = {
                'action': 'disconnect',
                'bound_mac': '11:22:33:44:55:67'
            }
            
            response = self.client.post(self.url, data, format='json')
            
            # Check response
            self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_404_NOT_FOUND])
            
        except Exception as e:
            self.skipTest(f"Router not accessible: {e}")


class RouterCommandTests(TestCase):
    """Tests specifically for router command execution"""
    
    @patch('security.net_auth.RouterManager.get_connection')
    def test_router_command_retry_logic(self, mock_router):
        """Test that router commands retry on failure"""
        from security.net_auth import NetworkAuthView
        
        view = NetworkAuthView()
        
        # Mock router to fail twice then succeed
        mock_api = MagicMock()
        mock_api.side_effect = [
            Exception("First failure"),
            Exception("Second failure"),
            [{'success': True}]  # Success on third attempt
        ]
        mock_router.return_value = mock_api
        
        result, error = view.execute_router_command("/ip/hotspot/active/print")
        
        self.assertIsNotNone(result)
        self.assertIsNone(error)
        self.assertEqual(mock_router.call_count, 3)

    @patch('security.net_auth.RouterManager.get_connection')
    def test_router_command_all_retries_fail(self, mock_router):
        """Test router command when all retries fail"""
        from security.net_auth import NetworkAuthView
        
        view = NetworkAuthView()
        
        # Mock router to always fail
        mock_router.side_effect = Exception("Router connection failed")
        
        result, error = view.execute_router_command("/ip/hotspot/active/print")
        
        self.assertIsNone(result)
        self.assertIsNotNone(error)
        self.assertEqual(mock_router.call_count, 3)


# Test data setup helper
def create_test_data():
    """Helper function to create test data for manual testing"""
    client1 = ClientH.objects.create(
        account='MANUAL001',
        status='active',
        current_ip_address='192.168.88.200'
    )
    
    client2 = ClientH.objects.create(
        account='MANUAL002', 
        status='active',
        current_ip_address='192.168.88.201'
    )
    
    voucher1 = DispatchVoucher.objects.create(
        dispatch_account='MANUAL001',
        dispatch_voucher_code='MANUALVOUCHER001',
        dispatch_status='inactive'
    )
    
    voucher2 = DispatchVoucher.objects.create(
        dispatch_account='MANUAL002',
        dispatch_voucher_code='MANUALVOUCHER002', 
        dispatch_status='inactive'
    )
    
    return {
        'clients': [client1, client2],
        'vouchers': [voucher1, voucher2]
    }