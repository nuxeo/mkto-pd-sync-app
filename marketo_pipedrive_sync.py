from flask import Flask, g
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

    app.logger.debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(get_marketo_client(), lead_id)

    person = pipedrive.Person(get_pipedrive_client(), lead.pipedriveId)
    updated = False
    for pd_field in mappings.PIPEDRIVE_TO_MARKETO:
        updated = update_field(lead, person, pd_field, mappings.PIPEDRIVE_TO_MARKETO[pd_field], get_pipedrive_client()) or updated

    # FIXME for test purpose, set owner_id
    person.owner_id = 1628545  # my (Helene Jonin) owner id

    if updated:
        app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(lead.pipedriveId) or "")
        person.save()

        if lead.pipedriveId is None or lead.id != person.marketoid:
            app.logger.debug("Updating Pipedrive ID in Marketo")
            lead.pipedriveId = person.id
            lead.save()
    else:
        app.logger.debug("Nothing to do")

    return 'OK'  # TODO


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
def create_or_update_lead_in_marketo(person_id):

    app.logger.debug("Getting person data from Pipedrive with id %s", str(person_id))
    person = pipedrive.Person(get_pipedrive_client(), person_id)

    lead = marketo.Lead(get_marketo_client(), person.marketoid)
    updated = False
    for mkto_field in mappings.MARKETO_TO_PIPEDRIVE:
        updated = update_field(person, lead, mkto_field, mappings.MARKETO_TO_PIPEDRIVE[mkto_field], get_marketo_client()) or updated

    if updated:
        app.logger.debug("Sending to Marketo%s", " with id %s" % str(person.marketoid) or "")
        lead.save()

        if person.marketoid is None or person.marketoid != lead.id:
            app.logger.debug("Updating Marketo ID in Pipedrive")
            person.marketoid = lead.id
            person.save()
    else:
        app.logger.debug("Nothing to do")

    return 'OK'  # TODO


def update_field(from_resource, to_resource, to_field, mapping, to_client):
    updated = False
    app.logger.debug("Updating field %s", to_field)
    from_values = []
    for from_field in mapping["fields"]:
        from_attr = getattr(from_resource, from_field)
        if "adapter" in mapping and callable(mapping["adapter"]):
            app.logger.debug("Using adapter")
            from_attr = mapping["adapter"](from_attr, to_client)  # TODO: Better parameters passing
        from_values.append(str(from_attr) if from_attr is not None else "")
    new_attr = " ".join(from_values)
    if hasattr(to_resource, to_field):
        old_attr = getattr(to_resource, to_field) or ""
        if str(new_attr) != str(old_attr):
            setattr(to_resource, to_field, new_attr)
            updated = True
    else:
        setattr(to_resource, to_field, new_attr)
        updated = True

    return updated

if __name__ == "__main__":
    app.run()
