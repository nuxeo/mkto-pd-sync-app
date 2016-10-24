from .context import marketo
from .context import secret

import logging
import unittest


class MarketoTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mkto = marketo.MarketoClient(secret.IDENTITY_ENDPOINT, secret.CLIENT_ID, secret.CLIENT_SECRET,
                                         secret.API_ENDPOINT)

    def test_load_lead(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.firstName, "Marco")
        self.assertEqual(lead.lastName, "Antonio")
        self.assertEqual(lead.email, "emeamarco@gmail.com")

    def test_load_lead_get_not_default_field(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.pipedriveId, 63080)

    def test_load_lead_get_undefined_field(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        with self.assertRaises(AttributeError):
            lead.fake_field

    def test_load_lead_undefined(self):
        lead = marketo.Lead(self.mkto, -1)
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)

    def test_load_lead_undefined_2(self):
        lead = marketo.Lead(self.mkto, "")
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)

    def test_load_lead_with_email(self):
        lead = marketo.Lead(self.mkto, "emeamarco@gmail.com", "email")
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.firstName, "Marco")
        self.assertEqual(lead.lastName, "Antonio")

    def test_empty_lead_get_field(self):
        lead = marketo.Lead(self.mkto)
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)
        self.assertIsNone(lead.firstName)

    def test_save_lead(self):
        lead = marketo.Lead(self.mkto)
        lead.firstName = "Test"
        lead.lastName = "Lead 2"
        lead.email = "lead@test2.com"
        self.assertIsNone(lead.id)
        lead.save()
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEquals(lead.firstName, "Test")
        self.assertEquals(lead.lastName, "Lead 2")
        self.assertEquals(lead.email, "lead@test2.com")
        # Delete created lead
        self.mkto.delete_resource("lead", lead.id)

    def test_update_lead(self):
        # Get lead first
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, "Marco")
        # Then update
        # NB: For the update to work, field should not block updates from WS API
        # Go to Admin -> Field Management -> search for the field
        # Field Actions ->  Block Field Updates -> disable Web service API
        lead.firstName = "Test 3"
        lead.save()
        # Reload lead before checking bc properties are not updated from result after saving
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertEquals(lead.firstName, "Test 3")
        # Reset updated value
        lead.firstName = "Marco"
        lead.save()

    def test_load_opportunity(self):
        opportunity = marketo.Opportunity(self.mkto, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertIsNotNone(opportunity)
        self.assertEqual(opportunity.id, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertEqual(opportunity.marketoGUID, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertEqual(opportunity.externalOpportunityId, "o1")
        self.assertEqual(opportunity.name, "Chairs")

    def test_load_opportunity_with_external_id(self):
        opportunity = marketo.Opportunity(self.mkto, "o1", "externalOpportunityId")
        self.assertIsNotNone(opportunity)
        self.assertEqual(opportunity.id, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertEqual(opportunity.marketoGUID, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertEqual(opportunity.externalOpportunityId, "o1")
        self.assertEqual(opportunity.name, "Chairs")

    def test_load_opportunity_undefined_with_external_id(self):
        opportunity = marketo.Opportunity(self.mkto, "o2", "externalOpportunityId")
        self.assertIsNotNone(opportunity)
        self.assertIsNone(opportunity.id)

    def test_load_role(self):
        role = marketo.Role(self.mkto, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertIsNotNone(role)
        self.assertEqual(role.id, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertEqual(role.marketoGUID, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertEqual(role.externalOpportunityId, "o1")
        self.assertEqual(role.leadId, 7591021)
        self.assertEqual(role.role, "Technical Buyer")

    def test_load_role_with_lead_id(self):
        role = marketo.Role(self.mkto, 7591021, "leadId")
        self.assertIsNotNone(role)
        self.assertEqual(role.id, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertEqual(role.marketoGUID, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertEqual(role.externalOpportunityId, "o1")
        self.assertEqual(role.leadId, 7591021)
        self.assertEqual(role.role, "Technical Buyer")

    def test_save_opportunity_and_role(self):
        opportunity = marketo.Opportunity(self.mkto)
        opportunity.externalOpportunityId = "testOpportunity1"
        opportunity.name = "Test opportunity 1"
        self.assertIsNone(opportunity.id)
        opportunity.save()
        self.assertIsNotNone(opportunity)
        self.assertIsNotNone(opportunity.id)
        self.assertEquals(opportunity.externalOpportunityId, "testOpportunity1")
        self.assertEquals(opportunity.name, "Test opportunity 1")

        role = marketo.Role(self.mkto)
        role.externalOpportunityId = "testOpportunity1"
        role.leadId = 7591021
        role.role = "Test role 1"
        self.assertIsNone(role.id)
        role.save()
        self.assertIsNotNone(role)
        self.assertIsNotNone(role.id)
        self.assertEquals(role.externalOpportunityId, "testOpportunity1")
        self.assertEquals(role.leadId, 7591021)
        self.assertEquals(role.role, "Test role 1")

        # Delete created opportunity and role
        self.mkto.delete_resource("opportunities/role", role.marketoGUID)
        self.mkto.delete_resource("opportunity", opportunity.marketoGUID)

    def test_update_opportunity(self):
        # Get opportunity first
        opportunity = marketo.Opportunity(self.mkto, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertIsNotNone(opportunity)
        self.assertIsNotNone(opportunity.id)
        self.assertEqual(opportunity.name, "Chairs")
        self.assertEqual(opportunity.externalOpportunityId, "o1")  # Check dedupeBy field
        # Then update
        opportunity.name = "Test opportunity 2"
        opportunity.save()
        # Reload opportunity before checking bc properties are not updated from result after saving
        opportunity = marketo.Opportunity(self.mkto, "6a38a3bd-edce-4d86-bcc0-83f1feef8997")
        self.assertEquals(opportunity.name, "Test opportunity 2")
        # Reset updated value
        opportunity.name = "Chairs"
        opportunity.save()

    def test_update_role(self):
        # Get role first
        role = marketo.Role(self.mkto, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertIsNotNone(role)
        self.assertIsNotNone(role.id)
        self.assertEquals(role.isPrimary, False)
        # Check dedupeBy fields
        self.assertEqual(role.externalOpportunityId, "o1")
        self.assertEqual(role.leadId, 7591021)
        self.assertEquals(role.role, "Technical Buyer")
        # Then update
        role.isPrimary = True
        role.save()
        # Reload role before checking bc properties are not updated from result after saving
        role = marketo.Role(self.mkto, "d8c8fec7-cd0a-4088-bba7-ee7d57e45b11")
        self.assertEquals(role.isPrimary, True)
        # Reset updated value
        role.isPrimary = False
        role.save()

    def test_load_company_with_external_id(self):
        company = marketo.Company(self.mkto, "c1", "externalCompanyId")
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        self.assertEqual(company.company, "Test company")

    def test_load_company_with_name(self):
        company = marketo.Company(self.mkto, "Test company", "company")
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        self.assertEqual(company.externalCompanyId, "c1")

    def test_save_company(self):
        company = marketo.Company(self.mkto)
        company.externalCompanyId = "testCompany1"
        company.company = "Test company 1"
        self.assertIsNone(company.id)
        company.save()
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        self.assertEqual(company.externalCompanyId, "testCompany1")
        self.assertEqual(company.company, "Test company 1")
        # Delete created company
        self.mkto.delete_resource("company", company.id)

    def test_update_company(self):
        # Get company first
        company = marketo.Company(self.mkto, "c1", "externalCompanyId")
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        # Then update
        company.company = "Test company 2"
        company.save()
        # Reload company before checking bc properties are not updated from result after saving
        company = marketo.Company(self.mkto, "c1", "externalCompanyId")
        self.assertEquals(company.company, "Test company 2")
        # Reset updated value
        company.company = "Test company"
        company.save()

    def test_save_lead_and_company(self):
        # Create company
        company = marketo.Company(self.mkto)
        company.externalCompanyId = "testCompany2"
        company.company = "Test company 2"
        company.save()
        self.assertIsNotNone(company)
        self.assertIsNotNone(company.id)
        # Create lead linked to created company
        lead = marketo.Lead(self.mkto)
        lead.firstName = "Test"
        lead.lastName = "Lead 4"
        lead.email = "lead@test4.com"
        lead.externalCompanyId = "testCompany2"
        lead.save()
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        # Delete created lead and company
        self.mkto.delete_resource("lead", lead.id)
        self.mkto.delete_resource("company", company.id)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("marketo").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(MarketoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
