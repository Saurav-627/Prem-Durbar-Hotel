import sys
from .rooms import create_booking
from .zipline import create_zipline_booking
from .checkout import checkout_page
from .api import channel_manager_sync

# Export module-like object to maintain complete backward compatibility for `from .views import booking`
booking = sys.modules[__name__]

__all__ = [
    'create_booking',
    'create_zipline_booking',
    'checkout_page',
    'channel_manager_sync',
    'booking',
]
