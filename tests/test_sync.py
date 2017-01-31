# coding=UTF-8
from .context import sync

import datetime
import json
import mock
import os
import re
import requests
import unittest

from google.appengine.ext import ndb, testbed

RESOURCE_MAPPING = {
    '/v1/leads/describe.json':               {'{}': 'resources/leadFields.json'},
    '/v1/leads.json':                        {
        "{'filterType': 'id', 'filterValues': '10'}": 'resources/lead10.json',
        "{'filterType': 'id', 'filterValues': '20'}": 'resources/lead20.json',
        "{'filterType': 'id', 'filterValues': '30'}": 'resources/lead30.json',
        "{'filterType': 'id', 'filterValues': '40'}": 'resources/lead40.json'
    },
    '/v1/personFields':                      {'{}': 'resources/personFields.json'},
    '/v1/persons/10':                        {'{}': 'resources/person10.json'},
    '/v1/persons/20':                        {'{}': 'resources/person20.json'},
    '/v1/persons/30':                        {'{}': 'resources/person30.json'},
    '/v1/userFields':                        {'{}': 'resources/userFields.json'},
    '/v1/users/find':                        {"{'term': u'Helene Jonin'}": 'resources/userHeleneJonin.json'},
    '/v1/users/1628545':                     {'{}': 'resources/user1628545.json'},
    '/v1/companies/describe.json':           {'{}': 'resources/companyFields.json'},
    '/v1/companies.json':                    {
        "{'filterType': 'externalCompanyId', 'filterValues': 'testFlaskCompany'}"      : 'resources/company10.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-10'}"    : 'resources/empty.json',
        "{'filterType': 'company', 'filterValues': 'Test Flask Organization'}"         : 'resources/empty.json',
        "{'filterType': 'id', 'filterValues': '20'}"                                   : 'resources/company20.json',
        "{'filterType': 'id', 'filterValues': '30'}"                                   : 'resources/company30.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-20'}"    : 'resources/company20.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-30'}"    : 'resources/company30.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'mkto-lead-company-40'}"  : 'resources/empty.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-50'}"    : 'resources/empty.json',
        "{'filterType': 'company', 'filterValues': 'Test Flask Unlinked Organization'}": 'resources/company50.json'
    },
    '/v1/organizationFields':                {'{}': 'resources/organizationFields.json'},
    '/v1/organizations/find':                {"{'term': u'Test Flask Company'}": 'resources/emptyPdFind.json'},
    '/v1/organizations/10':                  {'{}': 'resources/organization10.json'},
    '/v1/organizations/20':                  {'{}': 'resources/organization20.json'},
    '/v1/organizations/30':                  {'{}': 'resources/organization30.json'},
    '/v1/organizations/50':                  {'{}': 'resources/organization50.json'},
    '/v1/organizations':                     {
        "{'filter_id': 1}": 'resources/empty.json',
        "{'filter_id': 2}": 'resources/organization20_filter.json',
        "{'filter_id': 3}": 'resources/organization30_filter.json'
    },
    '/v1/dealFields':                        {'{}': 'resources/dealFields.json'},
    '/v1/deals/10':                          {'{}': 'resources/deal10.json'},
    '/v1/deals/20':                          {'{}': 'resources/deal20.json'},
    '/v1/deals/30':                          {'{}': 'resources/deal30.json'},
    '/v1/pipelines/12':                      {'{}': 'resources/pipeline12.json'},
    '/v1/opportunities/describe.json':       {'{}': 'resources/opportunityFields.json'},
    '/v1/opportunities/roles/describe.json': {'{}': 'resources/opportunityRoleFields.json'},
    '/v1/opportunities.json':                {
        "{'filterType': 'externalOpportunityId', 'filterValues': 'pd-deal-10'}": 'resources/empty.json',
        "{'filterType': 'externalOpportunityId', 'filterValues': 'pd-deal-20'}": 'resources/opportunity20.json',
        "{'filterType': 'externalOpportunityId', 'filterValues': 'pd-deal-30'}": 'resources/opportunity30.json'
    },
    '/v1/stages/34':                         {'{}': 'resources/stage34.json'},
    '/v1/activityFields':                    {'{}': 'resources/activityFields.json'},
    '/v1/filters':                           {'{}': 'resources/filters.json'},
    '/v1/filters/1':                         {'{}': 'resources/filter1.json'}
}


