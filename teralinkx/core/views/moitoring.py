from librouteros import connect
import time
import logging

logging.getLogger("routeros_api").setLevel(logging.WARNING)
logging.getLogger("librouteros").setLevel(logging.WARNING)

API_HOST = '192.168.88.1'
API_USER = 'clientHandler'
API_PASS = 'handling'

def format_bytes(size):
    """Convert bytes to KB, MB, GB, TB, PB with appropriate unit."""
    # Units from Bytes up to Petabytes
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    index = 0
    while size >= 1024 and index < len(units) - 1:
        size /= 1024.0
        index += 1
    return f"{size:.2f} {units[index]}"

# def monitor_user(usermanid):
#     try:
#         api = connect(username=API_USER, password=API_PASS, host=API_HOST)
#         monitor = api(cmd='/user-manager/user/monitor', **{'numbers': usermanid, 'once': ''})
#         for stat in monitor:
#             print(
#                 f"uptime: {stat.get('total-uptime', '')} | "
#                 f"total-download: {format_bytes(int(stat.get('total-download', 0)))} | "
#                 f"total-upload: {format_bytes(int(stat.get('total-upload', 0)))} | "
#                 f"active-sessions: {stat.get('active-sessions', '')}"
#             )
#             return {
#                 'uptime': stat.get('total-uptime', ''),
#                 'total_download': format_bytes(int(stat.get('total-download', 0))),
#                 'total_upload': format_bytes(int(stat.get('total-upload', 0))),
#                 'active_sessions': int(stat.get('active-sessions', 0)),
#             }
#     except Exception as e:
#         logging.error(f"Monitoring failed for {usermanid}: {e}")
#         return None
#     finally:
#         try:
#             api.close()
#         except:
#             pass
import re

def parse_uptime(uptime_str):
    """
    Convert uptime string like '2h23m54s' or '33m11s' to seconds.
    """
    if not uptime_str:
        return 0
    pattern = r'(?:(\d+)h)?(?:(\d+)m)?(?:(\d+)s)?'
    match = re.match(pattern, uptime_str)
    if not match:
        return 0
    hours, minutes, seconds = match.groups()
    total_seconds = (
        int(hours or 0) * 3600 +
        int(minutes or 0) * 60 +
        int(seconds or 0)
    )
    return total_seconds

def monitor_user(usermanid):
    try:
        api = connect(username=API_USER, password=API_PASS, host=API_HOST)
        monitor = api(cmd='/user-manager/user/monitor', **{'numbers': usermanid, 'once': ''})
        for stat in monitor:
            uptime_sec = parse_uptime(stat.get('total-uptime', '0s'))
            total_download = int(stat.get('total-download', 0))
            total_upload = int(stat.get('total-upload', 0))

            return {
                'uptime': uptime_sec,
                'total_download': total_download,
                'total_upload': total_upload,
                'active_sessions': int(stat.get('active-sessions', 0)),
            }
    except Exception as e:
        logging.error(f"Monitoring failed for {usermanid}: {e}")
        return None
    finally:
        try:
            api.close()
        except:
            pass



def get_users():
    try:
        api = connect(username=API_USER, password=API_PASS, host=API_HOST)

        print("Connected to MikroTik RouterOS.")
        users = list(api(cmd='/user-manager/user/print' ,**{'where': 'name="BAL-8C2L5XMTFO6XP"'}))
        # print(users)

        for stat in users:
            userId = stat.get('.id', '')
            userName = stat.get('name', '')
            

            print(
                f"Id: {userId} | Name: {userName} | "
               
            )
            time.sleep(1)  # Adjust interval

    except (OSError, BrokenPipeError) as e:
        print("Connection lost:", e)
    finally:
        try:
            api.close()
            print("Disconnected.")
        except:
            pass


def get_user_by_name(search_name):
    api = connect(username=API_USER, password=API_PASS, host=API_HOST)

    # Fetch only name and id to minimize data
    users = api(
        cmd='/user-manager/user/print',
        **{'.proplist': 'name,.id'}
    )

    for user in users:
        if user.get('name') == search_name:
            user_id = user.get('.id')
            # print(f"Found user: {user}")
            # print(f"id: {user.get('.id')}")
            return user_id
        
    raise ValueError(f"User with name '{search_name}' not found in User Manager")
   

if __name__ == "__main__":
    monitor_user('*10')
    get_users()
    get_user_by_name('BAL-8C2L5XMTFO6XP')
