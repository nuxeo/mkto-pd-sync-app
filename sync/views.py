from flask import jsonify, request
from functools import wraps
from secret import *
from sync import app, get_marketo_client, get_pipedrive_client

import mappings
import marketo
import pipedrive


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


@app.errorhandler(InvalidUsage)
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


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
@authenticate
def marketo_lead_to_pipedrive_person(lead_id):
    ret = create_or_update_person_in_pipedrive(lead_id)
    return jsonify(**ret)


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
@authenticate
def pipedrive_person_to_marketo_lead(person_id):
    ret = create_or_update_lead_in_marketo(person_id)
    return jsonify(**ret)


@app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
@authenticate
def pipedrive_deal_to_marketo_opportunity_and_role(deal_id):
    ret = create_or_update_opportunity_in_marketo(deal_id)
    return jsonify(**ret)


def create_or_update_person_in_pipedrive(lead_id):
    """Creates or update a person in Pipedrive with data from the
    lead found in Marketo with the given id.
    Update can be performed if the lead is already associated to a person
    (field pipedriveId is populated).
    Data to set is defined in mappings.
    If the person is already up-to-date with any associated lead, does nothing.
    """
    app.logger.debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(get_marketo_client(), lead_id)

    if lead.id is not None:
        person = pipedrive.Person(get_pipedrive_client(), lead.pipedriveId)
        status = "created" if person.id is None else "updated"

        data_changed = False
        for pd_field in mappings.PERSON_TO_LEAD:
            data_changed = update_field(lead, person, pd_field, mappings.PERSON_TO_LEAD[pd_field])\
                           or data_changed

        # FIXME for test purpose, set owner_id
        person.owner_id = 1628545  # my (Helene Jonin) owner id

        if data_changed:
            # Perform the update only if data actually changed
            app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(person.id) if person.id is not None else "")
            person.save()

            if lead.pipedriveId is None or str(lead.id) != str(person.marketoid):
                app.logger.debug("Updating Pipedrive ID in Marketo")
                lead.pipedriveId = person.id
                lead.save()
        else:
            app.logger.debug("Nothing to do")
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


def create_or_update_organization_in_pipedrive(company_name):
    """Creates or update an organization in Pipedrive with data from the
    company found in Marketo with the given name.
    Update can be performed if the organization and the company share the same name.
    Data to set is defined in mappings.
    If the organization is already up-to-date with any associated company, does nothing.
    """
    app.logger.debug("Getting company data from Marketo with name %s", str(company_name))
    company = marketo.Company(get_marketo_client(), company_name, "company")

    if company.id is not None:
        organization = pipedrive.Organization(get_pipedrive_client(), company_name, "name")
        status = "created" if organization.id is None else "updated"

        data_changed = False
        for pd_field in mappings.ORGANIZATION_TO_COMPANY:
            data_changed = update_field(company, organization, pd_field, mappings.ORGANIZATION_TO_COMPANY[pd_field])\
                           or data_changed

        # FIXME for test purpose, set owner_id
        organization.owner_id = 1628545  # my (Helene Jonin) owner id

        if data_changed:
            # Perform the update only if data actually changed
            app.logger.debug("Sending to Pipedrive%s", " with id %s"
                                                       % str(organization.id) if organization.id is not None else "")
            organization.save()
        else:
            app.logger.debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": organization.id
        }

    else:
        ret = {
            "error": "No company found with name %s" % str(company_name)
        }

    return ret


