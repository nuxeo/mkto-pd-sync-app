import requests

import mappings
import marketo
import pipedrive

from sync import app, get_marketo_client, get_pipedrive_client


def create_or_update_person_in_pipedrive(lead_id):
    """
    Create or update a person in Pipedrive. Update can be performed if the lead is already associated to a person
    (field pipedriveId is populated). If the person is already up-to-date with the associated lead, does nothing.
    Data to set is defined in mappings.
    :param lead_id: The lead id to synchronize data from
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Fetching lead data from Marketo with id=%s', str(lead_id))
    lead = marketo.Lead(get_marketo_client(), lead_id)

    if lead.id is not None:
        person = pipedrive.Person(get_pipedrive_client(), lead.pipedriveId)
        if person.id is None:
            app.logger.info('New person created')
            status = 'created'
        else:
            app.logger.info('Person data fetched from Pipedrive with id=%s', str(person.id))
            status = 'updated'

        data_changed = False
        for pd_field in mappings.PERSON_TO_LEAD:
            data_changed = update_field(lead, person, pd_field, mappings.PERSON_TO_LEAD[pd_field]) or data_changed

        if data_changed:
            # Perform the update only if data has actually changed
            app.logger.info('Sending lead data with id=%s to Pipedrive%s', str(lead_id),
                         ' for person with id=%s' % str(person.id) if person.id is not None else '')
            person.save()

            if not lead.pipedriveId or lead.pipedriveId != person.id:
                app.logger.info('Updating pipedrive_id=%s in Marketo%s', person.id,
                             ' (old=%s)' % lead.pipedriveId if lead.pipedriveId else '')
                lead.pipedriveId = person.id
                lead.save()
        else:
            app.logger.info('Nothing to do in Pipedrive for person with id=%s', person.id)
            status = 'skipped'

        response = {
            'status': status,
            'id': person.id
        }

    else:
        message = 'No lead found in Marketo with id=%s' % str(lead_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def delete_person_in_pipedrive(lead_pipedrive_id):
    """
    Delete a person in Pipedrive.
    :param lead_pipedrive_id: The lead related person id to delete
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Deleting person in Pipedrive with id=%s', str(lead_pipedrive_id))
    person = pipedrive.Person(get_pipedrive_client(), lead_pipedrive_id, 'id', False)
    person_id = person.delete()

    if person_id:
        response = {
            'status': 'deleted',
            'id': person_id
        }

    else:
        message = 'Could not delete person in Pipedrive with id=%s' % str(lead_pipedrive_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def create_or_update_organization_in_pipedrive(company_external_id):
    """
    Create or update an organization in Pipedrive. Update can be performed if the organization is already associated to
    a company (field marketoid is populated) or if they share the same name or the same email domain. If the
    organization is already up-to-date with the associated company, does nothing.
    Data to set is defined in mappings.
    :param company_external_id: The company external id to synchronize data from
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Fetching company data from Marketo with external_id=%s', str(company_external_id))
    company = marketo.Company(get_marketo_client(), company_external_id, 'externalCompanyId')

    if company.id is not None:
        organization = find_organization_in_pipedrive(company)
        if organization.id is None:
            app.logger.info('New organization created')
            status = 'created'
        else:
            app.logger.info('Organization data fetched from Pipedrive with id=%s', str(organization.id))
            status = 'updated'

        data_changed = False
        for pd_field in mappings.ORGANIZATION_TO_COMPANY:
            data_changed = update_field(company, organization, pd_field, mappings.ORGANIZATION_TO_COMPANY[pd_field]) \
                           or data_changed

        if data_changed:
            # Perform the update only if data has actually changed
            app.logger.info('Sending company data with external_id=%s to Pipedrive%s', str(company_external_id),
                         ' for organization with id=%s' % str(organization.id)
                         if organization.id is not None else '')
            organization.save()
        else:
            app.logger.info('Nothing to do in Pipedrive for organization with id=%s', organization.id)
            status = 'skipped'

        response = {
            'status': status,
            'id': organization.id
        }

    else:
        message = 'No company found in Marketo with external_id=%s' % str(company_external_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def find_organization_in_pipedrive(company):
    # Search for the organization in Pipedrive
    # Try by id
    app.logger.debug('Trying to fetch organization data from Pipedrive with marketo_id=%s', company.id)
    organization = pipedrive.Organization(get_pipedrive_client(), company.id, 'marketoid')
    if organization.id is None:  # Then name
        app.logger.debug('Trying to fetch organization data from Pipedrive with name=%s', company.company)
        organization = pipedrive.Organization(get_pipedrive_client(), company.company, 'name')
    if organization.id is None:  # Finally Email domain
        app.logger.debug('Trying to fetch organization data from Pipedrive with email_domain=%s',
                      company.website)
        organization = pipedrive.Organization(get_pipedrive_client(), company.website, 'email_domain')
    return organization


def create_or_update_lead_in_marketo(person_id):
    """
    Create or update a lead in Marketo. Update can be performed if the person is already associated to a lead
    (field marketoid is populated). If the lead is already up-to-date with the associated person, does nothing.
    Data to set is defined in mappings.
    :param person_id: The person id to synchronize data from
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Fetching person data from Pipedrive with id=%s', str(person_id))
    person = pipedrive.Person(get_pipedrive_client(), person_id)

    if person.id is not None:
        lead = marketo.Lead(get_marketo_client(), person.marketoid)
        if lead.id is None:
            app.logger.info('New lead created')
            status = 'created'
        else:
            app.logger.info('Lead data fetched from Marketo with id=%s', str(lead.id))
            status = 'updated'

        data_changed = False
        for mkto_field in mappings.LEAD_TO_PERSON:
            data_changed = update_field(person, lead, mkto_field, mappings.LEAD_TO_PERSON[mkto_field]) or data_changed

        if data_changed:
            # Perform the update only if data has actually changed
            app.logger.info('Sending person data with id=%s to Marketo%s', str(person_id),
                         ' with id=%s' % str(person.id) if person.id is not None else '')
            lead.save()

            if not person.marketoid or len(person.marketoid.split(',')) > 1 or int(person.marketoid) != lead.id:
                app.logger.info('Updating marketo_id=%s in Pipedrive%s', lead.id,
                             ' (old=%s)' % person.marketoid if person.marketoid else '')
                person.marketoid = lead.id
                person.save()
        else:
            app.logger.info('Nothing to do in Marketo for lead with id=%s', lead.id)
            status = 'skipped'

        response = {
            'status': status,
            'id': lead.id
        }

    else:
        message = 'No person found with id %s' % str(person_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def create_or_update_company_in_marketo(organization_id):
    """
    Create or update a company in Marketo. Update can be performed if the company is already associated to
    an organization (organization field marketoid is populated) or if the external id comes from the organization id or
    if they share the same name. If the company is already up-to-date with the associated organization, does nothing.
    Data to set is defined in mappings.
    :param organization_id: The organization id to synchronize data from
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Fetching organization data from Pipedrive with id=%s', str(organization_id))
    organization = pipedrive.Organization(get_pipedrive_client(), organization_id)

    if organization.id is not None:
        company = find_company_in_marketo(organization)

        data_changed = False
        if company.id is None:
            app.logger.info('New company created')
            status = 'created'
            external_id = marketo.compute_external_id('organization', organization.id)
            company.externalCompanyId = external_id
            data_changed = True
        else:
            app.logger.info('Company data fetched from Marketo with id=%s/external_id=%s', str(company.id),
                         company.externalCompanyId)
            status = 'updated'

        for mkto_field in mappings.COMPANY_TO_ORGANIZATION:
            data_changed = update_field(organization, company, mkto_field, mappings.COMPANY_TO_ORGANIZATION[mkto_field]) \
                           or data_changed

        if data_changed:
            # Perform the update only if data has actually changed
            app.logger.info('Sending organization data with id=%s to Marketo%s', str(organization_id),
                         ' with id=%s/external_id=%s' % (str(company.id), company.externalCompanyId)
                         if company.id is not None else '')
            company.save()

            if not organization.marketoid \
                    or len(organization.marketoid.split(',')) > 1 or int(organization.marketoid) != company.id:
                app.logger.info('Updating marketo_id=%s in Pipedrive%s', organization.id,
                             ' (old=%s)' % organization.marketoid if organization.marketoid else '')
                organization.marketoid = company.id
                organization.save()
        else:
            app.logger.info('Nothing to do in Marketo for company with id=%s/external_id=%s', company.id,
                         company.externalCompanyId)
            status = 'skipped'

        response = {
            'status': status,
            'id': company.id,
            'externalId': company.externalCompanyId
        }

    else:
        message = 'No organization found with id %s' % str(organization_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def find_company_in_marketo(organization):
    # Search for the company in Marketo
    # Try id
    app.logger.debug('Trying to fetch company data from Marketo with id=%s', organization.marketoid)
    company = marketo.Company(get_marketo_client(), organization.marketoid)
    if company.id is None:  # Then external id  # TODO remove because useless?
        company_external_id = marketo.compute_external_id('organization', organization.id)
        app.logger.debug('Trying to fetch company data from Marketo with external_id=%s', company_external_id)
        company = marketo.Company(get_marketo_client(), company_external_id, 'externalCompanyId')
    if company.id is None:  # Finally name
        app.logger.debug('Trying to fetch company data from Marketo with name=%s', organization.name)
        company = marketo.Company(get_marketo_client(), organization.name, 'company')
    return company


def delete_lead_in_marketo(pipedrive_marketo_id):
    """
    Delete a lead in Marketo.
    :param pipedrive_marketo_id: The person related lead id to delete
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Deleting person in Marketo with id=%s', str(pipedrive_marketo_id))
    lead = marketo.Lead(get_marketo_client(), pipedrive_marketo_id)

    if lead.id is not None:
        lead.toDelete = True
        lead.save()

        if lead.id is not None:
            response = {
                'status': 'Ready for deletion',
                'id': lead.id
            }
        else:
            message = 'Could not prepare lead for deletion with id=%s' % str(pipedrive_marketo_id)
            app.logger.error(message)
            response = {
                'error': message
            }
    else:
        message = 'No lead found with id=%s' % str(pipedrive_marketo_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def create_or_update_opportunity_in_marketo(deal_id):
    """
    Create or update an opportunity in Marketo. Update can be performed if the opportunity external id comes from the
    deal id. If the opportunity is already up-to-date with the associated deal, does nothing.
    Role cannot be updated (the only updateable field would be isPrimary).
    Data to set is defined in mappings.
    :param deal_id: The deal id to synchronize data from
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Fetching deal data from Pipedrive with id=%s', str(deal_id))
    deal = pipedrive.Deal(get_pipedrive_client(), deal_id)

    if deal.id is not None:

        # Filter deals
        pipeline = pipedrive.Pipeline(get_pipedrive_client(), deal.pipeline_id)
        if pipeline.name in mappings.PIPELINE_FILTER_NAMES:

            # Opportunity
            opportunity_external_id = marketo.compute_external_id('deal', deal.id)
            opportunity = marketo.Opportunity(get_marketo_client(), opportunity_external_id,
                                              'externalOpportunityId')

            data_changed = False
            if opportunity.id is None:
                app.logger.info('New opportunity created')
                opportunity_status = 'created'
                opportunity.externalOpportunityId = opportunity_external_id
                data_changed = True
            else:
                app.logger.info('Opportunity data fetched from Marketo with id=%s/external_id=%s',
                             str(opportunity.id), opportunity_external_id)
                opportunity_status = 'updated'

            for mkto_field in mappings.OPPORTUNITY_TO_DEAL:
                data_changed = update_field(deal, opportunity, mkto_field, mappings.OPPORTUNITY_TO_DEAL[mkto_field]) \
                               or data_changed

            if data_changed:
                # Perform the update only if data has actually changed
                app.logger.info('Sending deal data with id=%s to Marketo%s', str(deal_id),
                             ' for opportunity with id=%s/external_id=%s'
                             % (str(opportunity.id), opportunity_external_id)
                             if opportunity.id is not None else '')
                opportunity.save()
            else:
                app.logger.info('Nothing to do in Marketo for opportunity with id=%s/external_id=%s',
                             opportunity.id, opportunity_external_id)
                opportunity_status = 'skipped'

            response = {
                'opportunity': {
                    'status': opportunity_status,
                    'id': opportunity.id
                }
            }

            # Role
            if deal.contact_person and deal.contact_person.marketoid:  # Ensure person has been synced # TODO create if not?
                # Role will automatically be created or updated using these 3 fields ("dedupeFields")
                role = marketo.Role(get_marketo_client())
                role.externalOpportunityId = opportunity.externalOpportunityId
                role.leadId = deal.contact_person.marketoid
                role.role = deal.champion.title if deal.champion and deal.champion.title else 'Default Role'
                role.isPrimary = deal.champion and deal.champion.marketoid == role.leadId
                app.logger.info(
                    'Sending deal data with id=%s to Marketo for role with (externalOpportunityId=%s, leadId=%s, role=%s)',
                    str(deal_id), role.externalOpportunityId, role.leadId, role.role)
                role.save()
                response['role'] = {'id': role.id}

        else:
            message = 'Deal synchronization with id=%s not enabled for pipeline=%s' % (deal_id, pipeline.name)
            app.logger.info(message)
            response = {
                'status': 'skipped',
                'message': message
            }

    else:
        message = 'No deal found in Pipedrive with id=%s' % str(deal_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def create_activity_in_pipedrive(lead_id):
    """
    Create an activity in Pipedrive.
    Data to set is defined in mappings.
    :param lead_id: The lead id to synchronize data from
    :return: A custom response object containing the synchronized entity status and id
    """
    app.logger.info('Fetching lead data from Marketo with id=%s', str(lead_id))
    lead = marketo.Lead(get_marketo_client(), lead_id)

    if lead.id is not None:
        activity = pipedrive.Activity(get_pipedrive_client())
        app.logger.info('New activity created')
        status = 'created'

        for pd_field in mappings.ACTIVITY_TO_LEAD:
            update_field(lead, activity, pd_field, mappings.ACTIVITY_TO_LEAD[pd_field])

        app.logger.info('Sending lead data with id=%s to Pipedrive activity', str(lead_id))
        activity.save()

        response = {
            'status': status,
            'id': activity.id
        }
    else:
        message = 'No lead found in Marketo with id=%s' % str(lead_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def compute_organization_in_pipedrive(organization_id):
    app.logger.info('Fetching organization data from Pipedrive with id=%s', str(organization_id))
    organization = pipedrive.Organization(get_pipedrive_client(), organization_id)

    if organization.id is not None:
        status = 'skipped'
        # Use keys to avoid conflicts in field names and keys
        if organization.b97ac2f12d2071c4c5efbf3a89c812c970f04af1\
                and organization.b97ac2f12d2071c4c5efbf3a89c812c970f04af1 in mappings.COUNTRY_TO_REGION:
            old_region = organization.e1cfd37b3fa5a3847f662fb7a3728c181b6dac15
            new_region = mappings.COUNTRY_TO_REGION[organization.b97ac2f12d2071c4c5efbf3a89c812c970f04af1]
            if new_region and new_region != old_region:
                organization.e1cfd37b3fa5a3847f662fb7a3728c181b6dac15 = new_region
                organization.save()
                status = 'updated'

        response = {
            'status': status
        }

    else:
        message = 'No organization found with id %s' % str(organization_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def compute_deal_in_pipedrive(deal_id):
    app.logger.info('Fetching deal data from Pipedrive with id=%s', str(deal_id))
    deal = pipedrive.Deal(get_pipedrive_client(), deal_id)

    if deal.id is not None:
        status = 'skipped'
        if deal.status in ('won', 'lost'):
            url = app.config['SLACK_WEBHOOK_URL']
            payload = {
                'attachments': [
                    {
                        'fallback': 'New Deal {}: <{}/deal/{}|Pipedrive Record>'
                            .format(deal.status, app.config['PD_APP_URL'], deal.id),
                        'pretext': 'New Deal {}: <{}/deal/{}|Pipedrive Record>'
                            .format(deal.status, app.config['PD_APP_URL'], deal.id),
                        'text': '{} has {} the deal {}'.format(deal.owner.name, deal.status, deal.title),
                        'color': 'good' if deal.status == 'won' else 'danger',
                        'fields': [
                            {
                                'title': 'Details',
                                'value': ('InternalPO : PO#{}\n'
                                          'Company: {}\n'
                                          'Value : {} {}\n'
                                          'Start Date : {}\n'
                                          'Duration (month) : {}\n'
                                          'Reseller (if any) : {}\n'
                                          'Won Time : {}\n'
                                          'Status : {}').format(deal.id,
                                                                deal.organization.name,
                                                                deal.currency,
                                                                deal.value,
                                                                deal.contract_start_date,
                                                                deal.duration,
                                                                '',
                                                                deal.won_time,
                                                                deal.status),
                                'short': False
                            }
                        ]
                    }
                ]
            }

            r = requests.post(url, json=payload)
            r.raise_for_status()
            status = r.content

        response = {
            'status': status
        }

    else:
        message = 'No deal found with id %s' % str(deal_id)
        app.logger.error(message)
        response = {
            'error': message
        }

    return response


def update_field(from_entity, to_entity, to_field, mapping):
    """
    Update an entity attribute if and only if the new value is different from the previous one and not empty.
    :param from_entity: The entity to get the attribute value from
    :param to_entity: The entity to update
    :param to_field: The attribute name
    :param mapping: The attribute mapping
    :return: The update status
    """
    app.logger.debug('Updating field=%s from entity=%s to entity=%s', to_field, from_entity, to_entity)

    new_attr = get_new_attr(from_entity, mapping)

    updated = False
    if hasattr(to_entity, to_field):
        old_attr = getattr(to_entity, to_field)
        if new_attr != old_attr and new_attr is not None and new_attr != '':
            app.logger.info('(old=%s, new=%s) for field=%s', old_attr, new_attr, to_field)
            setattr(to_entity, to_field, new_attr)
            updated = True
    else:
        app.logger.info('field=%s not found', to_field)
        setattr(to_entity, to_field, new_attr)
        updated = True

    return updated


def get_new_attr(from_entity, mapping):
    """
    Return the new attribute value after it has been processed with a mapping.
    :param from_entity: The entity to get the attribute value from
    :param mapping: The attribute mapping
    :return: The new attribute value
    """
    from_values = []

    if 'fields' in mapping:
        for from_field in mapping['fields']:
            from_attr = getattr(from_entity, from_field)

            # Call pre adapter on field raw value
            if 'pre_adapter' in mapping and callable(mapping['pre_adapter']):
                app.logger.debug('And pre-adapting value=%s', from_attr)
                from_attr = mapping['pre_adapter'](from_attr)

            from_values.append(from_attr)
    else:
        # Pass the entity object
        if 'transformer' in mapping and callable(mapping['transformer']):
            app.logger.debug('And transforming entity=%s', from_entity)
            from_attr = mapping['transformer'](from_entity)
            from_values.append(from_attr)

    new_attr = None
    if len(from_values):
        new_attr = from_values[0]  # Assume first value is the one to keep
        if len(from_values) > 1:  # Unless a mode is provided
            if 'mode' in mapping:
                if mapping['mode'] == 'join':
                    # For join mode assume separator is space
                    app.logger.debug('And joining values=%s with space', from_values)
                    new_attr = ' '.join(value for value in from_values if value)
                    new_attr = new_attr if new_attr.strip() else None
                elif mapping['mode'] == 'choose':
                    # Get first non empty value
                    app.logger.debug('And choosing first non empty value from values=%s', from_values)
                    new_attr = next((value for value in from_values if value), None)

    # Call post adapter on result
    if 'post_adapter' in mapping and callable(mapping['post_adapter']):
        app.logger.debug('And post-adapting result=%s', new_attr)
        new_attr = mapping['post_adapter'](new_attr)

    return new_attr
