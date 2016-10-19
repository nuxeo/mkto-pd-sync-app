from flask import Flask, g, jsonify
import marketo
import pipedrive
import mappings
from secret import *
import json

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
        new_attr = get_new_value(lead, mappings.PERSON_TO_LEAD[pd_field])
        if pd_field != "org_id":
            data_changed = update_field(person, pd_field, new_attr) or data_changed
        else:
            new_org_id = ""
            if new_attr:
                organization_data = json.loads(create_or_update_organization_in_pipedrive(new_attr).data)
                new_org_id = organization_data["id"]
            data_changed = update_field(person, pd_field, new_org_id) or data_changed

    # FIXME for test purpose, set owner_id
    person.owner_id = 1628545  # my (Helene Jonin) owner id

    if data_changed:
        # Perform the update only if data actually changed
        app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(lead.pipedriveId) or "")
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
        new_attr = get_new_value(company, mappings.ORGANIZATION_TO_COMPANY[pd_field])
        data_changed = update_field(organization, pd_field, new_attr) or data_changed

    # FIXME for test purpose, set owner_id
    organization.owner_id = 1628545  # my (Helene Jonin) owner id

    if data_changed:
        # Perform the update only if data actually changed
        app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(organization.id) or "")
        organization.save()
    else:
        app.logger.debug("Nothing to do")
        status = "skipped"

    ret = {
        "status": status,
        "id": organization.id
    }
    return jsonify(**ret)


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
        new_attr = get_new_value(person, mappings.LEAD_TO_PERSON[mkto_field])
        data_changed = update_field(lead, mkto_field, new_attr) or data_changed

    if data_changed:
        # Perform the update only if data actually changed
        app.logger.debug("Sending to Marketo%s", " with id %s" % str(person.marketoid) or "")
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
        new_attr = get_new_value(deal, mappings.DEAL_TO_OPPORTUNITY[mkto_field])
        data_changed = update_field(opportunity, mkto_field, new_attr) or data_changed

    if data_changed:
        # Perform the update only if data actually changed
        app.logger.debug("Sending to Marketo (opportunity)%s", " with id %s" % str(deal.id) or "")
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
            "id": opportunity.marketoGUID
        },
        "role": {
            "id": role.marketoGUID if role is not None else ""
        }
    }
    return jsonify(**ret)


def get_new_value(from_resource, mapping):
    from_values = []
    for from_field in mapping["fields"]:
        from_attr = getattr(from_resource, from_field)

        if "adapter" in mapping and callable(mapping["adapter"]):
            app.logger.debug("Adapting value %s", from_attr)
            from_attr = mapping["adapter"](from_attr)

        from_values.append(str(from_attr) if from_attr is not None else "")

    # Assume that if several fields are provided for mapping values should be joined using space
    return " ".join(from_values)


def update_field(to_resource, to_field, new_attr):
    app.logger.debug("Updating field %s", to_field)
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


if __name__ == "__main__":
    app.run()
