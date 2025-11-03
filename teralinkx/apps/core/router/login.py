from ros_api.api import Api, RouterOSTrapError
def print_verbose_logs(logs):
    for log in logs:
        print(log)
# Initialize the API connection
router = Api('192.168.188.152', user='admin', password='q', port=8728, verbose=True)
hotspotlogin = router.talk('/ip/hotspot/active/print')
print('hotspotlogin:', hotspotlogin)

# Function to print verbose logs

"""
def print_verbose_logs(logs):
    for log in logs:
        print(log)
        
dhcp = router.talk('/ip/dhcp-server/lease/print')
print(dhcp)
# Fetch existing configurations (as examples)
addresses = router.talk(['/ip/address/print'])
print('addresses:',addresses)

services = router.talk(['/ip/service/print'])
print('services',services)

hotspot = router.talk(['/ip/hotspot/print'])
print('servers;',hotspot)

hotspot_users = router.talk(['/ip/hotspot/user/print'])
print('clients:',hotspot_users)

# Add a new user profile

add_profile_command = [
    '/ip/hotspot/user/profile/add',
    '=name=beast',
    '=rate-limit=512k/512k',
    '=shared-users=1'
]

try:
    add_profile_response = router.talk('/ip/hotspot/user/profile/add =name=beast2 =rate-limit=1200k/256k =shared-users=1')   
    print("Profile added successfully:", add_profile_response)
    print_verbose_logs(add_profile_response)
except RouterOSTrapError as e:
    print("Failed to add profile:", e)

# Fetch the updated list of user profiles
hotspot_profiles = router.talk(['/ip/hotspot/user/profile/print'])
print('profiles:',hotspot_profiles)

#addurs = router.talk('/ip/hotspot/user/add =name=mans')
sysidentity = router.talk(['/system/identity/print'])
print('system:',sysidentity)


# Generate Vouchers
# Example: Generate a single voucher
voucher_response = api.get_resource('/tool/user-manager/user').add(
    customer='admin',
    username='user1',
    password='password1',
    profile='profile1'
)

# Extract voucher information
voucher_code = voucher_response.get('voucher')
voucher_attributes = {
    'username': 'user1',
    'password': 'password1',
    'profile': 'profile1',
    # Add additional attributes as needed
}

# Store Vouchers in Online Database
# Example: Send voucher data to a RESTful API
database_api_url = 'https://your-database-api.com/vouchers'
response = requests.post(database_api_url, json=voucher_attributes)

# Check response status
if response.status_code == 200:
    print("Voucher stored successfully in the database.")
else:
    print("Failed to store voucher in the database.")

# Disconnect from the Router
connection.disconnect()


"""
"""
# Function to generate vouchers in batch
def generate_vouchers(api, profile_name, count):
    vouchers = []
    for i in range(count):
        # Generate voucher
        voucher_response = api.get_resource('/tool/user-manager/user').add(
            customer='admin',
            username=f'user{i+1}',
            password=f'password{i+1}',
            profile=profile_name
        )
        # Extract voucher information
        voucher_code = voucher_response.get('voucher')
        voucher_attributes = {
            'username': f'user{i+1}',
            'password': f'password{i+1}',
            'profile': profile_name,
            # Add additional attributes as needed
        }
        vouchers.append(voucher_attributes)
    return vouchers

# Connect to the Router
connection = routeros_api.RouterOsApiPool(
    host='router_ip',
    username='admin',
    password='',
    port=8728,
    use_ssl=False,
    ssl_verify=False
)
api = connection.get_api()

# Generate Batch of Vouchers
profile_name = 'profile1'
voucher_count = 10  # Specify the number of vouchers to generate
vouchers = generate_vouchers(api, profile_name, voucher_count)

# Store Vouchers in Online Database
database_api_url = 'https://your-database-api.com/vouchers'
response = requests.post(database_api_url, json=vouchers)

# Check response status
if response.status_code == 200:
    print(f"{voucher_count} vouchers for profile '{profile_name}' stored successfully in the database.")
else:
    print("Failed to store vouchers in the database.")

# Disconnect from the Router
connection.disconnect()


"""