def create_or_update_lead_in_marketo(person_id):
    """Creates or update a lead in Marketo with data from the
    person found in Pipedrive with the given id.
    Update can be performed if the person is already associated to a lead
    (field marketoid is populated).
    Data to set is defined in mappings.
    If the lead is already up-to-date with any associated person, does nothing.
    """
    app.logger.debug("Getting person data from Pipedrive with id %s", str(person_id))
    person = pipedrive.Person(get_pipedrive_client(), person_id)

    if person.id is not None:
        lead = marketo.Lead(get_marketo_client(), person.marketoid)
        status = "created" if lead.id is None else "updated"

        data_changed = False
        for mkto_field in mappings.LEAD_TO_PERSON:
            data_changed = update_field(person, lead, mkto_field, mappings.LEAD_TO_PERSON[mkto_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            app.logger.debug("Sending to Marketo%s", " with id %s" % str(person.id) if person.id is not None else "")
            lead.save()

            if person.marketoid is None or str(person.marketoid) != str(lead.id):
                app.logger.debug("Updating Marketo ID in Pipedrive")
                person.marketoid = lead.id
                person.save()
        else:
            app.logger.debug("Nothing to do")
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


def create_or_update_company_in_marketo(organization_name):
    """Creates or update a company in Marketo with data from the
    organization found in Pipedrive with the given name.
    Update can be performed if the company and the organization share the same name.
    Data to set is defined in mappings.
    If the company is already up-to-date with any associated organization, does nothing.
    """
    app.logger.debug("Getting organization data from Pipedrive with name %s", str(organization_name))
    organization = pipedrive.Organization(get_pipedrive_client(), organization_name, "name")

    if organization.id is not None:
        company = marketo.Company(get_marketo_client(), organization_name, "company")

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
            app.logger.debug("Sending to Marketo%s", " with id %s" % str(company.id) if company.id is not None else "")
            company.save()
        else:
            app.logger.debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": company.id,
            "externalId": company.externalCompanyId
        }

    else:
        ret = {
            "error": "No organization found with name %s" % str(organization_name)
        }

    return ret


def create_or_update_opportunity_in_marketo(deal_id):
    """Creates or update an opportunity and an opportunity role in Marketo with data from the
    deal found in Pipedrive with the given id.
    Update can be performed if the deal is already associated to an opportunity
    (externalOpportunityId is equal to deal id).
    Role cannot be updated (no point for it unless we are mapping the only updateable field: isPrimary).
    Data to set is defined in mappings.
    If the opportunity is already up-to-date with any associated deal, does nothing.
    """
    app.logger.debug("Getting deal data from Pipedrive with id %s", str(deal_id))
    deal = pipedrive.Deal(get_pipedrive_client(), deal_id)

    if deal.id is not None:

        # Opportunity
        external_id = marketo.compute_external_id("deal", deal.id)
        opportunity = marketo.Opportunity(get_marketo_client(), external_id, "externalOpportunityId")

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
            app.logger.debug("Sending to Marketo (opportunity)%s",
                             " with id %s" % str(opportunity.id) if opportunity.id is not None else "")
            opportunity.save()
        else:
            app.logger.debug("Nothing to do")
            opportunity_status = "skipped"

        # Role
        role = None
        if deal.contact_person.marketoid is not None:  # Ensure has existed in Marketo # TODO: create if not?
            # Role will be automatically created or updated using these 3 fields ("dedupeFields")
            role = marketo.Role(get_marketo_client())
            role.externalOpportunityId = opportunity.externalOpportunityId
            role.leadId = deal.contact_person.marketoid
            role.role = "Fake role"  # TODO: set or map role - don't forget to change it in Unit Testing as well
            app.logger.debug("Sending to Marketo (role)")
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
            "error": "No deal found with id %s" % str(deal_id)
        }

    return ret


def update_field(from_resource, to_resource, to_field, mapping):
    app.logger.debug("Updating field %s", to_field)

    new_attr = get_new_attr(from_resource, mapping)

    updated = False
    if hasattr(to_resource, to_field):
        old_attr = getattr(to_resource, to_field) or ""
        if str(new_attr) != str(old_attr):  # Compare value string representations bc not sure of type
            setattr(to_resource, to_field, new_attr)
            updated = True
    else:
        setattr(to_resource, to_field, new_attr)
        updated = True

    return updated


def get_new_attr(from_resource, mapping):
    from_values = []
    for from_field in mapping["fields"]:
        from_attr = getattr(from_resource, from_field)

        # Call pre adapter on field value
        if "pre_adapter" in mapping and callable(mapping["pre_adapter"]):
            app.logger.debug("And pre-adapting value %s", from_attr)
            from_attr = mapping["pre_adapter"](from_attr)

        from_values.append(str(from_attr) if from_attr is not None else "")

    ret = ""
    if len(from_values):
        ret = from_values[0]  # Assume first value is the right one
        if len(from_values) > 1:
            # Otherwise if several fields are provided then mode should be supplied
            if "mode" in mapping:
                if mapping["mode"] == "join":
                    # For join mode assume separator is space
                    ret = " ".join(from_values)
                elif mapping["mode"] == "choose":
                    # Get first non empty value
                    ret = next((value for value in from_values if value is not ""), "")

    # Call post adapter on result value
    if "post_adapter" in mapping and callable(mapping["post_adapter"]):
        app.logger.debug("And post-adapting result %s", ret)
        ret = mapping["post_adapter"](ret)

    return ret
