from flask import Flask, g
from secret import *

import marketo
import pipedrive


app = Flask(__name__)

if not app.debug:
    import logging
    loggers = [app.logger, logging.getLogger('marketo'),
               logging.getLogger('pipedrive')]
    file_name = '/var/www/sync_app/sync_app.log'
    try:
        file_handler = logging.FileHandler(file_name)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s '
            '[in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.WARNING)
        for logger in loggers:
            logger.addHandler(file_handler)
    except IOError:
        logging.error("Could no create log file with name %s (make sure directory exists)", file_name)
        logging.basicConfig()
        for logger in loggers:
            logger.setLevel(logging.DEBUG)


def create_marketo_client():
    """Creates the Marketo client."""
    return marketo.MarketoClient(IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)


def create_pipedrive_client():
    """Creates the Pipedrive client."""
    return pipedrive.PipedriveClient(PD_API_TOKEN)


def get_marketo_client():
    """Creates a new Marketo client if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'marketo_client'):
        g.marketo_client = create_marketo_client()
    return g.marketo_client


def get_pipedrive_client():
    """Creates a new Pipedrive client if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'pipedrive_client'):
        g.pipedrive_client = create_pipedrive_client()
    return g.pipedrive_client


import sync.views
from .views import create_or_update_company_in_marketo, create_or_update_organization_in_pipedrive  # Export these methods for adapters
