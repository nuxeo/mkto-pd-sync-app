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

    if lead.pipedriveId is None or lead.id != person.marketoid:
        app.logger.debug("Updating Pipedrive ID in Marketo")
        lead.pipedriveId = person.id
        lead.save()

    return 'OK'  # TODO


@app.route('/pipedrive/person/<int:person_id>', methods=['POST'])
def create_or_update_lead_in_marketo(person_id):

    app.logger.debug("Getting person data from Pipedrive with id %s", str(person_id))
    person = pipedrive.Person(pd, person_id)

    lead = marketo.Lead(mkto, person.marketoid)
    for mkto_field in mappings.MARKETO_TO_PIPEDRIVE:
        app.logger.debug("Updating field %s", mkto_field)
        mapping = mappings.MARKETO_TO_PIPEDRIVE[mkto_field]
        pd_fields = mapping["fields"]
        setattr(lead, mkto_field, " ".join(map(
            lambda pd_field: adapt_field(getattr(person, pd_field), mapping, mkto), pd_fields)))

    app.logger.debug("Sending to Marketo%s", " with id %s" % str(person.marketoid) or "")
    lead.save()

    if person.marketoid is None or person.marketoid != lead.id:
        app.logger.debug("Updating Marketo ID in Pipedrive")
        person.marketoid = lead.id
        person.save()

    return 'OK'  # TODO


def adapt_field(attr, mapping, client):
    ret = attr
    if "adapter" in mapping and callable(mapping["adapter"]):
        app.logger.debug("Using adapter")
        ret = mapping["adapter"](attr, client)  # TODO: Better parameters passing
    return str(ret) if ret is not None else ""
