import logging

from datetime import datetime
from flask import Flask, jsonify, request
from google.appengine.ext import ndb

from .common import Error
from .util import EnqueuedTask

gae_app = Flask(__name__)


@gae_app.errorhandler(Error)
def handle_internal_server_error(error):
    logging.getLogger('sync').error('%s: %s', error.__class__.__name__, error)
    response = jsonify({
        'status': 'error',
        'message': error.message
    })
    response.status_code = 500
    return response


@gae_app.errorhandler(Exception)
def handle_internal_server_attribute_error(error):
    logging.getLogger('sync').error('%s: %s', error.__class__.__name__, error)
    response = jsonify({
        'status': 'error',
        'message': error.message
    })
    response.status_code = 500
    return response


@gae_app.route('/task/<string:task_name>', methods=['POST'])
def sync_handler(task_name):
    # Get task first in case it is deleted in the app while running
    enqueued_task_key = ndb.Key(EnqueuedTask, request.headers.get('X-AppEngine-TaskName'))
    enqueued_task = enqueued_task_key.get()
    # Acknowledge the task: set its arrival time
    if enqueued_task:
        enqueued_task.ata = datetime.utcnow()
        enqueued_task.put()

    id_ = int(request.form.get('id'))
    import tasks
    rv = getattr(tasks, task_name)(id_)

    # Release the task after completion (= succeeded): remove it from the datastore
    enqueued_task_key.delete()

    return jsonify(**rv)
