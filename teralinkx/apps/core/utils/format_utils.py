from datetime import timedelta
import re

def format_bytes(size):
    power = 1024
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    n = 0
    while size >= power and n < len(units) - 1:
        size /= power
        n += 1
    return f"{size:.2f} {units[n]}"

def parse_duration(duration_str):
    duration_str = duration_str.lower().strip()
    day_match = re.match(r'(\d+)\s*days?', duration_str)
    if day_match:
        return timedelta(days=int(day_match.group(1)))
    try:
        h, m, s = map(int, duration_str.split(':'))
        return timedelta(hours=h, minutes=m, seconds=s)
    except ValueError:
        return None