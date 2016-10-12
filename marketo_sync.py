from flask import Flask, url_for, request, jsonify
import marketo
import pipedrive
import mappings
from secret import *
import logging

# logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(__name__)

mkto = marketo.MarketoClient(
    IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)  # TODO: Add possibility to refresh access token!

pd = pipedrive.PipedriveClient(PD_API_TOKEN)


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
def create_or_update_person_in_pipedrive(lead_id):

    app.logger.debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(mkto, lead_id)

    person = pipedrive.Person(pd, lead.pipedriveId)
    updated = False
    for pd_field in mappings.PIPEDRIVE_TO_MARKETO:
        updated = update_field(lead, person, pd_field, mappings.PIPEDRIVE_TO_MARKETO[pd_field], pd) or updated

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
    person = pipedrive.Person(pd, person_id)

    lead = marketo.Lead(mkto, person.marketoid)
    updated = False
    for mkto_field in mappings.MARKETO_TO_PIPEDRIVE:
        updated = update_field(person, lead, mkto_field, mappings.MARKETO_TO_PIPEDRIVE[mkto_field], mkto) or updated

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
