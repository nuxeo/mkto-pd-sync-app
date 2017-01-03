# coding=UTF-8
import unittest

from .context import sync


class MarketoTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.mkto = sync.marketo.MarketoClient(sync.get_config('IDENTITY_ENDPOINT'), sync.get_config('CLIENT_ID'),
                                              sync.get_config('CLIENT_SECRET'), sync.get_config('API_ENDPOINT'))

    def test_load_lead(self):
        lead = sync.marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.firstName, 'Marco')
        self.assertEqual(lead.lastName, 'Antonio')
        self.assertEqual(lead.email, 'emeamarco@gmail.com')

    def test_load_lead_2(self):
        lead = sync.marketo.Lead(self.mkto, 7591021, 'id', False)
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertIsNone(lead.firstName)
        self.assertIsNone(lead.lastName)
        self.assertIsNone(lead.email)
        lead.load()
        self.assertEqual(lead.firstName, 'Marco')
        self.assertEqual(lead.lastName, 'Antonio')
        self.assertEqual(lead.email, 'emeamarco@gmail.com')

    def test_load_multiple_lead(self):
        leads = self.mkto.get_entities('lead', [7591021, 8271235, -1, ''], 'id')
        self.assertEqual(len(leads), 2)
        self.assertIsNotNone(leads[0])
        self.assertIsNotNone(leads[0].id)
        self.assertEqual(leads[0].firstName, 'Marco')
        self.assertEqual(leads[0].lastName, 'Antonio')
        self.assertEqual(leads[0].email, 'emeamarco@gmail.com')
        self.assertIsNotNone(leads[1])
        self.assertIsNotNone(leads[1].id)
        self.assertEqual(leads[1].firstName, 'Helene')
        self.assertEqual(leads[1].lastName, 'Jonin')
        self.assertEqual(leads[1].email, 'hjonin@nuxeo.com')

    def test_load_lead_get_not_default_field(self):
        lead = sync.marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.pipedriveId, 63080)

    def test_load_lead_get_undefined_field(self):
        lead = sync.marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        with self.assertRaises(AttributeError):
            lead.fake_field

    def test_load_lead_undefined(self):
        lead = sync.marketo.Lead(self.mkto, -1)
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)

    def test_load_lead_undefined_2(self):
        lead = sync.marketo.Lead(self.mkto, '')
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)

    def test_load_lead_with_email(self):
        lead = sync.marketo.Lead(self.mkto, 'emeamarco@gmail.com', 'email')
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.firstName, 'Marco')
        self.assertEqual(lead.lastName, 'Antonio')

    def test_empty_lead_get_field(self):
        lead = sync.marketo.Lead(self.mkto)
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)
        self.assertIsNone(lead.firstName)

    def test_empty_lead_load(self):
        lead = sync.marketo.Lead(self.mkto)
        lead.load()

    def test_save_lead(self):
        lead = sync.marketo.Lead(self.mkto)
        lead.firstName = 'Test'
        lead.lastName = 'L€ad 2'  # Try non ASCII character
        lead.email = 'lead@test2.com'
        #  Test some fields
        lead.website = 'test-company-website.com'
        lead.country = 'France'
        self.assertIsNone(lead.id)
        lead.save()
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        # Reload lead before checking bc properties are not updated from result after saving
        lead.load()
        self.assertEquals(lead.firstName, 'Test')
        self.assertEquals(lead.lastName, u'L€ad 2')  # JSON strings are unicode
        self.assertEquals(lead.email, 'lead@test2.com')
        self.assertEquals(lead.website, 'test-company-website.com')
        self.assertEquals(lead.country, 'France')
        # Delete created lead
        lead.delete()

    def test_save_multiple_lead(self):
        leads = []
        lead = sync.marketo.Lead(self.mkto)
        lead.firstName = 'Test'
        lead.lastName = 'Lead 3'
        lead.email = 'lead@test3.com'
        leads.append(lead)
        lead = sync.marketo.Lead(self.mkto)
        lead.firstName = 'Test'
        lead.lastName = 'Lead 4'
        lead.email = 'lead@test4.com'
        leads.append(lead)
        saved_leads = self.mkto.put_entities('lead', leads)
        self.assertEqual(len(saved_leads), 2)
        self.assertIsNotNone(saved_leads[0])
        self.assertIsNotNone(saved_leads[0].id)
        # Reload lead before checking bc properties are not updated from result after saving
        saved_leads[0].load()
        self.assertEquals(saved_leads[0].firstName, 'Test')
        self.assertEquals(saved_leads[0].lastName, 'Lead 3')
        self.assertEquals(saved_leads[0].email, 'lead@test3.com')
        self.assertIsNotNone(saved_leads[1])
        self.assertIsNotNone(saved_leads[1].id)
        # Reload lead before checking bc properties are not updated from result after saving
        saved_leads[1].load()
        self.assertEquals(saved_leads[1].firstName, 'Test')
        self.assertEquals(saved_leads[1].lastName, 'Lead 4')
        self.assertEquals(saved_leads[1].email, 'lead@test4.com')
        # Delete created leads
        saved_leads[0].delete()
        saved_leads[1].delete()

    def test_update_lead(self):
        # Get lead first
        lead = sync.marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, 'Marco')
        # Then update
        # NB: For the update to work, field should not block updates from WS API
        # Go to Admin -> Field Management -> search for the field
        # Field Actions ->  Block Field Updates -> disable Web service API
        lead.firstName = 'Test 3'
        lead.save()
        # Reload lead before checking bc properties are not updated from result after saving
        lead.load()
        self.assertEquals(lead.firstName, 'Test 3')
        # Reset updated value
        lead.firstName = 'Marco'
        lead.save()

    def test_update_multiple_lead(self):
        leads = []
        # Get lead first
        lead = sync.marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, 'Marco')
        # Then update
        lead.firstName = 'Test 4'
        leads.append(lead)
        # Get lead first
        lead = sync.marketo.Lead(self.mkto, 8271235)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, 'Helene')
        # Then update
        lead.firstName = 'Test 5'
        leads.append(lead)
        saved_leads = self.mkto.put_entities('lead', leads)
        self.assertEqual(len(saved_leads), 2)
        # Reload lead before checking bc properties are not updated from result after saving
        saved_leads[0].load()
        self.assertEquals(saved_leads[0].firstName, 'Test 4')
        saved_leads[1].load()
        self.assertEquals(saved_leads[1].firstName, 'Test 5')
        # Reset updated value
        saved_leads[0].firstName = 'Marco'
        saved_leads[0].save()
        saved_leads[1].firstName = 'Helene'
        saved_leads[1].save()

    def test_load_opportunity(self):
        opportunity = sync.marketo.Opportunity(self.mkto, '6a38a3bd-edce-4d86-bcc0-83f1feef8997')
        self.assertIsNotNone(opportunity)
        self.assertEqual(opportunity.id, '6a38a3bd-edce-4d86-bcc0-83f1feef8997')
        self.assertEqual(opportunity.marketoGUID, '6a38a3bd-edce-4d86-bcc0-83f1feef8997')
        self.assertEqual(opportunity.externalOpportunityId, 'o1')
        self.assertEqual(opportunity.name, 'Chairs')

    def test_load_opportunity_with_external_id(self):
        opportunity = sync.marketo.Opportunity(self.mkto, 'o1', 'externalOpportunityId')
        self.assertIsNotNone(opportunity)
        self.assertEqual(opportunity.id, '6a38a3bd-edce-4d86-bcc0-83f1feef8997')
        self.assertEqual(opportunity.marketoGUID, '6a38a3bd-edce-4d86-bcc0-83f1feef8997')
        self.assertEqual(opportunity.externalOpportunityId, 'o1')
        self.assertEqual(opportunity.name, 'Chairs')

    def test_load_opportunity_undefined_with_external_id(self):
        opportunity = sync.marketo.Opportunity(self.mkto, 'o2', 'externalOpportunityId')
        self.assertIsNotNone(opportunity)
        self.assertIsNone(opportunity.id)

    def test_load_role(self):
        role = sync.marketo.Role(self.mkto, 'd8c8fec7-cd0a-4088-bba7-ee7d57e45b11')
        self.assertIsNotNone(role)
        self.assertEqual(role.id, 'd8c8fec7-cd0a-4088-bba7-ee7d57e45b11')
        self.assertEqual(role.marketoGUID, 'd8c8fec7-cd0a-4088-bba7-ee7d57e45b11')
        self.assertEqual(role.externalOpportunityId, 'o1')
        self.assertEqual(role.leadId, 7591021)
        self.assertEqual(role.role, 'Technical Buyer')

    def test_load_role_with_lead_id(self):
        role = sync.marketo.Role(self.mkto, 7591021, 'leadId')
        self.assertIsNotNone(role)
        self.assertEqual(role.id, 'd8c8fec7-cd0a-4088-bba7-ee7d57e45b11')
        self.assertEqual(role.marketoGUID, 'd8c8fec7-cd0a-4088-bba7-ee7d57e45b11')
        self.assertEqual(role.externalOpportunityId, 'o1')
        self.assertEqual(role.leadId, 7591021)
        self.assertEqual(role.role, 'Technical Buyer')

    def test_save_opportunity_and_role(self):
        opportunity = sync.marketo.Opportunity(self.mkto)
        opportunity.externalOpportunityId = 'testOpportunity1'
        opportunity.name = 'Test opportunity 1'
        #  Test some fields
        opportunity.lastActivityDate = '2016-11-16'
        self.assertIsNone(opportunity.id)
        opportunity.save()
        self.assertIsNotNone(opportunity)
        self.assertIsNotNone(opportunity.id)
        # Reload opportunity before checking bc properties are not updated from result after saving
        opportunity.load()
        self.assertEquals(opportunity.externalOpportunityId, 'testOpportunity1')
        self.assertEquals(opportunity.name, 'Test opportunity 1')
        self.assertEquals(opportunity.lastActivityDate, '2016-11-16')

        role = sync.marketo.Role(self.mkto)
        role.externalOpportunityId = 'testOpportunity1'
        role.leadId = 7591021
        role.role = 'Test role 1'
        self.assertIsNone(role.id)
        role.save()
        self.assertIsNotNone(role)
        self.assertIsNotNone(role.id)
        # Reload role before checking bc properties are not updated from result after saving
        role.load()
        self.assertEquals(role.externalOpportunityId, 'testOpportunity1')
        self.assertEquals(role.leadId, 7591021)
        self.assertEquals(role.role, 'Test role 1')

        # Delete created opportunity and role
        role.delete()
        opportunity.delete()

    def test_update_opportunity(self):
        # Get opportunity first
        opportunity = sync.marketo.Opportunity(self.mkto, '6a38a3bd-edce-4d86-bcc0-83f1feef8997')
        self.assertIsNotNone(opportunity)
        self.assertIsNotNone(opportunity.id)
        self.assertEqual(opportunity.name, 'Chairs')
        self.assertEqual(opportunity.externalOpportunityId, 'o1')  # Check dedupeBy field
        # Then update
        opportunity.name = 'Test opportunity 2'
        opportunity.save()
        # Reload opportunity before checking bc properties are not updated from result after saving
        opportunity.load()
        self.assertEquals(opportunity.name, 'Test opportunity 2')
        # Reset updated value
        opportunity.name = 'Chairs'
        opportunity.save()

    def test_update_role(self):
        # Get role first
        role = sync.marketo.Role(self.mkto, 'd8c8fec7-cd0a-4088-bba7-ee7d57e45b11')
        self.assertIsNotNone(role)
        self.assertIsNotNone(role.id)
        self.assertEquals(role.isPrimary, False)
        # Check dedupeBy fields
        self.assertEqual(role.externalOpportunityId, 'o1')
        self.assertEqual(role.leadId, 7591021)
        self.assertEquals(role.role, 'Technical Buyer')
        # Then update
        role.isPrimary = True
        role.save()
        # Reload role before checking bc properties are not updated from result after saving
        role.load()
        self.assertEquals(role.isPrimary, True)
        # Reset updated value
        role.isPrimary = False
        role.save()

    def test_load_company_with_external_id(self):
        company = sync.marketo.Company(self.mkto, 'c1', 'externalCompanyId')
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        self.assertEqual(company.company, 'Test company')

    def test_load_company_with_name(self):
        company = sync.marketo.Company(self.mkto, 'Test company', 'company')
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        self.assertEqual(company.externalCompanyId, 'c1')

    def test_load_company_with_name_unicode(self):
        company = sync.marketo.Company(self.mkto, u'Tést company', 'company')
        self.assertIsNotNone(company)

    def test_save_company(self):
        company = sync.marketo.Company(self.mkto)
        company.externalCompanyId = 'testCompany1'
        company.company = 'Test company 1'
        self.assertIsNone(company.id)
        company.save()
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        # Reload company before checking bc properties are not updated from result after saving
        company.load()
        self.assertEqual(company.externalCompanyId, 'testCompany1')
        self.assertEqual(company.company, 'Test company 1')
        # Delete created company
        company.delete('externalCompanyId')

    def test_update_company(self):
        # Get company first
        company = sync.marketo.Company(self.mkto, 'c1', 'externalCompanyId')
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        # Then update
        company.company = 'Test company 2'
        company.save()
        # Reload company before checking bc properties are not updated from result after saving
        company.load()
        self.assertEquals(company.company, 'Test company 2')
        # Reset updated value
        company.company = 'Test company'
        company.save()

    def test_save_lead_and_company(self):
        # Create company
        company = sync.marketo.Company(self.mkto)
        company.externalCompanyId = 'testCompany2'
        company.company = 'Test company 2'
        company.save()
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        # Create lead linked to created company
        lead = sync.marketo.Lead(self.mkto)
        lead.firstName = 'Test'
        lead.lastName = 'Lead 4'
        lead.email = 'lead@test4.com'
        lead.externalCompanyId = 'testCompany2'
        lead.save()
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        # Delete created lead and company
        lead.delete()
        company.delete('externalCompanyId')
