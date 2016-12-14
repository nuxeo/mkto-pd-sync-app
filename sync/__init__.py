import logging

from flask import Flask, jsonify, g

import marketo
import pipedrive
from .util import InvalidUsage

app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')  # Override configuration with your own objects


# Register an error handler to prevent from resulting in an internal server error
@app.errorhandler(InvalidUsage)
def handle_authentication_error(error):
    get_logger().error(error.message)
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.errorhandler(Exception)
def handle_internal_server_error(error):
    get_logger().error('%s: %s', error.__class__.__name__, error)
    response = jsonify({
        'status': 'error',
        'message': error.message
    })
    response.status_code = 500
    return response


def create_marketo_client():
    """Creates the Marketo client."""
    return marketo.MarketoClient(get_config('IDENTITY_ENDPOINT'), get_config('CLIENT_ID'),
                                 get_config('CLIENT_SECRET'), get_config('API_ENDPOINT'))


def create_pipedrive_client():
    """Creates the Pipedrive client."""
    return pipedrive.PipedriveClient(get_config('PD_API_TOKEN'))


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


def get_config(key):
    value = None
    try:
        value = app.config[key]
    except KeyError:
        get_logger().warning('Undefined configuration key=%s', key)
    return value


def get_logger():
    return app.logger


def create_logging_handler(testing_mode):
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s %(name)-24s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    if not testing_mode:
        handler.setLevel(logging.INFO)
    else:
        handler.setLevel(logging.DEBUG)
    return handler


get_logger().setLevel(
    logging.DEBUG)  # Set app logger level to the lowest to be able to configure an equal or higher level on module handlers

loggers = [(logging.getLogger('sync.marketo'), get_config('MARKETO_TESTING')),
           (logging.getLogger('sync.pipedrive'), get_config('PIPEDRIVE_TESTING'))]
for logger in loggers:
    logger[0].addHandler(create_logging_handler(logger[1]))
if not app.debug:
    get_logger().addHandler(create_logging_handler(get_config('TESTING')))

import sync.views