def side_effect_get(*args, **kwargs):
    rv = mock.MagicMock(spec=requests.Response)
    params = kwargs['params']
    if 'filterType' in params and 'filterValues' in params:
        value = "{'filterType': '%s', 'filterValues': '%s'}" % (params['filterType'], params['filterValues'])
    else:
        value = str(params)
    endpoint = [key for key in RESOURCE_MAPPING if re.match('^.*%s$' % key, args[0])][0]
    url = RESOURCE_MAPPING[endpoint][value]
    rv.url = '%s -> %s' % (args[0], url)
    with open(os.path.join(os.path.dirname(__file__), url)) as f:
        rv.json.return_value = json.load(f)
    f.closed
    return rv


def side_effect_post(*args, **kwargs):
    rv = mock.MagicMock(spec=requests.Response)
    payload = kwargs['data']
    if 'filterType' in payload and 'filterValues' in payload:
        value = "{'filterType': '%s', 'filterValues': '%s'}" % (payload['filterType'], payload['filterValues'])
    else:
        value = str(payload)
    endpoint = [key for key in RESOURCE_MAPPING if re.match('^.*%s$' % key, args[0])][0]
    url = RESOURCE_MAPPING[endpoint][value]
    rv.url = '%s -> %s' % (args[0], url)
    with open(os.path.join(os.path.dirname(__file__), url)) as f:
        rv.json.return_value = json.load(f)
    f.closed
    return rv


def side_effect_put(*args, **kwargs):
    rv = mock.MagicMock(spec=requests.Response)
    value = '{}'
    endpoint = [key for key in RESOURCE_MAPPING if re.match('^.*%s$' % key, args[0])][0]
    url = RESOURCE_MAPPING[endpoint][value]
    rv.url = '%s -> %s' % (args[0], url)
    with open(os.path.join(os.path.dirname(__file__), url)) as f:
        rv.json.return_value = json.load(f)
    f.closed
    return rv


saved_instances = {}


def mock_save_lead(lead):
    if not lead.id:
        lead.id = 15
    saved_instances['lead' + str(lead.id)] = lead


def mock_save_company(company):
    if not company.id:
        company.id = 15
    saved_instances['company' + str(company.id)] = company


def mock_save_opportunity(opportunity):
    if not opportunity.id:
        opportunity.id = 15
    saved_instances['opportunity' + str(opportunity.id)] = opportunity


def mock_save_role(role):
    if not role.id:
        role.id = 15
    saved_instances['role' + str(role.id)] = role


def mock_save_person(person):
    if not person.id:
        person.id = 15
    saved_instances['person' + str(person.id)] = person


def mock_save_organization(organization):
    if not organization.id:
        organization.id = 15
    saved_instances['organization' + str(organization.id)] = organization


def mock_save_activity(activity):
    if not activity.id:
        activity.id = 15
    saved_instances['activity' + str(activity.id)] = activity


def setup_get_filter_mock(mock_get_filter, filter_id):
    with open(os.path.join(os.path.dirname(__file__), 'resources/filter%s.json' % str(filter_id))) as f:
        mock_get_filter.return_value = json.load(f)['data']
    f.closed


