from flask import Flask, g, jsonify, request

import marketo
import pipedrive


gae_app = Flask(__name__, instance_relative_config=True)
# FIXME config should come from app
gae_app.config.from_object('config')
gae_app.config.from_pyfile('config.py')  # Override configuration with your own objects


def create_marketo_client():
    """Creates the Marketo client."""
    return marketo.MarketoClient(get_gae_config('IDENTITY_ENDPOINT'), get_gae_config('CLIENT_ID'),
                                 get_gae_config('CLIENT_SECRET'), get_gae_config('API_ENDPOINT'))


def create_pipedrive_client():
    """Creates the Pipedrive client."""
    return pipedrive.PipedriveClient(get_gae_config('PD_API_TOKEN'))


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


def get_gae_config(key):
    value = None
    try:
        value = gae_app.config[key]
    except KeyError:
        get_gae_logger().warning('Undefined configuration key %s', key)
    return value


def get_gae_logger():
    return gae_app.logger


@gae_app.route('/task/<string:task_name>', methods=['POST'])
def sync_handler(task_name):
    id_ = int(request.form.get('id'))
    import tasks
    rv = getattr(tasks, task_name)(id_)
    return jsonify(**rv)
