from .util import InvalidUsage

from flask import Flask, jsonify, g

import marketo
import pipedrive


app = Flask(__name__, instance_relative_config=True)
app.config.from_object('config')
app.config.from_pyfile('config.py')  # Override configuration with your own objects

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
        logging.error('Could no create log file with name %s (make sure directory exists)', file_name)
        logging.basicConfig()
        for logger in loggers:
            logger.setLevel(logging.DEBUG)


# Register an error handler to prevent from resulting in an internal server error
@app.errorhandler(InvalidUsage)
def handle_authentication_error(error):
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
        get_logger().warning('Undefined configuration key %s', key)
    return value


def get_logger():
    return app.logger


import sync.views
