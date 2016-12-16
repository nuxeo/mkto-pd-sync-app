import logging

from .client import PipedriveClient
from .resources import Deal
from .resources import Organization
from .resources import Person
from .resources import Pipeline
from .resources import User
from .resources import Activity

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
logging.getLogger(__name__).propagate = False  # Allow single module loggin configuration
