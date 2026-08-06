import sys

from .api import channel_manager_sync
from .checkout import checkout_page
from .rooms import create_booking
from .zipline import create_zipline_booking

# Export module-like object to maintain complete backward compatibility for `from .views import booking`
booking = sys.modules[__name__]

__all__ = [
    'booking',
    'channel_manager_sync',
    'checkout_page',
    'create_booking',
    'create_zipline_booking',
]
