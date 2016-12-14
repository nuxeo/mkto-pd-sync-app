from flask import Flask, jsonify, request
from google.appengine.ext import ndb

gae_app = Flask(__name__)


@gae_app.route('/task/<string:task_name>', methods=['POST'])
def sync_handler(task_name):
    id_ = int(request.form.get('id'))
    import tasks
    rv = getattr(tasks, task_name)(id_)

    # "Dequeue" task after processing (succeeded)
    enqueued_task = ndb.Key(urlsafe=request.form.get('task_urlsafe')).get()
    enqueued_task.key.delete()

    return jsonify(**rv)
