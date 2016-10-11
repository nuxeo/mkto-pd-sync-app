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
    IDENTITY_ENDPOINT, CLIENT_ID, CLIENT_SECRET, API_ENDPOINT)  # TODO: Add possibility to refresh access token!

pd = pipedrive.PipedriveClient(PD_API_TOKEN)


@app.route('/marketo/lead/<int:lead_id>', methods=['POST'])
def create_or_update_lead_in_pipedrive(lead_id):

    app.logger.debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(mkto, lead_id)

    person = pipedrive.Person(pd, lead.pipedriveId)
    for pd_field in mappings.PIPEDRIVE_TO_MARKETO:
        app.logger.debug("Updating field %s", pd_field)
        mapping = mappings.PIPEDRIVE_TO_MARKETO[pd_field]
        mkto_fields = mapping["fields"]
        setattr(person, pd_field, " ".join(map(
            lambda mkto_field: adapt_field(getattr(lead, mkto_field), mapping, pd), mkto_fields)))

    # FIXME for test purpose, set owner_id
    person.owner_id = 1628545  # my (Helene Jonin) owner id

    app.logger.debug("Sending to Pipedrive%s", " with id %s" % str(lead.pipedriveId) or "")
    person.save()

    if lead.pipedriveId is None:
        app.logger.debug("Updating Pipedrive ID in Marketo")
        lead.pipedriveId = person.id
        lead.save()

    return 'OK'


def adapt_field(attr, mapping, client):
    ret = attr
    if "adapter" in mapping and callable(mapping["adapter"]):
        app.logger.debug("Using adapter")
        ret = mapping["adapter"](attr, client)  # TODO: Better parameters passing
    return str(ret) if ret is not None else ""
