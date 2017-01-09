from flask import jsonify, request
from google.appengine.api import taskqueue
from google.appengine.ext import ndb

import sync
from .util import authenticate, EnqueuedTask


@sync.app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_lead(lead_id):
    rv = enqueue_task('create_or_update_person_in_pipedrive', {'id': lead_id})
    return jsonify(**rv)


@sync.app.route('/marketo/lead/<int:lead_pipedrive_id>/delete', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_lead_delete(lead_pipedrive_id):
    rv = enqueue_task('delete_person_in_pipedrive', {'id': lead_pipedrive_id})
    return jsonify(**rv)


@sync.app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person(person_id):
    rv = enqueue_task('create_or_update_lead_in_marketo', {'id': person_id})
    return jsonify(**rv)


@sync.app.route('/pipedrive/person', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            person_id = int(params['current']['id'])
            rv = enqueue_task('create_or_update_lead_in_marketo', {'id': person_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            sync.get_logger().error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@sync.app.route('/pipedrive/person/<int:person_marketo_id>/delete', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person_delete(person_marketo_id):
    rv = enqueue_task('delete_lead_in_marketo', {'id': person_marketo_id})
    return jsonify(**rv)


@sync.app.route('/pipedrive/person/delete', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person_delete_with_params():
    params = request.get_json()
    # 9a9714c55a34f5faf2956584040ca245b7ab641b = marketo ID hash key
    if params is not None and 'previous' in params and '9a9714c55a34f5faf2956584040ca245b7ab641b' in params[
        'previous'] and params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'] is not None:
        try:
            person_marketo_id = int(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])
            rv = enqueue_task('delete_lead_in_marketo', {'id': person_marketo_id})
        except ValueError:
            message = 'Incorrect marketo_id=%s' % str(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])
            sync.get_logger().error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@sync.app.route('/pipedrive/organization/<int:organization_id>', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_organization(organization_id):
    rv = enqueue_task('create_or_update_company_in_marketo', {'id': organization_id})
    return jsonify(**rv)


@sync.app.route('/pipedrive/organization', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_organization_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            organization_id = int(params['current']['id'])
            rv = enqueue_task('create_or_update_company_in_marketo', {'id': organization_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            sync.get_logger().error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@sync.app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_deal(deal_id):
    rv = enqueue_task('create_or_update_opportunity_in_marketo', {'id': deal_id})
    return jsonify(**rv)


@sync.app.route('/pipedrive/deal', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_deal_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            deal_id = int(params['current']['id'])
            rv = enqueue_task('create_or_update_opportunity_in_marketo', {'id': deal_id})
        except ValueError:
            message = 'Incorrect id=%s' % str(params['current']['id'])
            sync.get_logger().error(message)
            rv = {'error': message}
    else:
        rv = {}
    return jsonify(**rv)


@sync.app.route('/marketo/lead/<int:lead_id>/activity', methods=['POST'])
@authenticate(authorized_keys=sync.get_config('FLASK_AUTHORIZED_KEYS'))
def sync_lead_activity(lead_id):
    rv = enqueue_task('create_activity_in_pipedrive', {'id': lead_id})
    return jsonify(**rv)


def enqueue_task(task_name, params):
    """
    Create a task and place it in a push queue for further processing.
    :param task_name: The task name
    :param params: The task parameters
    :return: A custom response object containing a message
    """
    # Search for the the task in the datastore
    already_enqueued_task = EnqueuedTask.query(ndb.AND(EnqueuedTask.name == task_name, EnqueuedTask.params == params)).get()
    if already_enqueued_task and not already_enqueued_task.ata:  # Enqueued and never running
        response = {'message': 'Task already enqueued.'}

    else:
        if already_enqueued_task:
            # Enqueued but running or failed, how to make the difference?
            try:
                # Delete it in any case
                already_enqueued_task.key.delete()  # It may delete a running task
                q = taskqueue.Queue('default')
                t = taskqueue.Task(name=already_enqueued_task.task_name)
                q.delete_tasks(t)
            except taskqueue.BadTaskStateError:
                pass
        # Store the task to prevent from duplicates
        enqueued_task = EnqueuedTask(name=task_name, params=params)
        enqueued_task.put()

        # Create and enqueue task
        params.update({'task_urlsafe': enqueued_task.key.urlsafe()})
        task = taskqueue.add(
            url='/task/%s' % task_name,
            target='worker',
            params=params)
        
        enqueued_task.task_name = task.name
        enqueued_task.put()
        
        response = {'message': 'Task {} enqueued, ETA {}.'.format(task.name, task.eta)}

    return response
