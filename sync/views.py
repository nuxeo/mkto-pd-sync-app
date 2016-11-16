from flask import jsonify, request
from functools import wraps
from secret import *

import mappings
import marketo
import pipedrive
import sync


class InvalidUsage(Exception):
    """Exception raised for errors in the authentication.
    """
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        return rv


@sync.app.errorhandler(InvalidUsage)
def handle_authentication_error(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def authenticate(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.args.get('api_key') and request.args.get('api_key') in FLASK_AUTHORIZED_KEYS:
            return f(*args, **kwargs)
        else:
            raise InvalidUsage('Authentication required', status_code=401)
    return decorated_function


@sync.app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
@authenticate
def marketo_lead_to_pipedrive_person(lead_id):
    ret = create_or_update_person_in_pipedrive(lead_id)
    return jsonify(**ret)


@sync.app.route('/marketo/lead/<int:lead_pipedrive_id>/delete', methods=['POST'])
@authenticate
def delete_pipedrive_person(lead_pipedrive_id):
    data = sync.get_pipedrive_client().delete_resource("person", lead_pipedrive_id)

    if data:
        ret = {
            "status": "deleted",
            "id": data["id"]
        }

    else:
        ret = {
            "error": "Could not delete person with id %s" % str(lead_pipedrive_id)
        }

    return jsonify(**ret)


@sync.app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
@authenticate
def pipedrive_person_to_marketo_lead(person_id):
    ret = create_or_update_lead_in_marketo(person_id)
    return jsonify(**ret)


@sync.app.route('/pipedrive/person', methods=['POST'])
@authenticate
def pipedrive_person_to_marketo_lead_with_params():
    ret = {}
    params = request.get_json()
    if params is not None and "current" in params and "id" in params["current"] and params["current"]["id"] is not None:
        try:
            person_id = int(params["current"]["id"])
            ret = create_or_update_lead_in_marketo(person_id)
        except ValueError:
            ret = {
                "error": "Incorrect id %s" % str(params["current"]["id"])
            }
    return jsonify(**ret)


@sync.app.route('/pipedrive/organization/<int:organization_id>', methods=['POST'])
@authenticate
def pipedrive_organization_to_marketo_lead(organization_id):
    ret = create_or_update_company_in_marketo(organization_id)
    return jsonify(**ret)


@sync.app.route('/pipedrive/organization', methods=['POST'])
@authenticate
def pipedrive_organization_to_marketo_company_with_params():
    ret = {}
    params = request.get_json()
    if params is not None and "current" in params and "id" in params["current"] and params["current"]["id"] is not None:
        try:
            organization_id = int(params["current"]["id"])
            ret = create_or_update_company_in_marketo(organization_id)
        except ValueError:
            ret = {
                "error": "Incorrect id %s" % str(params["current"]["id"])
            }
    return jsonify(**ret)


@sync.app.route('/pipedrive/person/<int:pipedrive_marketo_id>/delete', methods=['POST'])
@authenticate
def delete_marketo_lead(pipedrive_marketo_id):
    lead = marketo.Lead(sync.get_marketo_client(), pipedrive_marketo_id)

    lead.toDelete = True
    lead.save()

    if lead.id is not None:
        ret = {
            "status": "Ready for deletion",
            "id": lead.id
        }
    else:
        ret = {
            "error": "Could not prepare lead for deletion with id %s" % str(pipedrive_marketo_id)
        }

    return jsonify(**ret)


@sync.app.route('/pipedrive/person/delete', methods=['POST'])
@authenticate
def delete_marketo_lead_with_params():
    ret = {}
    params = request.get_json()
    # 9a9714c55a34f5faf2956584040ca245b7ab641b = marketo ID hash key
    if params is not None and "previous" in params and "9a9714c55a34f5faf2956584040ca245b7ab641b" in params["previous"] and params["previous"]["9a9714c55a34f5faf2956584040ca245b7ab641b"] is not None:
        try:
            pipedrive_marketo_id = int(params["previous"]["9a9714c55a34f5faf2956584040ca245b7ab641b"])
            lead = marketo.Lead(sync.get_marketo_client(), pipedrive_marketo_id)

            lead.toDelete = True
            lead.save()

            if lead.id is not None:
                ret = {
                    "status": "Ready for deletion",
                    "id": lead.id
                }
            else:
                ret = {
                    "error": "Could not prepare lead for deletion with id %s" % str(pipedrive_marketo_id)
                }
        except ValueError:
            ret = {
                "error": "Incorrect id %s" % str(params["previous"]["9a9714c55a34f5faf2956584040ca245b7ab641b"])
            }
    return jsonify(**ret)


@sync.app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
@authenticate
def pipedrive_deal_to_marketo_opportunity_and_role(deal_id):
    ret = create_or_update_opportunity_in_marketo(deal_id)
    return jsonify(**ret)


@sync.app.route('/pipedrive/deal', methods=['POST'])
@authenticate
def pipedrive_deal_to_marketo_opportunity_and_role_with_params():
    ret = {}
    params = request.get_json()
    if params is not None and "current" in params and "id" in params["current"] and params["current"]["id"] is not None:
        try:
            deal_id = int(params["current"]["id"])
            ret = create_or_update_opportunity_in_marketo(deal_id)
        except ValueError:
            ret = {
                "error": "Incorrect id %s" % str(params["current"]["id"])
            }
    return jsonify(**ret)


def create_or_update_person_in_pipedrive(lead_id):
    """Creates or updates a person in Pipedrive with data from the
    lead found in Marketo with the given id.
    Update can be performed if the lead is already associated to a person
    (field pipedriveId is populated).
    Data to set is defined in mappings.
    If the person is already up-to-date with any associated lead, does nothing.
    """
    sync.app.logger.debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(sync.get_marketo_client(), lead_id)

    if lead.id is not None:
        person = pipedrive.Person(sync.get_pipedrive_client(), lead.pipedriveId)
        status = "created" if person.id is None else "updated"

        data_changed = False
        for pd_field in mappings.PERSON_TO_LEAD:
            data_changed = update_field(lead, person, pd_field, mappings.PERSON_TO_LEAD[pd_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(person.id) if person.id is not None else "")
            person.save()

            if lead.pipedriveId is None or lead.pipedriveId != person.id:
                sync.app.logger.debug("Updating Pipedrive id in Marketo")
                lead.pipedriveId = person.id
                lead.save()
        else:
            sync.app.logger.debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": person.id
        }

    else:
        ret = {
            "error": "No lead found with id %s" % str(lead_id)
        }

    return ret


def create_or_update_organization_in_pipedrive(company_external_id):
    """Creates or updates an organization in Pipedrive with data from the
    company found in Marketo with the given name.
    Update can be performed if the organization and the company share the same name.
    Data to set is defined in mappings.
    If the organization is already up-to-date with any associated company, does nothing.
    """
    sync.app.logger.debug("Getting company data from Marketo with external id %s", str(company_external_id))
    company = marketo.Company(sync.get_marketo_client(), company_external_id, "externalCompanyId")

    if company.id is not None:
        # Search organization in Pipedrive
        organization_id = marketo.get_id_part_from_external(company.externalCompanyId)
        if organization_id:  # Try id
            organization = pipedrive.Organization(sync.get_pipedrive_client(), organization_id)
        if not organization_id or organization.id is None:  # Then name
            organization = pipedrive.Organization(sync.get_pipedrive_client(), company.company, "name")
        if organization.id is None:  # Finally Email domain
            organization = pipedrive.Organization(sync.get_pipedrive_client(), company.website, "email_domain")
        status = "created" if organization.id is None else "updated"

        data_changed = False
        for pd_field in mappings.ORGANIZATION_TO_COMPANY:
            data_changed = update_field(company, organization, pd_field, mappings.ORGANIZATION_TO_COMPANY[pd_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.app.logger.debug("Sending to Pipedrive%s", " with id %s"
                                                            % str(organization.id) if organization.id is not None else "")
            organization.save()
        else:
            sync.app.logger.debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": organization.id
        }

    else:
        ret = {
            "error": "No company found with external id %s" % str(company_external_id)
        }

    return ret


def create_or_update_lead_in_marketo(person_id):
    """Creates or updates a lead in Marketo with data from the
    person found in Pipedrive with the given id.
    Update can be performed if the person is already associated to a lead
    (field marketoid is populated).
    Data to set is defined in mappings.
    If the lead is already up-to-date with any associated person, does nothing.
    """
    sync.app.logger.debug("Getting person data from Pipedrive with id %s", str(person_id))
    person = pipedrive.Person(sync.get_pipedrive_client(), person_id)

    if person.id is not None:
        lead = marketo.Lead(sync.get_marketo_client(), person.marketoid)
        status = "created" if lead.id is None else "updated"

        data_changed = False
        for mkto_field in mappings.LEAD_TO_PERSON:
            data_changed = update_field(person, lead, mkto_field, mappings.LEAD_TO_PERSON[mkto_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.app.logger.debug("Sending to Marketo%s", " with id %s" % str(person.id) if person.id is not None else "")
            lead.save()

            if person.marketoid is None or int(person.marketoid) != lead.id:
                sync.app.logger.debug("Updating Marketo id in Pipedrive")
                person.marketoid = lead.id
                person.save()
        else:
            sync.app.logger.debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": lead.id
        }

    else:
        ret = {
            "error": "No person found with id %s" % str(person_id)
        }

    return ret


def create_or_update_company_in_marketo(organization_id):
    """Creates or updates a company in Marketo with data from the
    organization found in Pipedrive with the given name.
    Update can be performed if the company and the organization share the same name.
    Data to set is defined in mappings.
    If the company is already up-to-date with any associated organization, does nothing.
    """
    sync.app.logger.debug("Getting organization data from Pipedrive with id %s", str(organization_id))
    organization = pipedrive.Organization(sync.get_pipedrive_client(), organization_id)

    if organization.id is not None:
        # Search organization in Pipedrive
        # Try external id
        company = marketo.Company(sync.get_marketo_client(),
                                  marketo.compute_external_id("organization", organization.id), "externalCompanyId")
        if company.id is None:  # Or name
            company = marketo.Company(sync.get_marketo_client(), organization.name, "company")

        data_changed = False
        if company.id is None:
            status = "created"
            external_id = marketo.compute_external_id("organization", organization.id)
            company.externalCompanyId = external_id
            data_changed = True
        else:
            status = "updated"

        for mkto_field in mappings.COMPANY_TO_ORGANIZATION:
            data_changed = update_field(organization, company, mkto_field, mappings.COMPANY_TO_ORGANIZATION[mkto_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.app.logger.debug("Sending to Marketo%s", " with id %s" % str(company.id) if company.id is not None else "")
            company.save()
        else:
            sync.app.logger.debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": company.id,
            "externalId": company.externalCompanyId
        }

    else:
        ret = {
            "error": "No organization found with id %s" % str(organization_id)
        }

    return ret


def create_or_update_opportunity_in_marketo(deal_id):
    """Creates or updates an opportunity and an opportunity role in Marketo with data from the
    deal found in Pipedrive with the given id.
    Update can be performed if the deal is already associated to an opportunity
    (externalOpportunityId is computed from deal id).
    Role cannot be updated (no point for it unless we are mapping the only updateable field: isPrimary).
    Data to set is defined in mappings.
    If the opportunity is already up-to-date with any associated deal, does nothing.
    """
    sync.app.logger.debug("Getting deal data from Pipedrive with id %s", str(deal_id))
    deal = pipedrive.Deal(sync.get_pipedrive_client(), deal_id)

    if deal.id is not None:

        # Filter deals
        pipeline = pipedrive.Pipeline(sync.get_pipedrive_client(), deal.pipeline_id)
        if pipeline.name == "NX Subscription (New and Upsell)":

            # Opportunity
            external_id = marketo.compute_external_id("deal", deal.id)
            opportunity = marketo.Opportunity(sync.get_marketo_client(), external_id, "externalOpportunityId")

            data_changed = False
            if opportunity.id is None:
                opportunity_status = "created"
                opportunity.externalOpportunityId = external_id
                data_changed = True
            else:
                opportunity_status = "updated"

            for mkto_field in mappings.DEAL_TO_OPPORTUNITY:
                data_changed = update_field(deal, opportunity, mkto_field, mappings.DEAL_TO_OPPORTUNITY[mkto_field])\
                               or data_changed

            if data_changed:
                # Perform the update only if data actually changed
                sync.app.logger.debug("Sending to Marketo (opportunity)%s",
                                      " with id %s" % str(opportunity.id) if opportunity.id is not None else "")
                opportunity.save()
            else:
                sync.app.logger.debug("Nothing to do")
                opportunity_status = "skipped"

            # Role
            role = None
            if deal.contact_person.marketoid is not None:  # Ensure person has existed in Marketo # TODO: create if not?
                # Role will be automatically created or updated using these 3 fields ("dedupeFields")
                role = marketo.Role(sync.get_marketo_client())
                role.externalOpportunityId = opportunity.externalOpportunityId
                role.leadId = deal.contact_person.marketoid
                role.role = deal.champion.title if deal.champion and deal.champion.title else "Default Role"
                role.isPrimary = deal.champion and deal.champion.marketoid == role.leadId
                sync.app.logger.debug("Sending to Marketo (role)")
                role.save()

            ret = {
                "opportunity": {
                    "status": opportunity_status,
                    "id": opportunity.id
                },
                "role": {
                    "id": role.id
                }
            }

        else:
            ret = {
                "status": "skipped",
                "message": "Deal sync not allowed for pipeline %s" % pipeline.name
            }

    else:
        ret = {
            "error": "No deal found with id %s" % str(deal_id)
        }

    return ret


def update_field(from_resource, to_resource, to_field, mapping):
    sync.app.logger.debug("Updating field %s", to_field)

    new_attr = get_new_attr(from_resource, mapping)

    updated = False
    if hasattr(to_resource, to_field):
        old_attr = getattr(to_resource, to_field)
        sync.app.logger.debug("Old attribute for field %s was %s and new is %s", to_field, old_attr, new_attr)
        if new_attr != old_attr:
            setattr(to_resource, to_field, new_attr)
            updated = True
    else:
        setattr(to_resource, to_field, new_attr)
        updated = True

    return updated


def get_new_attr(from_resource, mapping):
    from_values = []

    if "fields" in mapping:
        for from_field in mapping["fields"]:
            from_attr = getattr(from_resource, from_field)

            # Call pre adapter on field raw value
            if "pre_adapter" in mapping and callable(mapping["pre_adapter"]):
                sync.app.logger.debug("And pre-adapting value %s", from_attr)
                from_attr = mapping["pre_adapter"](from_attr)

            from_values.append(from_attr)
    else:
        # Pass the whole resource
        if "transformer" in mapping and callable(mapping["transformer"]):
            sync.app.logger.debug("And transforming resource %s", from_resource)
            from_attr = mapping["transformer"](from_resource)
            from_values.append(from_attr)

    ret = None
    if len(from_values):
        ret = from_values[0]  # Assume first value is the right one
        if len(from_values) > 1:  # Unless a mode is provided
            if "mode" in mapping:
                if mapping["mode"] == "join":
                    # For join mode assume separator is space
                    ret = " ".join(value for value in from_values if value)
                    ret = ret if ret.strip() else None
                elif mapping["mode"] == "choose":
                    # Get first non empty value
                    ret = next((value for value in from_values if value), None)

    # Call post adapter on result
    if "post_adapter" in mapping and callable(mapping["post_adapter"]):
        sync.app.logger.debug("And post-adapting result %s", ret)
        ret = mapping["post_adapter"](ret)

    return ret
