# gshock_api/exceptions.py

class GShockError(Exception):
    """Base exception for all G-Shock errors."""
    pass

class GShockConnectionError(GShockError):
    """Raised when BLE connection to G-Shock device fails."""    
    pass

class GShockIgnorableException(GShockConnectionError):
    """Raised when BLE connection to G-Shock device fails."""    
    pass
