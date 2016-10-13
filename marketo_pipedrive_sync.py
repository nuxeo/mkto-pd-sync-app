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

    status = "created" if lead.pipedriveId is None else "updated"

    person = pipedrive.Person(get_pipedrive_client(), lead.pipedriveId)
    data_changed = False
    for pd_field in mappings.PIPEDRIVE_TO_MARKETO:
        data_changed = update_field(lead, person, pd_field, mappings.PIPEDRIVE_TO_MARKETO[pd_field], get_pipedrive_client())\
                  or data_changed

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

    status = "created" if person.marketoid is None else "updated"

    lead = marketo.Lead(get_marketo_client(), person.marketoid)
    data_changed = False
    for mkto_field in mappings.MARKETO_TO_PIPEDRIVE:
        data_changed = update_field(person, lead, mkto_field, mappings.MARKETO_TO_PIPEDRIVE[mkto_field], get_marketo_client()) or data_changed

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


def update_field(from_resource, to_resource, to_field, mapping, to_client):
    app.logger.debug("Updating field %s", to_field)
    updated = False

    from_values = []
    for from_field in mapping["fields"]:
        from_attr = getattr(from_resource, from_field)

        if "adapter" in mapping and callable(mapping["adapter"]):
            app.logger.debug("Using adapter")
            from_attr = mapping["adapter"](value=from_attr, client=to_client)

        from_values.append(str(from_attr) if from_attr is not None else "")

    # Assume that if several fields are provided for mapping values should be joined using space
    new_attr = " ".join(from_values)

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
