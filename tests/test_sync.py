from .context import sync, tasks

import datetime
import json
import mock
import os
import requests
import unittest

from google.appengine.ext import ndb, testbed

vals = {
    (sync.get_config('API_ENDPOINT') + '/v1/leads/describe.json',):               {'{}': 'resources/leadFields.json'},
    (sync.get_config('API_ENDPOINT') + '/v1/leads.json',):                        {
        "{'filterType': 'id', 'filterValues': '10'}": 'resources/lead10.json',
        "{'filterType': 'id', 'filterValues': '20'}": 'resources/lead20.json',
        "{'filterType': 'id', 'filterValues': '30'}": 'resources/lead30.json',
        "{'filterType': 'id', 'filterValues': '40'}": 'resources/lead40.json'
        },
    ('https://api.pipedrive.com/v1/personFields',):                               {'{}': 'resources/personFields.json'},
    ('https://api.pipedrive.com/v1/persons/10',):                                 {'{}': 'resources/person10.json'},
    ('https://api.pipedrive.com/v1/persons/20',):                                 {'{}': 'resources/person20.json'},
    ('https://api.pipedrive.com/v1/persons/30',):                                 {'{}': 'resources/person30.json'},
    ('https://api.pipedrive.com/v1/userFields',):                                 {'{}': 'resources/userFields.json'},
    ('https://api.pipedrive.com/v1/users/find',):                                 {"{'term': u'Helene Jonin'}": 'resources/userHeleneJonin.json'},
    ('https://api.pipedrive.com/v1/users/1628545',):                              {'{}': 'resources/user1628545.json'},
    (sync.get_config('API_ENDPOINT') + '/v1/companies/describe.json',):           {'{}': 'resources/companyFields.json'},
    (sync.get_config('API_ENDPOINT') + '/v1/companies.json',):                    {
        "{'filterType': 'externalCompanyId', 'filterValues': 'testFlaskCompany'}"      : 'resources/company10.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-10'}"    : 'resources/empty.json',
        "{'filterType': 'company', 'filterValues': 'Test Flask Organization'}"         : 'resources/empty.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-20'}"    : 'resources/company20.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-30'}"    : 'resources/company30.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'mkto-lead-company-40'}"  : 'resources/empty.json',
        "{'filterType': 'externalCompanyId', 'filterValues': 'pd-organization-50'}"    : 'resources/empty.json',
        "{'filterType': 'company', 'filterValues': 'Test Flask Unlinked Organization'}": 'resources/company50.json'
        },
    ('https://api.pipedrive.com/v1/organizationFields',):                         {'{}': 'resources/organizationFields.json'},
    ('https://api.pipedrive.com/v1/organizations/find',):                         {"{'term': u'Test Flask Company'}": 'resources/emptyPdFind.json'},
    ('https://api.pipedrive.com/v1/organizations/10',):                           {'{}': 'resources/organization10.json'},
    ('https://api.pipedrive.com/v1/organizations/20',):                           {'{}': 'resources/organization20.json'},
    ('https://api.pipedrive.com/v1/organizations/30',):                           {'{}': 'resources/organization30.json'},
    ('https://api.pipedrive.com/v1/organizations/50',):                           {'{}': 'resources/organization50.json'},
    ('https://api.pipedrive.com/v1/dealFields',):                                 {'{}': 'resources/dealFields.json'},
    ('https://api.pipedrive.com/v1/deals/10',):                                   {'{}': 'resources/deal10.json'},
    ('https://api.pipedrive.com/v1/deals/20',):                                   {'{}': 'resources/deal20.json'},
    ('https://api.pipedrive.com/v1/deals/30',):                                   {'{}': 'resources/deal30.json'},
    ('https://api.pipedrive.com/v1/pipelines/12',):                               {'{}': 'resources/pipeline12.json'},
    (sync.get_config('API_ENDPOINT') + '/v1/opportunities/describe.json',):       {'{}': 'resources/opportunityFields.json'},
    (sync.get_config('API_ENDPOINT') + '/v1/opportunities/roles/describe.json',): {'{}': 'resources/opportunityRoleFields.json'},
    (sync.get_config('API_ENDPOINT') + '/v1/opportunities.json',):                {
        "{'filterType': 'externalOpportunityId', 'filterValues': 'pd-deal-10'}": 'resources/empty.json',
        "{'filterType': 'externalOpportunityId', 'filterValues': 'pd-deal-20'}": 'resources/opportunity20.json',
        "{'filterType': 'externalOpportunityId', 'filterValues': 'pd-deal-30'}": 'resources/opportunity30.json'
        },
    ('https://api.pipedrive.com/v1/stages/34',):                                  {'{}': 'resources/stage34.json'},
    ('https://api.pipedrive.com/v1/activityFields',):                             {'{}': 'resources/activityFields.json'}
}


