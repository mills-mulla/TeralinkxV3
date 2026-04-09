class BusinessLogicError(Exception):
    """Raised when business logic validation fails"""
    pass

class AuthenticationError(Exception):
    """Raised when authentication fails"""
    pass

class DeviceConflictError(Exception):
    """Raised when device ownership conflict occurs"""
    pass

class LocationDetectionError(Exception):
    """Raised when location detection fails"""
    pass