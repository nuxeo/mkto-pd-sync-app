from datetime import datetime
from flask import Flask, jsonify, request
from google.appengine.ext import ndb

gae_app = Flask(__name__)


@gae_app.route('/task/<string:task_name>', methods=['POST'])
def sync_handler(task_name):
    # Get task first in case it is deleted in the app while running
    enqueued_task_key = ndb.Key(urlsafe=request.form.get('task_urlsafe'))
    enqueued_task = enqueued_task_key.get()
    # Acknowledge the task: set its arrival time
    enqueued_task.ata = datetime.utcnow()
    enqueued_task.put()

    id_ = int(request.form.get('id'))
    import tasks
    rv = getattr(tasks, task_name)(id_)

    # Release the task after completion (= succeeded): remove it from the datastore
    enqueued_task_key.delete()

    return jsonify(**rv)