def side_effect_get(*args, **kwargs):
    rv = mock.MagicMock(spec=requests.Response)
    params = kwargs['params']
    if 'filterType' in params and 'filterValues' in params:
        value = "{'filterType': '%s', 'filterValues': '%s'}" % (params['filterType'], params['filterValues'])
    else:
        value = str(params)
    rv.url = '%s -> %s' % (args[0], vals[args][value])
    with open(os.path.join(os.path.dirname(__file__), vals[args][value])) as f:
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


@mock.patch.object(requests.Session, 'get', side_effect=side_effect_get)
@mock.patch.object(sync.marketo.Lead, 'save', mock_save_lead)
@mock.patch.object(sync.marketo.Company, 'save', mock_save_company)
@mock.patch.object(sync.marketo.Opportunity, 'save', mock_save_opportunity)
@mock.patch.object(sync.marketo.Role, 'save', mock_save_role)
@mock.patch.object(sync.pipedrive.Person, 'save', mock_save_person)
@mock.patch.object(sync.pipedrive.Organization, 'save', mock_save_organization)
@mock.patch.object(sync.pipedrive.Activity, 'save', mock_save_activity)
@mock.patch('sync.marketo.MarketoClient._get_auth_token')
class SyncTestCase(unittest.TestCase):
    AUTHENTICATION_PARAM = '?api_key=' + sync.get_config('FLASK_AUTHORIZED_KEYS')['test']

    @classmethod
    def setUpClass(cls):
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

    @classmethod
    def tearDownClass(cls):
        cls.context.pop()

        cls.testbed.deactivate()

    def test_authentication_error(self, mock_mkto_get_token, mock_get):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/1')
            self.assertEqual(rv.status_code, 401)
            data = json.loads(rv.data)
            self.assertEqual(data['message'], 'Authentication required')

    @mock.patch('sync.views.enqueue_task')
    def test_internal_server_error(self, mock_sync_lead, mock_mkto_get_token, mock_get):
        mock_sync_lead.side_effect = Exception('Boom!')
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/1' + self.AUTHENTICATION_PARAM)
            self.assertEqual(rv.status_code, 500)
            data = json.loads(rv.data)
            self.assertEqual(data['message'], 'Boom!')

    def test_flow(self, mock_mkto_get_token, mock_get):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/1' + self.AUTHENTICATION_PARAM)
            data = json.loads(rv.data)
            self.assertTrue(data['message'])

            tasks = self.taskqueue_stub.get_filtered_tasks()
            self.assertEqual(len(tasks), 1)
            self.assertEqual(tasks[0].name, 'task1')

    # Test tasks

    def test_create_person_in_pipedrive(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_person_in_pipedrive(10)

        person_id = saved_instances['lead10'].pipedriveId
        self.assertIsNotNone(person_id)  # Pipedrive id has been updated

        person = saved_instances['person' + str(ret['id'])]
        self.assertIsNotNone(person)  # Person has been created
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, 'Test Flask Lead')
        self.assertEquals(person.email, 'lead@testflask.com')
        self.assertIsNotNone(person.org_id)
        self.assertEquals(person.title, 'Manager')
        self.assertEquals(person.phone, '9876543210')
        self.assertEquals(person.inferred_country, 'Italy')
        self.assertEquals(person.lead_source, 'Organic Search')
        self.assertEquals(person.owner_id, 1628545)
        self.assertEquals(person.created_date, '2016-01-01')
        self.assertEquals(person.state, 'Italy')
        self.assertEquals(person.city, 'Milano')
        self.assertEquals(person.lead_score, 10)
        self.assertEquals(person.date_sql, '2016-11-16')
        self.assertEquals(person.lead_status, 'Recycled')

        # Test Organization sync
        organization = saved_instances['organization' + str(person.org_id)]  # Organization has been created
        self.assertEquals(organization.name, 'Test Flask Company')
        self.assertEquals(organization.address, '11th St')
        self.assertEquals(organization.city, 'New York')
        self.assertEquals(organization.state, 'NY')
        self.assertEquals(organization.country, 'United States')
        self.assertEquals(organization.company_phone, '0123456789')
        self.assertEquals(organization.industry, 'Finance')
        self.assertEquals(organization.annual_revenue, 1000000)
        self.assertEquals(organization.number_of_employees, 10)

        # Test return data
        self.assertEquals(ret['status'], 'created')

    def test_update_person_in_pipedrive(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_person_in_pipedrive(20)

        person = saved_instances['person20']
        self.assertEquals(person.name, 'Test Linked Flask Lead')  # Person has been updated
        self.assertEquals(person.email, 'lead@testlinkedflask.com')
        self.assertIsNotNone(person.org_id)
        self.assertEquals(person.title, 'Accountant')
        self.assertEquals(person.phone, '1357924680')
        self.assertEquals(person.inferred_country, 'Spain')
        self.assertEquals(person.lead_source, 'Product')
        self.assertEquals(person.owner_id, 1628545)
        self.assertEquals(person.created_date, '2016-01-02')
        self.assertEquals(person.state, 'Spain')
        self.assertEquals(person.city, 'Barcelona')
        self.assertEquals(person.lead_score, 13)
        self.assertEquals(person.date_sql, '2016-11-16')
        self.assertEquals(person.lead_status, 'Prospect')

        # Test Organization sync
        organization = saved_instances['organization20']  # Organization has been created
        self.assertEquals(organization.name, 'Test Flask Linked Company')  # Organization has been updated

        # Test return data
        self.assertEquals(ret['status'], 'updated')
        self.assertEquals(ret['id'], person.id)

    def test_update_person_in_pipedrive_no_change(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_person_in_pipedrive(30)

        # Test return data
        self.assertEquals(ret['status'], 'skipped')

    def test_create_person_in_pipedrive_company_form_fields(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_person_in_pipedrive(40)

        person_id = saved_instances['lead40'].pipedriveId
        self.assertIsNotNone(person_id)  # Pipedrive id has been updated

        person = saved_instances['person' + str(ret['id'])]
        self.assertIsNotNone(person)  # Person has been created
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, 'Test Other Flask Lead')
        self.assertEquals(person.email, 'lead2@testflask.com')
#         self.assertIsNotNone(person.org_id)  # Company not truly saved => no possible to be found

        # Test Organization sync
#         self.assertEquals(person.organization.name, 'another-flask-company.com')
#         self.assertEquals(person.organization.country, 'Canada')

        # Test return data
        self.assertEquals(ret['status'], 'created')

    def test_create_lead_in_marketo(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_lead_in_marketo(10)

        lead_id = saved_instances['person10'].marketoid
        self.assertIsNotNone(lead_id)  # Marketo id has been updated

        lead = saved_instances['lead' + str(ret['id'])]
        self.assertIsNotNone(lead)  # Lead has been created
        self.assertIsNotNone(lead.id)
        self.assertEquals(lead.firstName, 'Test Flask')
        self.assertEquals(lead.lastName, 'Person')
        self.assertEquals(lead.email, 'person@testflask.com')
        self.assertIsNotNone(lead.externalCompanyId)
        self.assertEquals(lead.title, 'Dev')
        self.assertEquals(lead.phone, '5647382910')
        self.assertEquals(lead.leadSource, 'Direct Traffic')
        self.assertEquals(lead.conversicaLeadOwnerEmail, 'hjonin@nuxeo.com')
        self.assertEquals(lead.conversicaLeadOwnerFirstName, 'Helene')
        self.assertEquals(lead.conversicaLeadOwnerLastName, 'Jonin')
        self.assertEquals(lead.leadStatus, 'Disqualified')

        # Test Company sync
        company = saved_instances['company' + str(15)]
        self.assertIsNotNone(company)  # Company has been created
        self.assertEquals(company.company, 'Test Flask Organization')
        self.assertEquals(company.billingStreet, 'Rue Mouffetard')
        self.assertEquals(company.billingCity, u'Paris')
        self.assertEquals(company.billingState, 'France')
        self.assertEquals(company.billingCountry, 'France')
        self.assertEquals(company.mainPhone, '0192837465')
        self.assertEquals(company.industry, 'Consulting')
        self.assertEquals(company.annualRevenue, 2000000)
        self.assertEquals(company.numberOfEmployees, 20)

        # Test return data
        self.assertEquals(ret['status'], 'created')

    def test_update_lead_in_marketo(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_lead_in_marketo(20)

        lead = saved_instances['lead20']
        self.assertEquals(lead.firstName, 'Test Linked Flask')  # Lead has been updated
        self.assertEquals(lead.lastName, 'Person')
        self.assertEquals(lead.email, 'person@testlinkedflask.com')
        self.assertEquals(lead.externalCompanyId, 'pd-organization-20')
        self.assertEquals(lead.title, 'Consultant')
        self.assertEquals(lead.phone, '2468013579')
        self.assertEquals(lead.leadSource, 'Web Referral')
        self.assertEquals(lead.conversicaLeadOwnerEmail, 'hjonin@nuxeo.com')
        self.assertEquals(lead.conversicaLeadOwnerFirstName, 'Helene')
        self.assertEquals(lead.conversicaLeadOwnerLastName, 'Jonin')
        self.assertEquals(lead.leadStatus, 'MQL')

        # Test Company sync
        company = saved_instances['company20']
        self.assertEquals(company.company, 'Test Flask Linked Organization')  # Company has been updated

        # Test return data
        self.assertEquals(ret['status'], 'updated')

    def test_update_lead_in_marketo_no_change(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_lead_in_marketo(30)
        # Test return data
        self.assertEquals(ret['status'], 'skipped')

    @mock.patch.object(sync.tasks, 'PIPELINE_FILTER_NAME', 'Fake Pipeline')
    def test_create_opportunity_and_role_in_marketo(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_opportunity_in_marketo(10)

        opportunity = saved_instances['opportunity' + str(ret['opportunity']['id'])]
        self.assertIsNotNone(opportunity)  # Opportunity has been created
        self.assertIsNotNone(opportunity.id)
        self.assertEquals(opportunity.externalOpportunityId, sync.marketo.compute_external_id('deal', 10))
        self.assertEquals(opportunity.name, 'Test Flask Deal')
        self.assertEquals(opportunity.type, 'New Business')
        self.assertEquals(opportunity.description, 'Dummy description 1')
        self.assertEquals(opportunity.lastActivityDate, '2016-11-14')
        self.assertEquals(opportunity.isClosed, False)
        self.assertEquals(opportunity.isWon, False)
        self.assertEquals(opportunity.amount, 10000)
        self.assertIsNone(opportunity.closeDate)  # Not closed -> no close date
        self.assertEquals(opportunity.stage, 'Sales Qualified Lead')
        self.assertIsNone(opportunity.fiscalQuarter)  # Not closed -> no close date
        self.assertIsNone(opportunity.fiscalYear)  # Not closed -> no close date

        role = saved_instances['role' + str(ret['role']['id'])]
        self.assertIsNotNone(role)  # Role has been created
        self.assertIsNotNone(role.id)
        self.assertEquals(role.externalOpportunityId, sync.marketo.compute_external_id('deal', 10))
        self.assertEquals(role.leadId, '20')
        self.assertEquals(role.role, 'Default Role')

        # Test return data
        self.assertEquals(ret['opportunity']['status'], 'created')

    @mock.patch.object(sync.tasks, 'PIPELINE_FILTER_NAME', 'Fake Pipeline')
    def test_update_opportunity_and_role_in_marketo(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_opportunity_in_marketo(20)

        opportunity = saved_instances['opportunity6a38a3bd-edce-4d86-bcc0-83f1feef8997']
        self.assertEquals(opportunity.name, 'Test Flask Linked Deal')  # Opportunity has been updated
        self.assertEquals(opportunity.type, 'Consulting')
        self.assertEquals(opportunity.description, 'Dummy description 2')
        self.assertEquals(opportunity.lastActivityDate, '2016-11-15')
        self.assertEquals(opportunity.isClosed, True)
        self.assertEquals(opportunity.isWon, False)
        self.assertEquals(opportunity.amount, 20000)
        self.assertEquals(opportunity.closeDate, '2016-11-16')
        self.assertEquals(opportunity.stage, 'Sales Qualified Lead')
        self.assertEquals(opportunity.fiscalQuarter, 4)
        self.assertEquals(opportunity.fiscalYear, 2016)

        # Test return data
        self.assertEquals(ret['opportunity']['status'], 'updated')

    @mock.patch.object(sync.tasks, 'PIPELINE_FILTER_NAME', 'Fake Pipeline')
    def test_update_opportunity_and_role_in_marketo_no_change(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_opportunity_in_marketo(30)

        # Test return data
        self.assertEquals(ret['opportunity']['status'], 'skipped')

    def test_update_company_in_marketo_find_by_name_no_change(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_or_update_company_in_marketo(50)

#         updated_company = saved_instances['company50']  # Not saved

        # Test return data
        self.assertEquals(ret['status'], 'skipped')

    def test_create_activity_in_pipedrive(self, mock_mkto_get_token, mock_get):
        ret = tasks.create_activity_in_pipedrive(20)

        activity = saved_instances['activity' + str(ret['id'])]
        self.assertIsNotNone(activity)  # Person has been created
        self.assertIsNotNone(activity.id)
        self.assertEquals(activity.user_id, 1628545)
        self.assertEquals(activity.person_id, 20)
        self.assertEquals(activity.type, 'call')
        self.assertEquals(activity.subject, 'Follow up with Test Linked Flask Lead')
        self.assertEquals(activity.note, 'Did something interesting on 12/19/2016')
        self.assertEquals(activity.due_date, datetime.datetime.now().strftime('%Y-%m-%d'))

        # Test return data
        self.assertEquals(ret['status'], 'created')