@mock.patch.object(requests.Session, 'get', side_effect=side_effect_get)
@mock.patch.object(requests.Session, 'post', side_effect=side_effect_post)
@mock.patch.object(requests.Session, 'put', side_effect=side_effect_put)
@mock.patch.object(sync.marketo.Lead, 'save', mock_save_lead)
@mock.patch.object(sync.marketo.Company, 'save', mock_save_company)
@mock.patch.object(sync.marketo.Opportunity, 'save', mock_save_opportunity)
@mock.patch.object(sync.marketo.Role, 'save', mock_save_role)
@mock.patch.object(sync.pipedrive.Person, 'save', mock_save_person)
@mock.patch.object(sync.pipedrive.Organization, 'save', mock_save_organization)
@mock.patch.object(sync.pipedrive.Activity, 'save', mock_save_activity)
@mock.patch('sync.sync.marketo.MarketoClient._get_auth_token')
class SyncTestCase(unittest.TestCase):
    AUTHENTICATION_PARAM = '?api_key=' + sync.app.config['FLASK_AUTHORIZED_KEYS']['test']

    @classmethod
    @mock.patch('sync.sync.marketo.MarketoClient._get_auth_token')
    def setUpClass(cls, mock_mkto_get_token):
        cls.context = sync.app.app_context()
        cls.context.push()

        # First, create an instance of the Testbed class.
        cls.testbed = testbed.Testbed()
        # Then activate the testbed, which prepares the service stubs for use.
        cls.testbed.activate()
        # Next, declare which service stubs you want to use.
        cls.testbed.init_datastore_v3_stub()
        cls.testbed.init_memcache_stub()
        # Clear ndb's in-context cache between tests.
        # This prevents data from leaking between tests.
        # Alternatively, you could disable caching by
        # using ndb.get_context().set_cache_policy(False)
        ndb.get_context().clear_cache()

        # root_path must be set the the location of queue.yaml.
        # Otherwise, only the 'default' queue will be available.
        cls.testbed.init_taskqueue_stub(root_path='..')
        cls.taskqueue_stub = cls.testbed.get_stub(testbed.TASKQUEUE_SERVICE_NAME)

        cls.mkto = sync.marketo.MarketoClient('', '', '', '')
        cls.pd = sync.pipedrive.PipedriveClient('')

    @classmethod
    def tearDownClass(cls):
        cls.context.pop()

        cls.testbed.deactivate()

    def test_authentication_error(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/1')
            self.assertEqual(rv.status_code, 401)
            data = json.loads(rv.data)
            self.assertEqual(data['message'], 'Authentication required')

    def test_flow(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/1' + self.AUTHENTICATION_PARAM)
            data = json.loads(rv.data)
            self.assertTrue(data['message'])

            tasks = self.taskqueue_stub.get_filtered_tasks()
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].name, 'task1')

    # Test tasks

    def test_create_person_and_organization_from_company_in_pipedrive(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        lead_to_sync = sync.marketo.Lead(self.mkto, 10)
        self.assertIsNone(lead_to_sync.pipedriveId)  # Pipedrive id is empty

        company_to_sync = sync.marketo.Company(self.mkto, lead_to_sync.externalCompanyId, 'externalCompanyId')
        found_organization = sync.tasks.find_organization_in_pipedrive(company_to_sync)
        self.assertIsNone(found_organization.id)  # Organization does not exist

        rv = sync.tasks.create_or_update_person_in_pipedrive(lead_to_sync.id)

        # Test Lead sync
        synced_lead = saved_instances['lead' + str(lead_to_sync.id)]
        self.assertIsNotNone(synced_lead.pipedriveId)  # Pipedrive id has been updated

        # Person has been created
        synced_person = saved_instances['person' + str(rv['id'])]
        self.assertIsNotNone(synced_person.id)
        self.assertEquals(rv['status'], 'created')

        # Test values
        self.assertEquals(synced_person.name, 'Test Flask Lead')
        self.assertEquals(synced_person.email, 'lead@testflask.com')
        self.assertIsNotNone(synced_person.org_id)
        self.assertEquals(synced_person.title, 'Manager')
        self.assertEquals(synced_person.phone, '9876543210')
        self.assertEquals(synced_person.inferred_country, 'Italy')
        self.assertEquals(synced_person.lead_source, 'Organic Search')
        self.assertEquals(synced_person.owner_id, 1628545)
        self.assertEquals(synced_person.created_date, '2016-01-01')
        self.assertEquals(synced_person.state, 'Italy')
        self.assertEquals(synced_person.city, 'Milano')
        self.assertEquals(synced_person.lead_score, 10)
        self.assertEquals(synced_person.date_sql, '2016-11-16')
        self.assertEquals(synced_person.lead_status, 'Recycled')

        # Test Organization sync
        synced_organization = saved_instances['organization' + str(synced_person.org_id)]  # Organization has been created

        # Test values
        self.assertEquals(synced_organization.name, 'Test Flask Company')
        self.assertEquals(synced_organization.address, '11th St')
        self.assertEquals(synced_organization.city, 'New York')
        self.assertEquals(synced_organization.state, 'NY')
        self.assertEquals(synced_organization.b97ac2f12d2071c4c5efbf3a89c812c970f04af1, 'United States')
        self.assertEquals(synced_organization.company_phone, '0123456789')
        self.assertEquals(synced_organization.industry, 'Finance')
        self.assertEquals(synced_organization.annual_revenue, 1000000)
        self.assertEquals(synced_organization.number_of_employees, 10)
        self.assertEquals(synced_organization.marketoid, '10')

    @mock.patch('sync.sync.pipedrive.PipedriveClient.get_organization_marketoid_filter')
    def test_update_person_and_linked_organization_in_pipedrive(self, mock_get_filter, mock_mkto_get_token, mock_put, mock_post, mock_get):
        setup_get_filter_mock(mock_get_filter, 2)

        lead_to_sync = sync.marketo.Lead(self.mkto, 20)

        # Lead has already been synced
        self.assertIsNotNone(lead_to_sync.pipedriveId)
        person_to_sync = sync.pipedrive.Person(self.pd, lead_to_sync.pipedriveId)
        self.assertIsNotNone(person_to_sync.id)

        company_to_sync = sync.marketo.Company(self.mkto, lead_to_sync.externalCompanyId, 'externalCompanyId')
        found_organization = sync.tasks.find_organization_in_pipedrive(company_to_sync)
        self.assertIsNotNone(found_organization.id)  # Organization exists
        found_organization = sync.pipedrive.Organization(self.pd, company_to_sync.id, 'marketoid')
        self.assertIsNotNone(found_organization.id)  # Organization has been found with marketo id

        rv = sync.tasks.create_or_update_person_in_pipedrive(lead_to_sync.id)

        # Test Lead sync

        # Person has been updated
        synced_person = saved_instances['person' + str(lead_to_sync.pipedriveId)]
        self.assertEquals(rv['status'], 'updated')
        self.assertEquals(rv['id'], synced_person.id)

        # Test values
        self.assertEquals(synced_person.name, 'Test Linked Flask Lead')
        self.assertEquals(synced_person.email, 'lead@testlinkedflask.com')
        self.assertIsNotNone(synced_person.org_id)
        self.assertEquals(synced_person.title, 'Accountant')
        self.assertEquals(synced_person.phone, '1357924680')
        self.assertEquals(synced_person.inferred_country, 'Spain')
        self.assertEquals(synced_person.lead_source, 'Product')
        self.assertEquals(synced_person.owner_id, 1628545)
        self.assertEquals(synced_person.created_date, '2016-01-02')
        self.assertEquals(synced_person.state, 'Spain')
        self.assertEquals(synced_person.city, 'Barcelona')
        self.assertEquals(synced_person.lead_score, 13)
        self.assertEquals(synced_person.date_sql, '2016-11-16')
        self.assertEquals(synced_person.lead_status, 'Prospect')

        # Test Organization sync
        synced_organization = saved_instances['organization' + str(found_organization.id)]  # Organization has been updated

        # Test values
        self.assertEquals(synced_organization.name, 'Test Flask Linked Company')

    @mock.patch('sync.sync.pipedrive.PipedriveClient.get_organization_marketoid_filter')
    def test_update_person_in_pipedrive_no_change(self, mock_get_filter, mock_mkto_get_token, mock_put, mock_post, mock_get):
        setup_get_filter_mock(mock_get_filter, 3)

        lead_to_sync = sync.marketo.Lead(self.mkto, 30)

        # Lead has already been synced
        self.assertIsNotNone(lead_to_sync.pipedriveId)
        person_to_sync = sync.pipedrive.Person(self.pd, lead_to_sync.pipedriveId)
        self.assertIsNotNone(person_to_sync.id)

        company_to_sync = sync.marketo.Company(self.mkto, lead_to_sync.externalCompanyId, 'externalCompanyId')
        found_organization = sync.tasks.find_organization_in_pipedrive(company_to_sync)
        self.assertIsNotNone(found_organization.id)  # Organization exists
        found_organization = sync.pipedrive.Organization(self.pd, company_to_sync.id, 'marketoid')
        self.assertIsNotNone(found_organization.id)  # Organization has been found with marketo id

        rv = sync.tasks.create_or_update_person_in_pipedrive(lead_to_sync.id)

        # Test return data
        self.assertEquals(rv['status'], 'skipped')

    def test_create_person_in_pipedrive_and_company_from_form_fields_in_marketo(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        lead_to_sync = sync.marketo.Lead(self.mkto, 40)
        self.assertIsNone(lead_to_sync.pipedriveId)  # Pipedrive id is empty
        self.assertIsNone(lead_to_sync.externalCompanyId)

        rv = sync.tasks.create_or_update_person_in_pipedrive(lead_to_sync.id)

        # Test Lead sync
        synced_lead = saved_instances['lead' + str(lead_to_sync.id)]
        self.assertIsNotNone(synced_lead.pipedriveId)  # Pipedrive id has been updated

        # Person has been created
        synced_person = saved_instances['person' + str(rv['id'])]
        self.assertIsNotNone(synced_person.id)
        self.assertEquals(rv['status'], 'created')

        # Test values
        self.assertEquals(synced_person.name, 'Test Other Flask Lead')
        self.assertEquals(synced_person.email, 'lead2@testflask.com')

        created_company = saved_instances['company15']  # Company has been created
        self.assertIsNotNone(created_company.id)
        self.assertIsNotNone(synced_lead.externalCompanyId)  # External company id has been updated

        # Organization cannot be created because company not actually saved
        # self.assertIsNotNone(synced_person.org_id)
        # self.assertEquals(synced_person.organization.name, 'another-flask-company.com')
        # self.assertEquals(synced_person.organization.b97ac2f12d2071c4c5efbf3a89c812c970f04af1, 'Canada')

    def test_create_lead_and_company_from_organization_in_marketo(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        person_to_sync = sync.pipedrive.Person(self.pd, 10)
        self.assertIsNone(person_to_sync.marketoid)  # Marketo id is empty

        organization_to_sync = sync.pipedrive.Organization(self.pd, person_to_sync.org_id)
        found_company = sync.tasks.find_company_in_marketo(organization_to_sync)
        self.assertIsNone(found_company.id)  # Company does not exist

        rv = sync.tasks.create_or_update_lead_in_marketo(person_to_sync.id)

        # Test Person sync
        synced_person = saved_instances['person' + str(person_to_sync.id)]
        self.assertIsNotNone(synced_person.marketoid)  # Marketo id has been updated

        # Lead has been created
        synced_lead = saved_instances['lead' + str(rv['id'])]
        self.assertIsNotNone(synced_lead.id)
        self.assertEquals(rv['status'], 'created')

        # Test values
        self.assertEquals(synced_lead.firstName, 'Test Flask')
        self.assertEquals(synced_lead.lastName, 'Person')
        self.assertEquals(synced_lead.email, 'person@testflask.com')
        self.assertIsNotNone(synced_lead.externalCompanyId)
        self.assertEquals(synced_lead.title, 'Dev')
        self.assertEquals(synced_lead.phone, '5647382910')
        self.assertEquals(synced_lead.leadSource, 'Direct Traffic')
        self.assertEquals(synced_lead.conversicaLeadOwnerEmail, 'hjonin@nuxeo.com')
        self.assertEquals(synced_lead.conversicaLeadOwnerFirstName, 'Helene')
        self.assertEquals(synced_lead.conversicaLeadOwnerLastName, 'Jonin')
        self.assertEquals(synced_lead.leadStatus, 'Disqualified')
        self.assertEqual(synced_lead.leadCountry, 'Germany')

        # Test Company sync
        synced_company = saved_instances['company' + str(15)]  # Company has been created

        # Test values
        self.assertEquals(synced_company.company, 'Test Flask Organization')
        self.assertEquals(synced_company.billingStreet, 'Rue Mouffetard')
        self.assertEquals(synced_company.billingCity, u'Paris')
        self.assertEquals(synced_company.billingState, 'France')
        self.assertEquals(synced_company.billingCountry, 'France')
        self.assertEquals(synced_company.mainPhone, '0192837465')
        self.assertEquals(synced_company.industry, 'Consulting')
        self.assertEquals(synced_company.annualRevenue, 2000000)
        self.assertEquals(synced_company.numberOfEmployees, 20)

    def test_update_lead_and_linked_company_in_marketo(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        person_to_sync = sync.pipedrive.Person(self.pd, 20)

        # Person has already been synced
        self.assertIsNotNone(person_to_sync.marketoid)
        lead_to_sync = sync.marketo.Lead(self.mkto, person_to_sync.marketoid)
        self.assertIsNotNone(lead_to_sync.id)

        organization_to_sync = sync.pipedrive.Organization(self.pd, person_to_sync.org_id)
        found_company = sync.tasks.find_company_in_marketo(organization_to_sync)
        self.assertIsNotNone(found_company.id)  # Company exists
        found_company = sync.marketo.Company(self.mkto, organization_to_sync.marketoid)
        self.assertIsNotNone(found_company.id)  # Company has been found with marketo id

        rv = sync.tasks.create_or_update_lead_in_marketo(person_to_sync.id)

        # Test Person sync

        # Lead has been updated
        synced_lead = saved_instances['lead' + str(person_to_sync.marketoid)]
        self.assertEquals(rv['status'], 'updated')
        self.assertEquals(rv['id'], synced_lead.id)

        # Test values
        self.assertEquals(synced_lead.firstName, 'Test Linked Flask')
        self.assertEquals(synced_lead.lastName, 'Person')
        self.assertEquals(synced_lead.email, 'person@testlinkedflask.com')
        self.assertEquals(synced_lead.externalCompanyId, 'pd-organization-20')
        self.assertEquals(synced_lead.title, 'Consultant')
        self.assertEquals(synced_lead.phone, '2468013579')
        self.assertEquals(synced_lead.leadSource, 'Web Referral')
        self.assertEquals(synced_lead.conversicaLeadOwnerEmail, 'hjonin@nuxeo.com')
        self.assertEquals(synced_lead.conversicaLeadOwnerFirstName, 'Helene')
        self.assertEquals(synced_lead.conversicaLeadOwnerLastName, 'Jonin')
        self.assertEquals(synced_lead.leadStatus, 'MQL')
        self.assertEqual(synced_lead.leadCountry, 'United Kingdom')

        # Test Company sync
        synced_company = saved_instances['company' + str(found_company.id)]  # Company has been updated

        # Test values
        self.assertEquals(synced_company.company, 'Test Flask Linked Organization')

    def test_update_lead_in_marketo_no_change(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        person_to_sync = sync.pipedrive.Person(self.pd, 30)

        # Person has already been synced
        self.assertIsNotNone(person_to_sync.marketoid)
        lead_to_sync = sync.marketo.Lead(self.mkto, person_to_sync.marketoid)
        self.assertIsNotNone(lead_to_sync.id)

        organization_to_sync = sync.pipedrive.Organization(self.pd, person_to_sync.org_id)
        found_company = sync.tasks.find_company_in_marketo(organization_to_sync)
        self.assertIsNotNone(found_company.id)  # Company exists
        found_company = sync.marketo.Company(self.mkto, organization_to_sync.marketoid)
        self.assertIsNotNone(found_company.id)  # Company has been found with marketo id

        rv = sync.tasks.create_or_update_lead_in_marketo(person_to_sync.id)

        # Test return data
        self.assertEquals(rv['status'], 'skipped')

    @mock.patch.object(sync.tasks, 'PIPELINE_FILTER_NAMES', ['Fake Pipeline', 'Foo'])
    def test_create_opportunity_and_role_in_marketo(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        deal_to_sync = sync.pipedrive.Deal(self.pd, 10)

        rv = sync.tasks.create_or_update_opportunity_in_marketo(deal_to_sync.id)

        # Test Deal sync

        # Opportunity has been created
        synced_opportunity = saved_instances['opportunity' + str(rv['opportunity']['id'])]
        self.assertIsNotNone(synced_opportunity.id)
        self.assertEquals(rv['opportunity']['status'], 'created')

        # Test values
        self.assertEquals(synced_opportunity.externalOpportunityId, sync.marketo.compute_external_id('deal', 10))
        self.assertEquals(synced_opportunity.name, 'Test Flask Deal')
        self.assertEquals(synced_opportunity.type, 'New Business')
        self.assertEquals(synced_opportunity.description, 'Dummy description 1')
        self.assertEquals(synced_opportunity.lastActivityDate, '2016-11-14')
        self.assertEquals(synced_opportunity.isClosed, False)
        self.assertEquals(synced_opportunity.isWon, False)
        self.assertEquals(synced_opportunity.amount, 10000)
        self.assertIsNone(synced_opportunity.closeDate)  # Not closed -> no close date
        self.assertEquals(synced_opportunity.stage, 'Sales Qualified Lead')
        self.assertIsNone(synced_opportunity.fiscalQuarter)  # Not closed -> no close date
        self.assertIsNone(synced_opportunity.fiscalYear)  # Not closed -> no close date

        # Role has been created
        synced_role = saved_instances['role' + str(rv['role']['id'])]
        self.assertIsNotNone(synced_role.id)

        # Test values
        self.assertEquals(synced_role.externalOpportunityId, sync.marketo.compute_external_id('deal', 10))
        self.assertEquals(synced_role.leadId, '20')
        self.assertEquals(synced_role.role, 'Default Role')

    @mock.patch.object(sync.tasks, 'PIPELINE_FILTER_NAMES', ['Fake Pipeline'])
    def test_update_opportunity_and_role_in_marketo(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        deal_to_sync = sync.pipedrive.Deal(self.pd, 20)

        rv = sync.tasks.create_or_update_opportunity_in_marketo(deal_to_sync.id)

        # Test Deal sync

        # Opportunity has been updated
        synced_opportunity = saved_instances['opportunity6a38a3bd-edce-4d86-bcc0-83f1feef8997']
        self.assertEquals(rv['opportunity']['status'], 'updated')
        self.assertEquals(rv['opportunity']['id'], synced_opportunity.id)

        # Test values
        self.assertEquals(synced_opportunity.name, 'Test Flask Linked Deal')
        self.assertEquals(synced_opportunity.type, 'Consulting')
        self.assertEquals(synced_opportunity.description, 'Dummy description 2')
        self.assertEquals(synced_opportunity.lastActivityDate, '2016-11-15')
        self.assertEquals(synced_opportunity.isClosed, True)
        self.assertEquals(synced_opportunity.isWon, False)
        self.assertEquals(synced_opportunity.amount, 20000)
        self.assertEquals(synced_opportunity.closeDate, '2016-11-16')
        self.assertEquals(synced_opportunity.stage, 'Sales Qualified Lead')
        self.assertEquals(synced_opportunity.fiscalQuarter, 4)
        self.assertEquals(synced_opportunity.fiscalYear, 2016)

    @mock.patch.object(sync.tasks, 'PIPELINE_FILTER_NAMES', ['Fake Pipeline'])
    def test_update_opportunity_and_role_in_marketo_no_change(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        deal_to_sync = sync.pipedrive.Deal(self.pd, 30)

        rv = sync.tasks.create_or_update_opportunity_in_marketo(deal_to_sync.id)

        # Test return data
        self.assertEquals(rv['opportunity']['status'], 'skipped')

    def test_update_company_in_marketo_find_by_name_no_change(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        organization_to_sync = sync.pipedrive.Organization(self.pd, 50)

        found_company = sync.tasks.find_company_in_marketo(organization_to_sync)
        self.assertIsNotNone(found_company.id)  # Company exists
        found_company = sync.marketo.Company(self.mkto, organization_to_sync.marketoid)
        self.assertIsNone(found_company.id)  # Company has not been found with marketo id
        found_company = sync.marketo.Company(self.mkto, sync.marketo.compute_external_id('organization', organization_to_sync.id),
                                        'externalCompanyId')
        self.assertIsNone(found_company.id)  # Company has not been found with external company id
        found_company = sync.marketo.Company(self.mkto, organization_to_sync.name, 'company')
        self.assertIsNotNone(found_company.id)  # Company has been found with name

        rv = sync.tasks.create_or_update_company_in_marketo(organization_to_sync.id)

        # Test return data
        self.assertEquals(rv['status'], 'skipped')

    def test_create_activity_in_pipedrive(self, mock_mkto_get_token, mock_put, mock_post, mock_get):
        lead_to_sync = sync.marketo.Lead(self.mkto, 20)

        rv = sync.tasks.create_activity_in_pipedrive(lead_to_sync.id)

        # Activity has been created
        synced_activity = saved_instances['activity' + str(rv['id'])]
        self.assertIsNotNone(synced_activity.id)
        self.assertEquals(rv['status'], 'created')

        # Test values
        self.assertEquals(synced_activity.user_id, 1628545)
        self.assertEquals(synced_activity.person_id, 20)
        self.assertEquals(synced_activity.type, 'call')
        self.assertEquals(synced_activity.subject, 'Follow up with Test Linked Flask Lead')
        self.assertEquals(synced_activity.note, 'Did something interesting on 12/19/2016')
        self.assertEquals(synced_activity.due_date, datetime.datetime.now().strftime('%Y-%m-%d'))

if __name__ == '__main__':
    unittest.main()
