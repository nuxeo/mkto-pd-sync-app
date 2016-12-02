from . import app, get_config
from .util import authenticate

from flask import jsonify, request
from google.appengine.api import taskqueue


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_lead(lead_id):
    response = enqueue_task('create_or_update_person_in_pipedrive', lead_id)
    return jsonify(**response)


@app.route('/marketo/lead/<int:lead_pipedrive_id>/delete', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_lead_delete(lead_pipedrive_id):
    response = enqueue_task('delete_person_in_pipedrive', lead_pipedrive_id)
    return jsonify(**response)


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person(person_id):
    response = enqueue_task('create_or_update_lead_in_marketo', person_id)
    return jsonify(**response)


@app.route('/pipedrive/person', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person_with_params():
    response = {}
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            person_id = int(params['current']['id'])
            response = enqueue_task('create_or_update_lead_in_marketo', person_id)
        except ValueError:
            response = {'error': 'Incorrect id %s' % str(params['current']['id'])}
    return jsonify(**response)


@app.route('/pipedrive/person/<int:person_marketo_id>/delete', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person_delete(person_marketo_id):
    response = enqueue_task('delete_lead_in_marketo', person_marketo_id)
    return jsonify(**response)


@app.route('/pipedrive/person/delete', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_person_delete_with_params():
    response = {}
    params = request.get_json()
    # 9a9714c55a34f5faf2956584040ca245b7ab641b = marketo ID hash key
    if params is not None and 'previous' in params and '9a9714c55a34f5faf2956584040ca245b7ab641b' in params['previous'] and params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'] is not None:
        try:
            person_marketo_id = int(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])
            response = enqueue_task('delete_lead_in_marketo', person_marketo_id)
        except ValueError:
            response = {'error': 'Incorrect id %s' % str(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])}
    return jsonify(**response)


@app.route('/pipedrive/organization/<int:organization_id>', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_organization(organization_id):
    response = enqueue_task('create_or_update_company_in_marketo', organization_id)
    return jsonify(**response)


@app.route('/pipedrive/organization', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_organization_with_params():
    response = {}
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            organization_id = int(params['current']['id'])
            response = enqueue_task('create_or_update_company_in_marketo', organization_id)
        except ValueError:
            response = {'error': 'Incorrect id %s' % str(params['current']['id'])}
    return jsonify(**response)


@app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_deal(deal_id):
    response = enqueue_task('create_or_update_opportunity_in_marketo', deal_id)
    return jsonify(**response)


@app.route('/pipedrive/deal', methods=['POST'])
@authenticate(authorized_keys=get_config('FLASK_AUTHORIZED_KEYS'))
def sync_deal_with_params():
    response = {}
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            deal_id = int(params['current']['id'])
            response = enqueue_task('create_or_update_opportunity_in_marketo', deal_id)
        except ValueError:
            response = {'error': 'Incorrect id %s' % str(params['current']['id'])}
    return jsonify(**response)


def enqueue_task(task_name, object_id):
    task = taskqueue.add(
            url='/task/%s' % task_name,
            target='worker',
            params={'id': object_id})

    response = {'message': 'Task {} enqueued, ETA {}.'.format(task.name, task.eta)}
    return response
