from flask import jsonify, request
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

from sync import app
from .util import authenticate, EnqueuedTask


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_lead(lead_id):
    rv = enqueue_task('create_or_update_person_in_pipedrive', {'id': lead_id})
    return jsonify(**rv)


@app.route('/marketo/lead/<int:lead_pipedrive_id>/delete', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_lead_delete(lead_pipedrive_id):
    rv = enqueue_task('delete_person_in_pipedrive', {'id': lead_pipedrive_id})
    return jsonify(**rv)


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_person(person_id):
    rv = enqueue_task('create_or_update_lead_in_marketo', {'id': person_id})
    return jsonify(**rv)


@app.route('/pipedrive/person', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_person_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            person_id = int(params['current']['id'])
            rv = enqueue_task('create_or_update_lead_in_marketo', {'id': person_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            app.logger.error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@app.route('/pipedrive/person/<int:person_marketo_id>/delete', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_person_delete(person_marketo_id):
    rv = enqueue_task('delete_lead_in_marketo', {'id': person_marketo_id})
    return jsonify(**rv)


@app.route('/pipedrive/person/delete', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_person_delete_with_params():
    params = request.get_json()
    # 9a9714c55a34f5faf2956584040ca245b7ab641b = marketo id hash key
    if params is not None and 'previous' in params \
            and '9a9714c55a34f5faf2956584040ca245b7ab641b' in params['previous'] \
            and params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'] is not None:
        try:
            person_marketo_id = int(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])
            rv = enqueue_task('delete_lead_in_marketo', {'id': person_marketo_id})
        except ValueError:
            message = 'Incorrect marketo_id=%s' % str(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])
            app.logger.error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@app.route('/pipedrive/organization/<int:organization_id>', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_organization(organization_id):
    rv = enqueue_task('create_or_update_company_in_marketo', {'id': organization_id})
    return jsonify(**rv)


@app.route('/pipedrive/organization', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_organization_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            organization_id = int(params['current']['id'])
            rv = enqueue_task('create_or_update_company_in_marketo', {'id': organization_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            app.logger.error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_deal(deal_id):
    rv = enqueue_task('create_or_update_opportunity_in_marketo', {'id': deal_id})
    return jsonify(**rv)


@app.route('/pipedrive/deal', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_deal_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            deal_id = int(params['current']['id'])
            rv = enqueue_task('create_or_update_opportunity_in_marketo', {'id': deal_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            app.logger.error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@app.route('/marketo/lead/<int:lead_id>/activity', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def sync_lead_activity(lead_id):
    rv = enqueue_task('create_activity_in_pipedrive', {'id': lead_id})
    return jsonify(**rv)


@app.route('/pipedrive/organization/<int:organization_id>/compute', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def compute_organization(organization_id):
    rv = enqueue_task('compute_organization_in_pipedrive', {'id': organization_id})
    return jsonify(**rv)


@app.route('/pipedrive/organization/compute', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def compute_organization_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            organization_id = int(params['current']['id'])

            rv = enqueue_task('compute_organization_in_pipedrive', {'id': organization_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            app.logger.error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@app.route('/pipedrive/deal/notify', methods=['POST'])
@authenticate(authorized_keys=app.config['FLASK_AUTHORIZED_KEYS'])
def compute_deal_with_params():
    params = request.get_json()
    rv = {}
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            deal_id = int(params['current']['id'])

            deal_status = params['current']['status']
            previous_deal_status = params['previous']['status']
            if deal_status != previous_deal_status and deal_status in ('lost', 'won'):
                rv = enqueue_task('notify_deal_in_slack_for_status', {'id': deal_id})

            deal_notes_count = params['current']['notes_count']
            previous_deal_notes_count = params['previous']['notes_count']
            if deal_notes_count == previous_deal_notes_count + 1:
                rv = enqueue_task('notify_deal_in_slack_for_note', {'id': deal_id})

        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            app.logger.error(message)
            rv = {'error': message}

    return jsonify(**rv)


def enqueue_task(task_name, params):
    """
    Create a task and place it in a push queue for further processing.
    :param task_name: The task name
    :param params: The task parameters
    :return: A custom response object containing a message
    """
    # Search for the task in the datastore
    already_enqueued_task = EnqueuedTask.query(ndb.AND(EnqueuedTask.name == task_name, EnqueuedTask.params == params))\
        .get()
    if already_enqueued_task and not already_enqueued_task.ata:  # Enqueued and never running
        response = {'message': 'Task already enqueued.'}

    else:
        if already_enqueued_task:
            # Enqueued but running or failed, how to make the difference?
            try:
                # Delete it in any case
                already_enqueued_task_key = already_enqueued_task.key
                already_enqueued_task_id = already_enqueued_task_key.id()
                already_enqueued_task_key.delete()  # It may delete a running task
                queue = taskqueue.Queue('default')
                former_task = taskqueue.Task(name=already_enqueued_task_id)
                queue.delete_tasks(former_task)
            except taskqueue.BadTaskStateError:
                pass

        # Create and enqueue App Engine task
        task = taskqueue.add(
            url='/task/%s' % task_name,
            target='worker',
            params=params)

        # Store the task to prevent from duplicates
        enqueued_task = EnqueuedTask(name=task_name, params=params, id=task.name)
        enqueued_task.put()

        response = {'message': 'Task {} enqueued, ETA {}.'.format(task.name, task.eta)}

    return response
