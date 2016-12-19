import logging

from .client import MarketoClient
from .helpers import compute_external_id
from .resources import Company
from .resources import Lead
from .resources import Opportunity
from .resources import Role

try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
logging.getLogger(__name__).propagate = False  # Allow single module logging configuration
