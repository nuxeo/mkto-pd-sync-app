from . import app
from .functions import *
from .util import authenticate, InvalidUsage

from flask import jsonify, request


# Register an error handler to prevent from resulting in an internal server error
@app.errorhandler(InvalidUsage)
def handle_authentication_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
@authenticate
def marketo_lead_to_pipedrive_person(lead_id):
    rv = create_or_update_person_in_pipedrive.delay(lead_id)
    if hasattr(rv, 'key'):
        if rv.return_value is None:
            ret = jsonify(key=rv.key, ready=False)
        else:
            ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
    else:
        ret = jsonify(**rv)
    return ret


@app.route('/marketo/lead/<int:lead_pipedrive_id>/delete', methods=['POST'])
@authenticate
def delete_pipedrive_person(lead_pipedrive_id):
    rv = delete_person_in_pipedrive.delay(lead_pipedrive_id)
    if hasattr(rv, 'key'):
        if rv.return_value is None:
            ret = jsonify(key=rv.key, ready=False)
        else:
            ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
    else:
        ret = jsonify(**rv)
    return ret


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
@authenticate
def pipedrive_person_to_marketo_lead(person_id):
    rv = create_or_update_lead_in_marketo.delay(person_id)
    if hasattr(rv, 'key'):
        if rv.return_value is None:
            ret = jsonify(key=rv.key, ready=False)
        else:
            ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
    else:
        ret = jsonify(**rv)
    return ret


@app.route('/pipedrive/person', methods=['POST'])
@authenticate
def pipedrive_person_to_marketo_lead_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            person_id = int(params['current']['id'])
            rv = create_or_update_lead_in_marketo.delay(person_id)
            if hasattr(rv, 'key'):
                if rv.return_value is None:
                    ret = jsonify(key=rv.key, ready=False)
                else:
                    ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
            else:
                ret = jsonify(**rv)
        except ValueError:
            ret = jsonify(error='Incorrect id %s' % str(params['current']['id']))
    else:
        ret = {}
    return ret


@app.route('/pipedrive/organization/<int:organization_id>', methods=['POST'])
@authenticate
def pipedrive_organization_to_marketo_company(organization_id):
    rv = create_or_update_company_in_marketo.delay(organization_id)
    if hasattr(rv, 'key'):
        if rv.return_value is None:
            ret = jsonify(key=rv.key, ready=False)
        else:
            ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
    else:
        ret = jsonify(**rv)
    return ret


@app.route('/pipedrive/organization', methods=['POST'])
@authenticate
def pipedrive_organization_to_marketo_company_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            organization_id = int(params['current']['id'])
            rv = create_or_update_company_in_marketo.delay(organization_id)
            if hasattr(rv, 'key'):
                if rv.return_value is None:
                    ret = jsonify(key=rv.key, ready=False)
                else:
                    ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
            else:
                ret = jsonify(**rv)
        except ValueError:
            ret = jsonify(error='Incorrect id %s' % str(params['current']['id']))
    else:
        ret = {}
    return ret


@app.route('/pipedrive/person/<int:pipedrive_marketo_id>/delete', methods=['POST'])
@authenticate
def delete_marketo_lead(pipedrive_marketo_id):
    rv = delete_lead_in_marketo.delay(pipedrive_marketo_id)
    if hasattr(rv, 'key'):
        if rv.return_value is None:
            ret = jsonify(key=rv.key, ready=False)
        else:
            ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
    else:
        ret = jsonify(**rv)
    return ret


@app.route('/pipedrive/person/delete', methods=['POST'])
@authenticate
def delete_marketo_lead_with_params():
    params = request.get_json()
    # 9a9714c55a34f5faf2956584040ca245b7ab641b = marketo ID hash key
    if params is not None and 'previous' in params and '9a9714c55a34f5faf2956584040ca245b7ab641b' in params['previous']\
            and params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'] is not None:
        try:
            pipedrive_marketo_id = int(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b'])
            rv = delete_lead_in_marketo.delay(pipedrive_marketo_id)
            if hasattr(rv, 'key'):
                if rv.return_value is None:
                    ret = jsonify(key=rv.key, ready=False)
                else:
                    ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
            else:
                ret = jsonify(**rv)
        except ValueError:
            ret = jsonify(error='Incorrect id %s' % str(params['previous']['9a9714c55a34f5faf2956584040ca245b7ab641b']))
    else:
        ret = {}
    return ret


@app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
@authenticate
def pipedrive_deal_to_marketo_opportunity_and_role(deal_id):
    rv = create_or_update_opportunity_in_marketo.delay(deal_id)
    if hasattr(rv, 'key'):
        if rv.return_value is None:
            ret = jsonify(key=rv.key, ready=False)
        else:
            ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
    else:
        ret = jsonify(**rv)
    return ret


@app.route('/pipedrive/deal', methods=['POST'])
@authenticate
def pipedrive_deal_to_marketo_opportunity_and_role_with_params():
    params = request.get_json()
    if params is not None and 'current' in params and 'id' in params['current'] and params['current']['id'] is not None:
        try:
            deal_id = int(params['current']['id'])
            rv = create_or_update_opportunity_in_marketo.delay(deal_id)
            if hasattr(rv, 'key'):
                if rv.return_value is None:
                    ret = jsonify(key=rv.key, ready=False)
                else:
                    ret = jsonify(key=rv.key, ready=True, result=rv.return_value)
            else:
                ret = jsonify(**rv)
        except ValueError:
            ret = jsonify(error='Incorrect id %s' % str(params['current']['id']))
    else:
        ret = {}
    return ret
