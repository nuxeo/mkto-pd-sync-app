from .util import InvalidUsage

from flask import Flask, jsonify, g


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
