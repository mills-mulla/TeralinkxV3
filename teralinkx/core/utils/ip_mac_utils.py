from teralinkx.core.models import DHCPLease

def resolve_mac_from_ip(ip):
    lease = DHCPLease.objects.filter(active_address=ip).first()
    return lease.active_mac_address if lease else None