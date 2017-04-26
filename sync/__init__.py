import logging
import os

from flask import Flask, jsonify, g

import marketo
import pipedrive
from .util import InvalidUsage

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
if not os.getenv('SERVER_SOFTWARE', '').startswith('Google App Engine/'):
    app.config.from_pyfile('config.py', silent=True)  # Override configuration with your own objects

# Register error handlers to prevent from resulting in internal server errors
@app.errorhandler(InvalidUsage)
def handle_authentication_error(error):
    app.logger.error(error.message)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def create_marketo_client():
    """Create the Marketo client."""
    return marketo.MarketoClient(app.config['IDENTITY_ENDPOINT'], app.config['CLIENT_ID'],
                                 app.config['CLIENT_SECRET'], app.config['API_ENDPOINT'])


def create_pipedrive_client():
    """Create the Pipedrive client."""
    return pipedrive.PipedriveClient(app.config['PD_API_TOKEN'])


def get_marketo_client():
    """Create a new Marketo client if there is none yet for the current application context."""
    if not hasattr(g, 'marketo_client'):
        g.marketo_client = create_marketo_client()
    return g.marketo_client


def get_pipedrive_client():
    """Create a new Pipedrive client if there is none yet for the current application context."""
    if not hasattr(g, 'pipedrive_client'):
        g.pipedrive_client = create_pipedrive_client()
    return g.pipedrive_client

if not app.config['TESTING']:
    app.logger.setLevel(logging.INFO)
else:
    app.logger.setLevel(logging.DEBUG)
if not app.debug:
    if app.config['TESTING']:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(name)-24s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        handler.setLevel(logging.DEBUG)
        app.logger.addHandler(handler)

import sync.views
