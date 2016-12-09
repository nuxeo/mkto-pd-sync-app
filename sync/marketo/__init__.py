from .client import MarketoClient
from .helpers import compute_external_id, get_id_part_from_external
from .resources import Lead
from .resources import Opportunity
from .resources import Role
from .resources import Company


# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
logging.getLogger(__name__).propagate = False  # Allow single module logging configuration
