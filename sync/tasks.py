import mappings
import marketo
import pipedrive
import sync

PIPELINE_FILTER_NAME = 'NX Subscription (New and Upsell)'


def create_or_update_person_in_pipedrive(lead_id):
    """Creates or updates a person in Pipedrive with data from the
    lead found in Marketo with the given id.
    Update can be performed if the lead is already associated to a person
    (field pipedriveId is populated).
    Data to set is defined in mappings.
    If the person is already up-to-date with any associated lead, does nothing.
    """
    sync.get_logger().info('Fetching lead data from Marketo with id=%s', str(lead_id))
    lead = marketo.Lead(sync.get_marketo_client(), lead_id)

    if lead.id is not None:
        person = pipedrive.Person(sync.get_pipedrive_client(), lead.pipedriveId)
        if person.id is None:
            sync.get_logger().info('New person created')
            status = 'created'
        else:
            sync.get_logger().info('Person data fetched from Pipedrive with id=%s', str(person.id))
            status = 'updated'

        data_changed = False
        for pd_field in mappings.PERSON_TO_LEAD:
            data_changed = update_field(lead, person, pd_field, mappings.PERSON_TO_LEAD[pd_field]) \
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.get_logger().info('Sending lead data with id=%s to Pipedrive%s', str(lead_id),
                                   ' for person with id=%s' % str(person.id) if person.id is not None else '')
            person.save()

            if not lead.pipedriveId or lead.pipedriveId != person.id:
                sync.get_logger().info('Updating pipedrive_id=%s in Marketo%s', person.id,
                                       ' (old=%s)' % lead.pipedriveId if lead.pipedriveId else '')
                lead.pipedriveId = person.id
                lead.save()
        else:
            sync.get_logger().info('Nothing to do in Pipedrive for person with id=%s', person.id)
            status = 'skipped'

        ret = {
            'status': status,
            'id': person.id
        }

    else:
        message = 'No lead found in Marketo with id=%s' % str(lead_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
        }

    return ret


def delete_person_in_pipedrive(lead_pipedrive_id):
    sync.get_logger().info('Deleting person in Pipedrive with id=%s', str(lead_pipedrive_id))
    data = sync.get_pipedrive_client().delete_resource('person', lead_pipedrive_id)

    if data:
        ret = {
            'status': 'deleted',
            'id': data['id']
        }

    else:
        message = 'Could not delete person in Pipedrive with id=%s' % str(lead_pipedrive_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
        }

    return ret


