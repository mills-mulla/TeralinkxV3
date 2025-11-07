import random
import string
from core.router.ros_api.api import Api, RouterOSTrapError

def generate_voucher(prefix, length):
    if length <= len(prefix):
        raise ValueError("Total length must be greater than the length of the prefix")

    allowed_chars = string.ascii_uppercase + string.digits
    random_part_length = length - len(prefix)
    random_part = ''.join(random.choices(allowed_chars, k=random_part_length))

    voucher_code = f"{prefix}-{random_part}"
    #print(f"Voucher Generated: {voucher_code}")
    
    return voucher_code

def parse_devices(devices_str: str) -> int:
    """
    Convert '1 device' or '2 devices' into an integer.
    Defaults to 1 if parsing fails.
    """
    try:
        return int(devices_str.split()[0])  # take the first word and convert to int
    except (ValueError, AttributeError, IndexError):
        return 1  # fallback to 1 if something unexpected

def activate_voucher(prefix, profile, devices):
    """
    Activate voucher in User Manager with shared-users = devices.
    devices can be a string like '1 device', '2 devices'.
    """
    voucher = generate_voucher(prefix, length=16)

    # Convert string like "2 devices" → 2
    device_count = str(parse_devices(devices))

    try:
        router = Api('192.168.88.1', user='admin', password='q', port=8728, verbose=True)

        # Create voucher user with shared-users set dynamically
        activate = router.talk('/user-manager/user/add =name=' + voucher + ' =shared-users=' + device_count) 
        print(f"Activate Response: {activate}")

        set_prof = router.talk('/user-manager/user-profile/add =user=' + voucher + ' =profile=' + profile)
        print(f"Set Profile Response: {set_prof}")
      

        print(f"Voucher {voucher} activated successfully for {device_count} device(s).")
        return {"voucher_code": voucher, "status": "activated", "devices": device_count}

    except Exception as e:
        print(f"Error activating voucher: {e}")
        return {"voucher_code": voucher, "status": "failed", "error": str(e)}



