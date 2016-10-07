from flask import Flask, url_for, request, jsonify
import marketo
import pipedrive
from secret import *
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config.from_object(__name__)

mkto = marketo.MarketoClient(
    IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)

pd = pipedrive.PipedriveClient(PD_API_TOKEN)

mapping = {  # From Marketo to Pipedrive
    "name": ["firstName", "lastName"],
    "email": ["email"]
}


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
def create_or_update_lead_in_pipedrive(lead_id):

    app.logger.debug("Getting lead data from Marketo")
    lead = marketo.Lead(mkto, lead_id)
    app.logger.debug("Sending to Pipedrive")
    person = pipedrive.Person(pd, lead.pipedriveId)
    for pd_field in mapping:
        setattr(person, pd_field, " ".join(map(lambda mkto_field: getattr(lead, mkto_field), mapping[pd_field])))
    # TODO for test purpose, set owner_id
    person.owner_id = 1628545  # my (Helene Jonin) owner id
    person.save()

    return 'OK'
