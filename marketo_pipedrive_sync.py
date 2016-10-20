from flask import Flask, g, jsonify
import marketo
import pipedrive
import mappings
from secret import *

app = Flask(__name__)
app.config.from_object(__name__)


def create_marketo_client():
    """Creates the Marketo client."""
    return marketo.MarketoClient(IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)


def create_pipedrive_client():
    """Creates the Pipedrive client."""
    return pipedrive.PipedriveClient(PD_API_TOKEN)


def get_marketo_client():
    """Creates a new Marketo client if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'marketo_client'):
        g.marketo_client = create_marketo_client()
    return g.marketo_client


def get_pipedrive_client():
    """Creates a new Pipedrive client if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'pipedrive_client'):
        g.pipedrive_client = create_pipedrive_client()
    return g.pipedrive_client


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
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

        if lead.pipedriveId is None or lead.id != person.marketoid:
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
    return jsonify(**ret)


def create_or_update_organization_in_pipedrive(company_name):
    """Creates or update an organization in Pipedrive with data from the
    company found in Marketo with the given name.
    Update can be performed if the organization and the company share the same name.
    Data to set is defined in mappings.
    If the organization is already up-to-date with any associated company, does nothing.
    """
    app.logger.debug("Getting company data from Marketo with name %s", str(company_name))
    company = marketo.Company(get_marketo_client(), company_name, "company")

    organization = get_pipedrive_client().find_resource_by_name("organization", company_name)
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
    return ret


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
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

        if person.marketoid is None or person.marketoid != lead.id:
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
    return jsonify(**ret)


def create_or_update_company_in_marketo(organization_name):
    """Creates or update a company in Marketo with data from the
    organization found in Pipedrive with the given name.
    Update can be performed if the company and the organization share the same name.
    Data to set is defined in mappings.
    If the company is already up-to-date with any associated organization, does nothing.
    """
    app.logger.debug("Getting organization data from Pipedrive with name %s", str(organization_name))
    organization = get_pipedrive_client().find_resource_by_name("organization", organization_name)

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
    return ret


@app.route('/pipedrive/deal/<int:deal_id>', methods=['POST'])
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
    if deal.contact_person.marketoid is not None:  # Ensure lead exists in Marketo # TODO: create if it does not?
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
    return jsonify(**ret)


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

    # Assume that if several fields are provided for mapping values should be joined using space
    ret = " ".join(from_values)

    # Call post adapter on result value
    if "post_adapter" in mapping and callable(mapping["post_adapter"]):
        app.logger.debug("And post-adapting result %s", ret)
        ret = mapping["post_adapter"](ret)

    return ret


if __name__ == "__main__":
    app.run()
