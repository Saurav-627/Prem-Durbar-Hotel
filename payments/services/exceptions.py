from typing import Dict, Any

class ApplicationError(Exception):
    """Base exception for our application"""

    message: str
    extra: Dict[str, Any]

    def __init__(self, message, extra=None):
        self.message = message
        self.extra = extra or {}
        super().__init__(message)
