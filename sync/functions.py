from . import get_logger, get_marketo_client, get_pipedrive_client
from .mappings import *

import marketo
import pipedrive


def create_or_update_person_in_pipedrive(lead_id):
    """Creates or updates a person in Pipedrive with data from the
    lead found in Marketo with the given id.
    Update can be performed if the lead is already associated to a person
    (field pipedriveId is populated).
    Data to set is defined in mappings.
    If the person is already up-to-date with any associated lead, does nothing.
    """
    get_logger().debug("Getting lead data from Marketo with id %s", str(lead_id))
    lead = marketo.Lead(get_marketo_client(), lead_id)

    if lead.id is not None:
        person = pipedrive.Person(get_pipedrive_client(), lead.pipedriveId)
        status = "created" if person.id is None else "updated"

        data_changed = False
        for pd_field in PERSON_TO_LEAD:
            data_changed = update_field(lead, person, pd_field, PERSON_TO_LEAD[pd_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            get_logger().debug("Sending to Pipedrive%s", " with id %s" % str(person.id) if person.id is not None else "")
            person.save()

            if not lead.pipedriveId or lead.pipedriveId != person.id:
                get_logger().debug("Updating Pipedrive id in Marketo")
                lead.pipedriveId = person.id
                lead.save()
        else:
            get_logger().debug("Nothing to do")
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


def delete_person_in_pipedrive(lead_pipedrive_id):
    data = get_pipedrive_client().delete_resource("person", lead_pipedrive_id)

    if data:
        ret = {
            "status": "deleted",
            "id": data["id"]
        }

    else:
        ret = {
            "error": "Could not delete person with id %s" % str(lead_pipedrive_id)
        }

    return ret


def create_or_update_organization_in_pipedrive(company_external_id):
    """Creates or updates an organization in Pipedrive with data from the
    company found in Marketo with the given name.
    Update can be performed if the organization and the company share the same name.
    Data to set is defined in mappings.
    If the organization is already up-to-date with any associated company, does nothing.
    """
    get_logger().debug("Getting company data from Marketo with external id %s", str(company_external_id))
    company = marketo.Company(get_marketo_client(), company_external_id, "externalCompanyId")

    if company.id is not None:
        # Search organization in Pipedrive
        organization_id = marketo.get_id_part_from_external(company.externalCompanyId)
        if organization_id:  # Try id
            organization = pipedrive.Organization(get_pipedrive_client(), organization_id)
        if not organization_id or organization.id is None:  # Then name
            organization = pipedrive.Organization(get_pipedrive_client(), company.company, "name")
        if organization.id is None:  # Finally Email domain
            organization = pipedrive.Organization(get_pipedrive_client(), company.website, "email_domain")
        status = "created" if organization.id is None else "updated"

        data_changed = False
        for pd_field in ORGANIZATION_TO_COMPANY:
            data_changed = update_field(company, organization, pd_field, ORGANIZATION_TO_COMPANY[pd_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            get_logger().debug("Sending to Pipedrive%s", " with id %s"
                                                            % str(organization.id) if organization.id is not None else "")
            organization.save()
        else:
            get_logger().debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": organization.id
        }

    else:
        ret = {
            "error": "No company found with external id %s" % str(company_external_id)
        }

    return ret


def create_or_update_lead_in_marketo(person_id):
    """Creates or updates a lead in Marketo with data from the
    person found in Pipedrive with the given id.
    Update can be performed if the person is already associated to a lead
    (field marketoid is populated).
    Data to set is defined in mappings.
    If the lead is already up-to-date with any associated person, does nothing.
    """
    get_logger().debug("Getting person data from Pipedrive with id %s", str(person_id))
    person = pipedrive.Person(get_pipedrive_client(), person_id)

    if person.id is not None:
        lead = marketo.Lead(get_marketo_client(), person.marketoid)
        status = "created" if lead.id is None else "updated"

        data_changed = False
        for mkto_field in LEAD_TO_PERSON:
            data_changed = update_field(person, lead, mkto_field, LEAD_TO_PERSON[mkto_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            get_logger().debug("Sending to Marketo%s", " with id %s" % str(person.id) if person.id is not None else "")
            lead.save()

            if not person.marketoid or int(person.marketoid) != lead.id:
                get_logger().debug("Updating Marketo id in Pipedrive")
                person.marketoid = lead.id
                person.save()
        else:
            get_logger().debug("Nothing to do")
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


def create_or_update_company_in_marketo(organization_id):
    """Creates or updates a company in Marketo with data from the
    organization found in Pipedrive with the given name.
    Update can be performed if the company and the organization share the same name.
    Data to set is defined in mappings.
    If the company is already up-to-date with any associated organization, does nothing.
    """
    get_logger().debug("Getting organization data from Pipedrive with id %s", str(organization_id))
    organization = pipedrive.Organization(get_pipedrive_client(), organization_id)

    if organization.id is not None:
        # Search organization in Pipedrive
        # Try external id
        company = marketo.Company(get_marketo_client(),
                                  marketo.compute_external_id("organization", organization.id), "externalCompanyId")
        if company.id is None:  # Or name
            company = marketo.Company(get_marketo_client(), organization.name, "company")

        data_changed = False
        if company.id is None:
            status = "created"
            external_id = marketo.compute_external_id("organization", organization.id)
            company.externalCompanyId = external_id
            data_changed = True
        else:
            status = "updated"

        for mkto_field in COMPANY_TO_ORGANIZATION:
            data_changed = update_field(organization, company, mkto_field, COMPANY_TO_ORGANIZATION[mkto_field])\
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            get_logger().debug("Sending to Marketo%s", " with id %s" % str(company.id) if company.id is not None else "")
            company.save()
        else:
            get_logger().debug("Nothing to do")
            status = "skipped"

        ret = {
            "status": status,
            "id": company.id,
            "externalId": company.externalCompanyId
        }

    else:
        ret = {
            "error": "No organization found with id %s" % str(organization_id)
        }

    return ret


def delete_lead_in_marketo(pipedrive_marketo_id):
    lead = marketo.Lead(get_marketo_client(), pipedrive_marketo_id)

    lead.toDelete = True
    lead.save()

    if lead.id is not None:
        ret = {
            "status": "Ready for deletion",
            "id": lead.id
        }
    else:
        ret = {
            "error": "Could not prepare lead for deletion with id %s" % str(pipedrive_marketo_id)
        }

    return ret


def create_or_update_opportunity_in_marketo(deal_id):
    """Creates or updates an opportunity and an opportunity role in Marketo with data from the
    deal found in Pipedrive with the given id.
    Update can be performed if the deal is already associated to an opportunity
    (externalOpportunityId is computed from deal id).
    Role cannot be updated (no point for it unless we are mapping the only updateable field: isPrimary).
    Data to set is defined in mappings.
    If the opportunity is already up-to-date with any associated deal, does nothing.
    """
    get_logger().debug("Getting deal data from Pipedrive with id %s", str(deal_id))
    deal = pipedrive.Deal(get_pipedrive_client(), deal_id)

    if deal.id is not None:

        # Filter deals
        pipeline = pipedrive.Pipeline(get_pipedrive_client(), deal.pipeline_id)
        if pipeline.name == "NX Subscription (New and Upsell)":

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

            for mkto_field in DEAL_TO_OPPORTUNITY:
                data_changed = update_field(deal, opportunity, mkto_field, DEAL_TO_OPPORTUNITY[mkto_field])\
                               or data_changed

            if data_changed:
                # Perform the update only if data actually changed
                get_logger().debug("Sending to Marketo (opportunity)%s",
                                      " with id %s" % str(opportunity.id) if opportunity.id is not None else "")
                opportunity.save()
            else:
                get_logger().debug("Nothing to do")
                opportunity_status = "skipped"

            # Role
            role = None
            if deal.contact_person.marketoid is not None:  # Ensure person has existed in Marketo # TODO: create if not?
                # Role will be automatically created or updated using these 3 fields ("dedupeFields")
                role = marketo.Role(get_marketo_client())
                role.externalOpportunityId = opportunity.externalOpportunityId
                role.leadId = deal.contact_person.marketoid
                role.role = deal.champion.title if deal.champion and deal.champion.title else "Default Role"
                role.isPrimary = deal.champion and deal.champion.marketoid == role.leadId
                get_logger().debug("Sending to Marketo (role)")
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
                "status": "skipped",
                "message": "Deal sync not allowed for pipeline %s" % pipeline.name
            }

    else:
        ret = {
            "error": "No deal found with id %s" % str(deal_id)
        }

    return ret


def update_field(from_resource, to_resource, to_field, mapping):
    get_logger().debug("Updating field %s", to_field)

    new_attr = get_new_attr(from_resource, mapping)

    updated = False
    if hasattr(to_resource, to_field):
        old_attr = getattr(to_resource, to_field)
        get_logger().debug("Old attribute for field %s was *%s* and new is *%s*", to_field, old_attr, new_attr)
        if new_attr != old_attr and new_attr is not None and new_attr != "":
            setattr(to_resource, to_field, new_attr)
            updated = True
    else:
        setattr(to_resource, to_field, new_attr)
        updated = True

    return updated


def get_new_attr(from_resource, mapping):
    from_values = []

    if "fields" in mapping:
        for from_field in mapping["fields"]:
            from_attr = getattr(from_resource, from_field)

            # Call pre adapter on field raw value
            if "pre_adapter" in mapping and callable(mapping["pre_adapter"]):
                get_logger().debug("And pre-adapting value %s", from_attr)
                from_attr = mapping["pre_adapter"](from_attr)

            from_values.append(from_attr)
    else:
        # Pass the whole resource
        if "transformer" in mapping and callable(mapping["transformer"]):
            get_logger().debug("And transforming resource %s", from_resource)
            from_attr = mapping["transformer"](from_resource)
            from_values.append(from_attr)

    ret = None
    if len(from_values):
        ret = from_values[0]  # Assume first value is the right one
        if len(from_values) > 1:  # Unless a mode is provided
            if "mode" in mapping:
                if mapping["mode"] == "join":
                    # For join mode assume separator is space
                    ret = " ".join(value for value in from_values if value)
                    ret = ret if ret.strip() else None
                elif mapping["mode"] == "choose":
                    # Get first non empty value
                    ret = next((value for value in from_values if value), None)

    # Call post adapter on result
    if "post_adapter" in mapping and callable(mapping["post_adapter"]):
        get_logger().debug("And post-adapting result %s", ret)
        ret = mapping["post_adapter"](ret)

    return ret
