import unittest
from .context import marketo_pipedrive_sync
from .context import marketo
from .context import pipedrive
from .context import secret
import logging
from flask import g
import json


class SyncTestCase(unittest.TestCase):
    AUTHENTICATION_PARAM = "?api_key=" + secret.FLASK_AUTHORIZED_KEYS[0]

    @classmethod
    def setUpClass(cls):
        with marketo_pipedrive_sync.app.app_context():
            # Create company to be linked with a Marketo lead
            company = marketo.Company(marketo_pipedrive_sync.get_marketo_client())
            company.externalCompanyId = "testFlaskCompany"
            company.company = "Test Flask Company"
            company.save()
            cls.company = company

            # Create lead in Marketo not linked with any person in Pipedrive
            lead = marketo.Lead(marketo_pipedrive_sync.get_marketo_client())
            lead.firstName = "Test Flask"
            lead.lastName = "Lead"
            lead.email = "lead@testflask.com"
            lead.externalCompanyId = cls.company.externalCompanyId
            lead.save()
            cls.lead = lead

            # Create organization to be linked with a Pipedrive person
            organization = pipedrive.Organization(marketo_pipedrive_sync.get_pipedrive_client())
            organization.name = "Test Flask Organization"
            organization.save()
            cls.organization = organization

            # Create person in Pipedrive not linked with any lead in Marketo
            person = pipedrive.Person(marketo_pipedrive_sync.get_pipedrive_client())
            person.name = "Test Flask Person"
            person.email = "person@testflask.com"
            person.org_id = cls.organization.id
            person.owner_id = 1628545  # my (Helene Jonin) owner id
            person.save()
            cls.person = person

            # Create lead in Marketo linked with a person in Pipedrive
            linked_lead = marketo.Lead(marketo_pipedrive_sync.get_marketo_client())
            linked_lead.firstName = "Test Linked Flask"
            linked_lead.lastName = "Lead"
            linked_lead.email = "lead@testlinkedflask.com"
            linked_lead.save()
            cls.linked_lead = linked_lead

            # Create person in Pipedrive linked with a lead in Marketo
            linked_person = pipedrive.Person(marketo_pipedrive_sync.get_pipedrive_client())
            linked_person.name = "Test Linked Flask Lead"
            linked_person.email = "lead@testlinkedflask.com"
            linked_person.owner_id = 1628545  # my (Helene Jonin) owner id
            linked_person.save()
            cls.linked_person = linked_person

            # Set the links
            cls.linked_lead.pipedriveId = cls.linked_person.id
            cls.linked_person.marketoid = cls.linked_lead.id
            cls.linked_lead.save()
            cls.linked_person.save()

            # Create deal in Pipedrive
            deal = pipedrive.Deal(marketo_pipedrive_sync.get_pipedrive_client())
            deal.title = "Test Flask Deal"
            deal.person_id = cls.linked_person.id
            deal.user_id = 1628545  # my (Helene Jonin) owner id
            deal.save()
            cls.deal = deal

            # Create deal in Pipedrive linked with an opportunity in Marketo
            linked_deal = pipedrive.Deal(marketo_pipedrive_sync.get_pipedrive_client())
            linked_deal.title = "Test Flask Linked Deal"
            linked_deal.person_id = cls.linked_person.id
            linked_deal.user_id = 1628545  # my (Helene Jonin) owner id
            linked_deal.save()
            cls.linked_deal = linked_deal

            # Create opportunity and role in Marketo linked with a deal in Pipedrive
            linked_opportunity = marketo.Opportunity(marketo_pipedrive_sync.get_marketo_client())
            linked_opportunity.externalOpportunityId = marketo.compute_external_id("deal", linked_deal.id)
            linked_opportunity.name = "Test Flask Linked Deal"
            linked_opportunity.save()
            cls.linked_opportunity = linked_opportunity
            linked_role = marketo.Role(marketo_pipedrive_sync.get_marketo_client())
            linked_role.externalOpportunityId = linked_opportunity.externalOpportunityId
            linked_role.leadId = cls.linked_lead.id
            linked_role.role = "Fake Role"
            linked_role.save()
            cls.linked_role = linked_role

            # Initialize class variables
            cls.new_lead = None
            cls.new_person = None
            cls.new_opportunity = None
            cls.new_role = None
            cls.new_organization = None
            cls.new_company = None

    @classmethod
    def tearDownClass(cls):
        with marketo_pipedrive_sync.app.app_context():
            # Delete created resources
            marketo_pipedrive_sync.get_marketo_client().delete_resource("lead", cls.lead.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("person", cls.person.id)
            marketo_pipedrive_sync.get_marketo_client().delete_resource("lead", cls.linked_lead.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("person", cls.linked_person.id)
            if cls.new_lead is not None:
                marketo_pipedrive_sync.get_marketo_client().delete_resource("lead", cls.new_lead.id)
            if cls.new_person is not None:
                marketo_pipedrive_sync.get_pipedrive_client().delete_resource("person", cls.new_person.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("deal", cls.deal.id)
            marketo_pipedrive_sync.get_marketo_client().delete_resource("opportunity", cls.linked_opportunity.id)
            marketo_pipedrive_sync.get_marketo_client().delete_resource("opportunities/role", cls.linked_role.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("deal", cls.linked_deal.id)
            if cls.new_opportunity is not None:
                marketo_pipedrive_sync.get_marketo_client().delete_resource("opportunity", cls.new_opportunity.id)
            if cls.new_role is not None:
                marketo_pipedrive_sync.get_marketo_client().delete_resource("opportunities/role", cls.new_role.id)
            marketo_pipedrive_sync.get_marketo_client().delete_resource("company", cls.company.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("organization", cls.organization.id)
            if cls.new_company is not None:
                marketo_pipedrive_sync.get_marketo_client().delete_resource("company", cls.new_company.id)
            if cls.new_organization is not None:
                marketo_pipedrive_sync.get_pipedrive_client().delete_resource("organization", cls.new_organization.id)

    def test_create_person_in_pipedrive(self):
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.lead.id) + self.AUTHENTICATION_PARAM)
            person_id = marketo.Lead(g.marketo_client, self.lead.id).pipedriveId
            self.assertIsNotNone(person_id)  # Pipedrive ID has been updated

            person = pipedrive.Person(g.pipedrive_client, person_id)
            self.new_person = person
            self.assertIsNotNone(person)  # Person has been created
            self.assertIsNotNone(person.id)
            self.assertEquals(person.name, "Test Flask Lead")
            self.assertEquals(person.email, "lead@testflask.com")
            self.new_organization = person.organization
            self.assertIsNotNone(person.organization)  # Company has been created
            self.assertEquals(person.organization.name, "Test Flask Company")

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "created")
            self.assertEquals(data["id"], person.id)

    def test_update_person_in_pipedrive(self):
        # Update lead in Marketo
        self.linked_lead.firstName = "Foo Flask"
        self.linked_lead.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.linked_lead.id) + self.AUTHENTICATION_PARAM)
            person = pipedrive.Person(g.pipedrive_client, self.linked_person.id)
            self.assertEquals(person.name, "Foo Flask Lead")  # Person has been updated

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "updated")
            self.assertEquals(data["id"], person.id)

    def test_update_person_in_pipedrive_no_change(self):
        # Reset values
        self.linked_lead.firstName = "Test Linked Flask"
        self.linked_lead.save()
        self.linked_person.name = "Test Linked Flask Lead"
        self.linked_person.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.linked_lead.id) + self.AUTHENTICATION_PARAM)
            person = pipedrive.Person(g.pipedrive_client, self.linked_person.id)
            self.assertEquals(person.name, "Test Linked Flask Lead")

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "skipped")
            self.assertEquals(data["id"], person.id)

    def test_create_lead_in_marketo(self):
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.person.id) + self.AUTHENTICATION_PARAM)
            lead_id = pipedrive.Person(g.pipedrive_client, self.person.id).marketoid
            self.assertIsNotNone(lead_id)  # Marketo ID has been updated

            lead = marketo.Lead(g.marketo_client, lead_id)
            self.new_lead = lead
            self.assertIsNotNone(lead)  # Lead has been created
            self.assertIsNotNone(lead.id)
            self.assertEquals(lead.firstName, "Test Flask")
            self.assertEquals(lead.lastName, "Person")
            self.assertEquals(lead.email, "person@testflask.com")

            company = marketo.Company(g.marketo_client, lead.externalCompanyId, "externalCompanyId")
            self.new_company = company
            self.assertIsNotNone(company)  # Company has been created
            self.assertEquals(company.company, "Test Flask Organization")

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "created")
            self.assertEquals(data["id"], lead.id)

    def test_update_lead_in_marketo(self):
        # Update person in Pipedrive
        self.linked_person.name = "Bar Flask Lead"
        self.linked_person.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.linked_person.id) + self.AUTHENTICATION_PARAM)
            lead = marketo.Lead(g.marketo_client, self.linked_lead.id)
            self.assertEquals(lead.firstName, "Bar Flask")  # Lead has been updated

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "updated")
            self.assertEquals(data["id"], lead.id)

    def test_update_lead_in_marketo_no_change(self):
        # Reset values
        self.linked_person.name = "Test Linked Flask Lead"
        self.linked_person.save()
        self.linked_lead.firstName = "Test Linked Flask"
        self.linked_lead.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.linked_person.id) + self.AUTHENTICATION_PARAM)
            lead = marketo.Lead(g.marketo_client, self.linked_lead.id)
            self.assertEquals(lead.firstName, "Test Linked Flask")

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "skipped")
            self.assertEquals(data["id"], lead.id)

    def test_create_opportunity_and_role_in_marketo(self):
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/deal/' + str(self.deal.id) + self.AUTHENTICATION_PARAM)

            data = json.loads(rv.data)
            opportunity_id = data["opportunity"]["id"]
            opportunity = marketo.Opportunity(g.marketo_client, opportunity_id)
            self.new_opportunity = opportunity
            self.assertIsNotNone(opportunity)  # Opportunity has been created
            self.assertIsNotNone(opportunity.id)
            self.assertEquals(opportunity.externalOpportunityId, marketo.compute_external_id("deal", self.deal.id))
            self.assertEquals(opportunity.name, "Test Flask Deal")

            role_id = data["role"]["id"]
            role = marketo.Role(g.marketo_client, role_id)
            self.new_role = role
            self.assertIsNotNone(role)  # Role has been created
            self.assertIsNotNone(role.id)
            self.assertEquals(role.externalOpportunityId, marketo.compute_external_id("deal", self.deal.id))
            self.assertEquals(role.leadId, int(self.linked_person.marketoid))
            self.assertEquals(role.role, "Fake role")

            # Test return data
            self.assertEquals(data["opportunity"]["status"], "created")

    def test_update_opportunity_in_marketo(self):
        # Update deal in Pipedrive
        self.linked_deal.title = "Test Flask Linked Deal updated"
        self.linked_deal.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/deal/' + str(self.linked_deal.id) + self.AUTHENTICATION_PARAM)

            data = json.loads(rv.data)
            opportunity_id = data["opportunity"]["id"]
            opportunity = marketo.Opportunity(g.marketo_client, opportunity_id)
            self.assertEquals(opportunity.name, "Test Flask Linked Deal updated")  # Opportunity has been updated

            # Test return data
            self.assertEquals(data["opportunity"]["status"], "updated")

    def test_update_opportunity_in_marketo_no_change(self):
        # Reset values
        self.linked_deal.title = "Test Flask Linked Deal"
        self.linked_deal.save()
        self.linked_opportunity.name = "Test Flask Linked Deal"
        self.linked_opportunity.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/deal/' + str(self.linked_deal.id) + self.AUTHENTICATION_PARAM)

            data = json.loads(rv.data)
            opportunity_id = data["opportunity"]["id"]
            opportunity = marketo.Opportunity(g.marketo_client, opportunity_id)
            self.assertEquals(opportunity.name, "Test Flask Linked Deal")

            # Test return data
            self.assertEquals(data["opportunity"]["status"], "skipped")


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("pipedrive").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(SyncTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
