from flask import Flask, url_for, request, jsonify
import marketo
import pipedrive
import mappings
from secret import *
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(__name__)

mkto = marketo.MarketoClient(
    IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)

pd = pipedrive.PipedriveClient(PD_API_TOKEN)


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
def create_or_update_lead_in_pipedrive(lead_id):

    app.logger.debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(mkto, lead_id)

    person = pipedrive.Person(pd, lead.pipedriveId)
    for pd_field in mappings.PIPEDRIVE_TO_MARKETO:
        app.logger.debug("Updating field %s", pd_field)
        setattr(person, pd_field, " ".join(
            map(lambda mkto_field: getattr(lead, mkto_field), mappings.PIPEDRIVE_TO_MARKETO[pd_field])))
    # TODO for test purpose, set owner_id
    person.owner_id = 1628545  # my (Helene Jonin) owner id
    app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(lead.pipedriveId) or "")
    person.save()

    if lead.pipedriveId is None:
        app.logger.debug("Updating Pipedrive ID in Marketo")
        lead.pipedriveId = person.id
        lead.save()

    return 'OK'
