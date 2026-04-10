# apps/finance/throttling.py
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle


class FinanceAPIThrottle(UserRateThrottle):
    rate = '2000/hour'

    def get_cache_key(self, request, view):
        # Use user ID so each user has their own bucket, not shared IP
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class FinanceAnonThrottle(AnonRateThrottle):
    rate = '200/hour'


class PaymentAPIThrottle(UserRateThrottle):
    rate = '1000/hour'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class ExportAPIThrottle(UserRateThrottle):
    rate = '100/hour'

    def get_cache_key(self, request, view):
        if request.user and request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}


class HealthCheckThrottle(AnonRateThrottle):
    rate = '10000/hour'
