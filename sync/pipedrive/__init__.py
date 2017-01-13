import logging

from .client import PipedriveClient
from .entities import Deal
from .entities import Organization
from .entities import Person
from .entities import Pipeline
from .entities import User
from .entities import Activity

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
