import logging

from .client import MarketoClient
from .helpers import compute_external_id
from .entities import Company
from .entities import Lead
from .entities import Opportunity
from .entities import Role

# Set default logging handler to avoid "No handler found" warnings.
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())

# Disable propagation of logged events to allow module level configuration.
logging.getLogger(__name__).propagate = False
