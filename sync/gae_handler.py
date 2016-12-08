from flask import Flask, jsonify, request


gae_app = Flask(__name__)


@gae_app.route('/task/<string:task_name>', methods=['POST'])
def sync_handler(task_name):
    id_ = int(request.form.get('id'))
    import tasks
    rv = getattr(tasks, task_name)(id_)
    return jsonify(**rv)