def create_or_update_organization_in_pipedrive(company_external_id):
    """Creates or updates an organization in Pipedrive with data from the
    company found in Marketo with the given name.
    Update can be performed if the organization and the company share the same name.
    Data to set is defined in mappings.
    If the organization is already up-to-date with any associated company, does nothing.
    """
    sync.get_logger().info('Fetching company data from Marketo with external_id=%s', str(company_external_id))
    company = marketo.Company(sync.get_marketo_client(), company_external_id, 'externalCompanyId')

    if company.id is not None:
        # Search organization in Pipedrive
        # Try id
        sync.get_logger().debug('Trying to fetch organization data from Pipedrive with marketo_id=%s', company.id)
        organization = pipedrive.Organization(sync.get_pipedrive_client(), company.id, 'marketoid')
        if organization.id is None:  # Then name
            sync.get_logger().debug('Trying to fetch organization data from Pipedrive with name=%s', company.company)
            organization = pipedrive.Organization(sync.get_pipedrive_client(), company.company, 'name')
        if organization.id is None:  # Finally Email domain
            sync.get_logger().debug('Trying to fetch organization data from Pipedrive with email_domain=%s',
                                    company.website)
            organization = pipedrive.Organization(sync.get_pipedrive_client(), company.website, 'email_domain')

        if organization.id is None:
            sync.get_logger().info('New organization created')
            status = 'created'
        else:
            sync.get_logger().info('Organization data fetched from Pipedrive with id=%s', str(organization.id))
            status = 'updated'

        data_changed = False
        for pd_field in mappings.ORGANIZATION_TO_COMPANY:
            data_changed = update_field(company, organization, pd_field, mappings.ORGANIZATION_TO_COMPANY[pd_field]) \
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.get_logger().info('Sending company data with external_id=%s to Pipedrive%s', str(company_external_id),
                                   ' for organization with id=%s' % str(
                                       organization.id) if organization.id is not None else '')
            organization.save()
        else:
            sync.get_logger().info('Nothing to do in Pipedrive for organization with id=%s', organization.id)
            status = 'skipped'

        ret = {
            'status': status,
            'id': organization.id
        }

    else:
        message = 'No company found in Marketo with external_id=%s' % str(company_external_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
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
    sync.get_logger().info('Fetching person data from Pipedrive with id=%s', str(person_id))
    person = pipedrive.Person(sync.get_pipedrive_client(), person_id)

    if person.id is not None:
        lead = marketo.Lead(sync.get_marketo_client(), person.marketoid)
        if lead.id is None:
            sync.get_logger().info('New lead created')
            status = 'created'
        else:
            sync.get_logger().info('Lead data fetched from Marketo with id=%s', str(lead.id))
            status = 'updated'

        data_changed = False
        for mkto_field in mappings.LEAD_TO_PERSON:
            data_changed = update_field(person, lead, mkto_field, mappings.LEAD_TO_PERSON[mkto_field]) \
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.get_logger().info('Sending person data with id=%s to Marketo%s', str(person_id),
                                   ' with id=%s' % str(person.id) if person.id is not None else '')
            lead.save()

            if not person.marketoid or int(person.marketoid) != lead.id:
                sync.get_logger().info('Updating marketo_id=%s in Pipedrive%s', lead.id,
                                       ' (old=%s)' % person.marketoid if person.marketoid else '')
                person.marketoid = lead.id
                person.save()
        else:
            sync.get_logger().info('Nothing to do in Marketo for lead with id=%s', lead.id)
            status = 'skipped'

        ret = {
            'status': status,
            'id': lead.id
        }

    else:
        message = 'No person found with id %s' % str(person_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
        }

    return ret


def create_or_update_company_in_marketo(organization_id):
    """Creates or updates a company in Marketo with data from the
    organization found in Pipedrive with the given name.
    Update can be performed if the company and the organization share the same name.
    Data to set is defined in mappings.
    If the company is already up-to-date with any associated organization, does nothing.
    """
    sync.get_logger().info('Fetching organization data from Pipedrive with id=%s', str(organization_id))
    organization = pipedrive.Organization(sync.get_pipedrive_client(), organization_id)

    if organization.id is not None:
        # Search organization in Pipedrive
        # Try id
        sync.get_logger().debug('Trying to fetch company data from Marketo with id=%s', organization.marketoid)
        company = marketo.Company(sync.get_marketo_client(), organization.marketoid)
        if company.id is None:  # Then external id
            company_external_id = marketo.compute_external_id('organization', organization.id)
            sync.get_logger().debug('Trying to fetch company data from Marketo with external_id=%s', company_external_id)
            company = marketo.Company(sync.get_marketo_client(), company_external_id, 'externalCompanyId')
        if company.id is None:  # Finally name
            sync.get_logger().debug('Trying to fetch company data from Marketo with name=%s', organization.name)
            company = marketo.Company(sync.get_marketo_client(), organization.name, 'company')

        if company.id is None:
            sync.get_logger().info('New company created')
            status = 'created'
            external_id = marketo.compute_external_id('organization', organization.id)
            company.externalCompanyId = external_id
            data_changed = True
        else:
            sync.get_logger().info('Company data fetched from Marketo with id=%s/external_id=%s', str(company.id),
                                   company.externalCompanyId)
            status = 'updated'

        data_changed = False
        for mkto_field in mappings.COMPANY_TO_ORGANIZATION:
            data_changed = update_field(organization, company, mkto_field, mappings.COMPANY_TO_ORGANIZATION[mkto_field]) \
                           or data_changed

        if data_changed:
            # Perform the update only if data actually changed
            sync.get_logger().info('Sending organization data with id=%s to Marketo%s', str(organization_id),
                                   ' with id=%s/external_id=%s' % (
                                   str(company.id), company.externalCompanyId) if company.id is not None else '')
            company.save()
            
            if not organization.marketoid or int(organization.marketoid) != company.id:
                sync.get_logger().info('Updating marketo_id=%s in Pipedrive%s', organization.id,
                                       ' (old=%s)' % organization.marketoid if organization.marketoid else '')
                organization.marketoid = company.id
                organization.save()
        else:
            sync.get_logger().info('Nothing to do in Marketo for company with id=%s/external_id=%s', company.id,
                                   company.externalCompanyId)
            status = 'skipped'

        ret = {
            'status': status,
            'id': company.id,
            'externalId': company.externalCompanyId
        }

    else:
        message = 'No organization found with id %s' % str(organization_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
        }

    return ret


def delete_lead_in_marketo(pipedrive_marketo_id):
    sync.get_logger().info('Deleting person in Marketo with id=%s', str(pipedrive_marketo_id))
    lead = marketo.Lead(sync.get_marketo_client(), pipedrive_marketo_id)

    if lead.id is not None:
        lead.toDelete = True
        lead.save()

        if lead.id is not None:
            ret = {
                'status': 'Ready for deletion',
                'id': lead.id
            }
        else:
            message = 'Could not prepare lead for deletion with id=%s' % str(pipedrive_marketo_id)
            sync.get_logger().error(message)
            ret = {
                'error': message
            }
    else:
        message = 'No lead found with id=%s' % str(pipedrive_marketo_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
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
    sync.get_logger().info('Fetching deal data from Pipedrive with id=%s', str(deal_id))
    deal = pipedrive.Deal(sync.get_pipedrive_client(), deal_id)

    if deal.id is not None:

        # Filter deals
        pipeline = pipedrive.Pipeline(sync.get_pipedrive_client(), deal.pipeline_id)
        if pipeline.name == PIPELINE_FILTER_NAME:

            # Opportunity
            opportunity_external_id = marketo.compute_external_id('deal', deal.id)
            opportunity = marketo.Opportunity(sync.get_marketo_client(), opportunity_external_id,
                                              'externalOpportunityId')

            if opportunity.id is None:
                sync.get_logger().info('New opportunity created')
                opportunity_status = 'created'
                opportunity.externalOpportunityId = opportunity_external_id
                data_changed = True
            else:
                sync.get_logger().info('Opportunity data fetched from Marketo with id=%s/external_id=%s',
                                       str(opportunity.id), opportunity_external_id)
                opportunity_status = 'updated'

            data_changed = False
            for mkto_field in mappings.DEAL_TO_OPPORTUNITY:
                data_changed = update_field(deal, opportunity, mkto_field, mappings.DEAL_TO_OPPORTUNITY[mkto_field]) \
                               or data_changed

            if data_changed:
                # Perform the update only if data actually changed
                sync.get_logger().info('Sending deal data with id=%s to Marketo%s', str(deal_id),
                                       ' for opportunity with id=%s/external_id=%s' % (str(opportunity.id),
                                                                                       opportunity_external_id) if opportunity.id is not None else '')
                opportunity.save()
            else:
                sync.get_logger().info('Nothing to do in Marketo for opportunity with id=%s/external_id=%s',
                                       opportunity.id, opportunity_external_id)
                opportunity_status = 'skipped'

            ret = {
                'opportunity': {
                    'status': opportunity_status,
                    'id': opportunity.id
                }
            }

            # Role
            if deal.contact_person and deal.contact_person.marketoid:  # Ensure person has existed in Marketo # TODO: create if not?
                # Role will be automatically created or updated using these 3 fields ("dedupeFields")
                role = marketo.Role(sync.get_marketo_client())
                role.externalOpportunityId = opportunity.externalOpportunityId
                role.leadId = deal.contact_person.marketoid
                role.role = deal.champion.title if deal.champion and deal.champion.title else 'Default Role'
                role.isPrimary = deal.champion and deal.champion.marketoid == role.leadId
                sync.get_logger().info(
                    'Sending deal data with id=%s to Marketo for role with (externalOpportunityId=%s, leadId=%s, role=%s)',
                    str(deal_id), role.externalOpportunityId, role.leadId, role.role)
                role.save()
                ret['role'] = {'id': role.id}

        else:
            message = 'Deal synchronization with id=%s not enabled for pipeline=%s' % (deal_id, pipeline.name)
            sync.get_logger().info(message)
            ret = {
                'status': 'skipped',
                'message': message
            }

    else:
        message = 'No deal found in Pipedrive with id=%s' % str(deal_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
        }

    return ret


def create_activity_in_pipedrive(lead_id):
    sync.get_logger().info('Fetching lead data from Marketo with id=%s', str(lead_id))
    lead = marketo.Lead(sync.get_marketo_client(), lead_id)

    if lead.id is not None:
        if lead.conversicaLeadOwnerFirstName and lead.conversicaLeadOwnerLastName\
                and lead.pipedriveId:  # If lead has owner and linked to person # TODO: what if incorrect pipedriveID?
            activity = pipedrive.Activity(sync.get_pipedrive_client())
            sync.get_logger().info('New activity created')
            status = 'created'

            for pd_field in mappings.ACTIVITY_TO_LEAD:
                update_field(lead, activity, pd_field, mappings.ACTIVITY_TO_LEAD[pd_field])

            sync.get_logger().info('Sending lead data with id=%s to Pipedrive activity', str(lead_id))
            activity.save()

            ret = {
                'status': status,
                'id': activity.id
            }

        else:
            message = 'Activity synchronization for lead with id=%s not enabled when no owner' % str(lead_id)
            sync.get_logger().info(message)
            ret = {
                'status': 'skipped',
                'message': message
            }
    else:
        message = 'No lead found in Marketo with id=%s' % str(lead_id)
        sync.get_logger().error(message)
        ret = {
            'error': message
        }

    return ret


def update_field(from_resource, to_resource, to_field, mapping):
    sync.get_logger().debug('Updating field=%s from resource=%s to resource=%s', to_field, from_resource, to_resource)

    new_attr = get_new_attr(from_resource, mapping)

    updated = False
    if hasattr(to_resource, to_field):
        old_attr = getattr(to_resource, to_field)
        if new_attr != old_attr and new_attr is not None and new_attr != '':
            sync.get_logger().debug('(old=%s, new=%s) for field=%s', old_attr, new_attr, to_field)
            setattr(to_resource, to_field, new_attr)
            updated = True
    else:
        sync.get_logger().debug('field=%s not found', to_field)
        setattr(to_resource, to_field, new_attr)
        updated = True

    return updated


def get_new_attr(from_resource, mapping):
    from_values = []

    if 'fields' in mapping:
        for from_field in mapping['fields']:
            from_attr = getattr(from_resource, from_field)

            # Call pre adapter on field raw value
            if 'pre_adapter' in mapping and callable(mapping['pre_adapter']):
                sync.get_logger().debug('And pre-adapting value=%s', from_attr)
                from_attr = mapping['pre_adapter'](from_attr)

            from_values.append(from_attr)
    else:
        # Pass the whole resource
        if 'transformer' in mapping and callable(mapping['transformer']):
            sync.get_logger().debug('And transforming resource=%s', from_resource)
            from_attr = mapping['transformer'](from_resource)
            from_values.append(from_attr)

    ret = None
    if len(from_values):
        ret = from_values[0]  # Assume first value is the right one
        if len(from_values) > 1:  # Unless a mode is provided
            if 'mode' in mapping:
                if mapping['mode'] == 'join':
                    # For join mode assume separator is space
                    sync.get_logger().debug('And joining values=%s with space', from_values)
                    ret = ' '.join(value for value in from_values if value)
                    ret = ret if ret.strip() else None
                elif mapping['mode'] == 'choose':
                    # Get first non empty value
                    sync.get_logger().debug('And choosing first non empty value from values=%s', from_values)
                    ret = next((value for value in from_values if value), None)

    # Call post adapter on result
    if 'post_adapter' in mapping and callable(mapping['post_adapter']):
        sync.get_logger().debug('And post-adapting result=%s', ret)
        ret = mapping['post_adapter'](ret)

    return ret
