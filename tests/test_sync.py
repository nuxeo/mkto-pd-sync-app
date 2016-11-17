from .context import marketo
from .context import pipedrive
from .context import secret
from .context import sync

import datetime
import json
import logging
import unittest


class SyncTestCase(unittest.TestCase):
    AUTHENTICATION_PARAM = "?api_key=" + secret.FLASK_AUTHORIZED_KEYS[0]

    @classmethod
    def setUpClass(cls):
        cls.context = sync.app.app_context()
        cls.context.push()

        # Create company to be linked with Marketo lead
        company = marketo.Company(sync.get_marketo_client())
        company.externalCompanyId = "testFlaskCompany"
        company.company = "Test Flask Company"
        company.billingStreet = "11th St"
        company.billingCity = "New York"
        company.billingState = "NY"
        company.billingCountry = "United States"
        company.mainPhone = "0123456789"
        company.industry = "Finance"
        company.annualRevenue = 1000000
        company.numberOfEmployees = 10
        company.save()
        cls.company = company

        # Create lead in Marketo not linked with any person in Pipedrive
        lead = marketo.Lead(sync.get_marketo_client())
        lead.firstName = "Test Flask"
        lead.lastName = "Lead"
        lead.email = "lead@testflask.com"
        lead.externalCompanyId = cls.company.externalCompanyId
        lead.title = "Manager"
        lead.phone = "9876543210"
        lead.leadSource = "Organic Search"
        lead.conversicaLeadOwnerEmail = "hjonin@nuxeo.com"
        lead.conversicaLeadOwnerFirstName = "Helene"
        lead.conversicaLeadOwnerLastName = "Jonin"
        lead.leadStatus = "Recycled"
        # lead.inferredCountry = "Italy"  # Not updateable
        # lead.createdAt = "2016-11-14 03:42:00"  # Not updateable
        # lead.inferredStateRegion = "Italy"  # Not updateable
        # lead.inferredCity = "Milano"  # Not updateable
        lead.leadScore = 10
        lead.mKTODateSQL = "2016-11-16 03:45:00"
        lead.save()
        cls.lead = lead

        # Create another lead in Marketo not linked with any person in Pipedrive
        lead_company_form_fields = marketo.Lead(sync.get_marketo_client())
        lead_company_form_fields.firstName = "Test Other Flask"
        lead_company_form_fields.lastName = "Lead"
        lead_company_form_fields.email = "lead2@testflask.com"
        # Company form fields
        lead_company_form_fields.website = "another-flask-company.com"
        lead_company_form_fields.country = "Canada"
        lead_company_form_fields.save()
        cls.lead_company_form_fields = lead_company_form_fields

        # Create organization to be linked with Pipedrive person
        organization = pipedrive.Organization(sync.get_pipedrive_client())
        organization.name = "Test Flask Organization"
        organization.address = "Rue Mouffetard"
        organization.city = "Paris"
        organization.state = "France"
        organization.country = "France"
        organization.company_phone = "0192837465"
        organization.industry = "Consulting"
        organization.annual_revenue = 2000000
        organization.number_of_employees = 20
        organization.save()
        cls.organization = organization

        # Create person in Pipedrive not linked with any lead in Marketo
        person = pipedrive.Person(sync.get_pipedrive_client())
        person.name = "Test Flask Person"
        person.email = "person@testflask.com"
        person.org_id = cls.organization.id
        person.title = "Dev"
        person.phone = "5647382910"
        person.inferred_country = "Germany"
        person.lead_source = "Direct Traffic"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        person.created_date = "2016-11-16T03:11:00Z"
        person.state = "Germany"
        person.city = "Munich"
        person.lead_score = 15
        person.date_sql = "2016-11-16T03:12:00Z"
        person.lead_status = "Disqualified"
        person.save()
        cls.person = person

        # Create organization to be linked with Pipedrive linked person and linked with a company in Marketo
        linked_organization = pipedrive.Organization(sync.get_pipedrive_client())
        linked_organization.save()
        cls.linked_organization = linked_organization

        # Create company to be linked with Marketo linked lead and linked with an organization in Pipedrive
        linked_company = marketo.Company(sync.get_marketo_client())
        linked_company.externalCompanyId = marketo.compute_external_id("organization", cls.linked_organization.id)
        linked_company.save()
        cls.linked_company = linked_company

        # Create lead in Marketo linked with a person in Pipedrive
        linked_lead = marketo.Lead(sync.get_marketo_client())
        linked_lead.externalCompanyId = cls.linked_company.externalCompanyId
        linked_lead.save()
        cls.linked_lead = linked_lead

        # Create person in Pipedrive linked with a lead in Marketo
        linked_person = pipedrive.Person(sync.get_pipedrive_client())
        linked_person.org_id = cls.linked_organization.id
        linked_person.save()
        cls.linked_person = linked_person

        # Set the links
        cls.linked_lead.pipedriveId = cls.linked_person.id
        cls.linked_person.marketoid = cls.linked_lead.id
        cls.linked_lead.save()
        cls.linked_person.save()

        # Create deal in Pipedrive
        deal = pipedrive.Deal(sync.get_pipedrive_client())
        deal.title = "Test Flask Deal"
        deal.type = "New Business"
        deal.deal_description = "Dummy description 1"
        deal.last_activity_date = "2016-11-14"
        deal.status = "open"
        deal.value = 10000
        deal.close_time = None  # Not closed -> no close date
        deal.stage_id = 34  # First stage id of "NX Subscription (New and Upsell)" pipeline
        deal.person_id = cls.linked_person.id
        deal.user_id = 1628545  # my (Helene Jonin) owner id
        deal.save()
        cls.deal = deal

        # Create deal in Pipedrive linked with an opportunity in Marketo
        linked_deal = pipedrive.Deal(sync.get_pipedrive_client())
        linked_deal.person_id = cls.linked_person.id
        linked_deal.last_activity_date = "2016-11-15"
        linked_deal.save()
        cls.linked_deal = linked_deal

        # Create opportunity and role in Marketo linked with a deal in Pipedrive
        linked_opportunity = marketo.Opportunity(sync.get_marketo_client())
        linked_opportunity.externalOpportunityId = marketo.compute_external_id("deal", linked_deal.id)
        linked_opportunity.save()
        cls.linked_opportunity = linked_opportunity
        linked_role = marketo.Role(sync.get_marketo_client())
        linked_role.externalOpportunityId = linked_opportunity.externalOpportunityId
        linked_role.leadId = cls.linked_lead.id
        linked_role.role = "Default Role"
        linked_role.save()
        cls.linked_role = linked_role

    @classmethod
    def tearDownClass(cls):
        # Delete created resources
        sync.get_marketo_client().delete_resource("lead", cls.lead.id)
        sync.get_marketo_client().delete_resource("lead", cls.lead_company_form_fields.id)
        sync.get_pipedrive_client().delete_resource("person", cls.person.id)
        sync.get_marketo_client().delete_resource("lead", cls.linked_lead.id)
        sync.get_pipedrive_client().delete_resource("person", cls.linked_person.id)
        sync.get_pipedrive_client().delete_resource("deal", cls.deal.id)
        sync.get_marketo_client().delete_resource("opportunity", cls.linked_opportunity.id)
        sync.get_marketo_client().delete_resource("opportunities/role", cls.linked_role.id)
        sync.get_pipedrive_client().delete_resource("deal", cls.linked_deal.id)
        sync.get_marketo_client().delete_resource("company", cls.company.externalCompanyId, "externalCompanyId")
        sync.get_pipedrive_client().delete_resource("organization", cls.organization.id)
        sync.get_marketo_client().delete_resource("company", cls.linked_company.externalCompanyId, "externalCompanyId")
        sync.get_pipedrive_client().delete_resource("organization", cls.linked_organization.id)

        cls.context.pop()

    def test_authentication_error(self):
        with sync.app.test_client() as c:
            # rv = c.post('/marketo/lead/' + str(self.lead.id))
            rv = c.post('/marketo/lead/1')
            rv.status_code = 401
            rv.message = "Authentication required"

    def test_create_person_in_pipedrive(self):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.lead.id) + self.AUTHENTICATION_PARAM)
            person_id = marketo.Lead(sync.get_marketo_client(), self.lead.id).pipedriveId
            self.assertIsNotNone(person_id)  # Pipedrive id has been updated

            person = pipedrive.Person(sync.get_pipedrive_client(), person_id)
            self.assertIsNotNone(person)  # Person has been created
            self.assertIsNotNone(person.id)
            self.assertEquals(person.name, "Test Flask Lead")
            self.assertEquals(person.email, "lead@testflask.com")
            self.assertIsNotNone(person.org_id)
            self.assertEquals(person.title, "Manager")
            self.assertEquals(person.phone, "9876543210")
            self.assertEquals(person.inferred_country, "United States")
            self.assertEquals(person.lead_source, "Organic Search")
            self.assertEquals(person.owner_id, 1628545)
            self.assertEquals(person.created_date, datetime.datetime.today().strftime("%Y-%m-%d"))
            self.assertEquals(person.state, "NY")
            self.assertEquals(person.city, "New York")
            self.assertEquals(person.lead_score, 10)
            self.assertEquals(person.date_sql, "2016-11-16")
            self.assertEquals(person.lead_status, "Recycled")

            # Test Organization sync
            self.assertIsNotNone(person.organization)  # Organization has been created
            self.assertEquals(person.organization.name, "Test Flask Company")
            self.assertEquals(person.organization.address, "11th St")
            self.assertEquals(person.organization.city, "New York")
            self.assertEquals(person.organization.state, "NY")
            self.assertEquals(person.organization.country, "United States")
            self.assertEquals(person.organization.company_phone, "0123456789")
            self.assertEquals(person.organization.industry, "Finance")
            self.assertEquals(person.organization.annual_revenue, 1000000)
            self.assertEquals(person.organization.number_of_employees, 10)

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "created")
            self.assertEquals(data["id"], person.id)

            # Delete created resources
            sync.get_pipedrive_client().delete_resource("person", person.id)
            sync.get_pipedrive_client().delete_resource("organization", person.organization.id)

    def test_update_person_in_pipedrive(self):
        # Set linked lead
        self.linked_lead.firstName = "Test Linked Flask"
        self.linked_lead.lastName = "Lead"
        self.linked_lead.email = "lead@testlinkedflask.com"
        self.linked_lead.title = "Accountant"
        self.linked_lead.phone = "1357924680"
        self.linked_lead.leadSource = "Product"
        self.linked_lead.conversicaLeadOwnerFirstName = "Helene"
        self.linked_lead.conversicaLeadOwnerLastName = "Jonin"
        self.linked_lead.conversicaLeadOwnerEmail = "hjonin@nuxeo.com"
        self.linked_lead.leadStatus = "Prospect"
        # self.linked_lead.inferredCountry = "Spain"  # Not updateable
        # self.linked_lead.createdAt = "2016-11-13 04:05:00"  # Not updateable
        # self.linked_lead.inferredStateRegion = "Spain"  # Not updateable
        # self.linked_lead.inferredCity = "Barcelona"  # Not updateable
        self.linked_lead.leadScore = 13
        self.linked_lead.mKTODateSQL = "2016-11-16 04:06:00"
        self.linked_lead.save()
        self.linked_company.company = "Test Flask Linked Company"
        self.linked_company.save()
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.linked_lead.id) + self.AUTHENTICATION_PARAM)
            person = pipedrive.Person(sync.get_pipedrive_client(), self.linked_person.id)
            self.assertEquals(person.name, "Test Linked Flask Lead")  # Person has been updated
            self.assertEquals(person.email, "lead@testlinkedflask.com")
            self.assertIsNotNone(person.org_id)
            self.assertEquals(person.title, "Accountant")
            self.assertEquals(person.phone, "1357924680")
            # self.assertEquals(person.inferred_country, "Spain")  # Because not updateable
            self.assertEquals(person.lead_source, "Product")
            self.assertEquals(person.owner_id, 1628545)
            self.assertEquals(person.created_date, datetime.datetime.today().strftime("%Y-%m-%d"))
            # self.assertEquals(person.state, "Spain")  # Because not updateable
            # self.assertEquals(person.city, "Barcelona")  # Because not updateable
            self.assertEquals(person.lead_score, 13)
            self.assertEquals(person.date_sql, "2016-11-16")
            self.assertEquals(person.lead_status, "Prospect")

            # Test Organization sync
            organization = pipedrive.Organization(sync.get_pipedrive_client(), person.organization.id)  # Force reload
            self.assertEquals(organization.name, "Test Flask Linked Company")  # Organization has been updated

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "updated")
            self.assertEquals(data["id"], person.id)

    def test_update_person_in_pipedrive_no_change(self):
        # Sync values
        self.linked_lead.firstName = "Test Linked Flask"
        self.linked_lead.lastName = "Person"
        self.linked_lead.email = "person@testlinkedflask.com"
        self.linked_lead.title = "Consultant"
        self.linked_lead.phone = "2468013579"
        self.linked_lead.leadSource = "Web Referral"
        self.linked_lead.conversicaLeadOwnerFirstName = "Helene"
        self.linked_lead.conversicaLeadOwnerLastName = "Jonin"
        self.linked_lead.conversicaLeadOwnerEmail = "hjonin@nuxeo.com"
        self.linked_lead.leadStatus = "MQL"
        # self.linked_lead.inferredCountry = "United Kingdom"  # Not updateable
        # self.linked_lead.createdAt = "2016-11-16 03:19:00"  # Not updateable
        # self.linked_lead.inferredStateRegion = "United Kingdom"  # Not updateable
        # self.linked_lead.inferredCity = "London"  # Not updateable
        self.linked_lead.leadScore = 30
        self.linked_lead.mKTODateSQL = "2016-11-16 03:20:00"
        self.linked_lead.save()
        self.linked_person.name = "Test Linked Flask Person"
        self.linked_person.email = "person@testlinkedflask.com"
        self.linked_person.title = "Consultant"
        self.linked_person.phone = "2468013579"
        self.linked_person.inferred_country = None  # Because not updateable
        self.linked_person.lead_source = "Web Referral"
        self.linked_person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.linked_person.created_date = datetime.datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
        self.linked_person.state = None  # Because not updateable
        self.linked_person.city = None  # Because not updateable
        self.linked_person.lead_score = 30
        self.linked_person.date_sql = "2016-11-16T03:20:00Z"
        self.linked_person.lead_status = "MQL"
        self.linked_person.save()
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.linked_lead.id) + self.AUTHENTICATION_PARAM)
            person = pipedrive.Person(sync.get_pipedrive_client(), self.linked_person.id)

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "skipped")
            self.assertEquals(data["id"], person.id)

    def test_create_lead_in_marketo(self):
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.person.id) + self.AUTHENTICATION_PARAM)
            lead_id = pipedrive.Person(sync.get_pipedrive_client(), self.person.id).marketoid
            self.assertIsNotNone(lead_id)  # Marketo id has been updated

            lead = marketo.Lead(sync.get_marketo_client(), lead_id)
            self.assertIsNotNone(lead)  # Lead has been created
            self.assertIsNotNone(lead.id)
            self.assertEquals(lead.firstName, "Test Flask")
            self.assertEquals(lead.lastName, "Person")
            self.assertEquals(lead.email, "person@testflask.com")
            self.assertIsNotNone(lead.externalCompanyId)
            self.assertEquals(lead.title, "Dev")
            self.assertEquals(lead.phone, "5647382910")
            self.assertEquals(lead.leadSource, "Direct Traffic")
            self.assertEquals(lead.conversicaLeadOwnerEmail, "hjonin@nuxeo.com")
            self.assertEquals(lead.conversicaLeadOwnerFirstName, "Helene")
            self.assertEquals(lead.conversicaLeadOwnerLastName, "Jonin")
            self.assertEquals(lead.leadStatus, "Disqualified")

            # Test Company sync
            company = marketo.Company(sync.get_marketo_client(), lead.externalCompanyId, "externalCompanyId")
            self.assertIsNotNone(company)  # Company has been created
            self.assertEquals(company.company, "Test Flask Organization")
            self.assertEquals(company.billingStreet, "Rue Mouffetard")
            self.assertEquals(company.billingCity, u"Paris")
            self.assertEquals(company.billingState, "France")
            self.assertEquals(company.billingCountry, "France")
            self.assertEquals(company.mainPhone, "0192837465")
            self.assertEquals(company.industry, "Consulting")
            self.assertEquals(company.annualRevenue, 2000000)
            self.assertEquals(company.numberOfEmployees, 20)

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "created")
            self.assertEquals(data["id"], lead.id)

            # Delete created resources
            sync.get_marketo_client().delete_resource("lead", lead.id)
            sync.get_marketo_client().delete_resource("company", company.externalCompanyId, "externalCompanyId")

    def test_update_lead_in_marketo(self):
        # Set linked person
        self.linked_person.name = "Test Linked Flask Person"
        self.linked_person.email = "person@testlinkedflask.com"
        self.linked_person.title = "Consultant"
        self.linked_person.phone = "2468013579"
        self.linked_person.inferred_country = "United Kingdom"
        self.linked_person.lead_source = "Web Referral"
        self.linked_person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.linked_person.created_date = "2016-11-16T03:19:00Z"
        self.linked_person.state = "United Kingdom"
        self.linked_person.city = "London"
        self.linked_person.lead_score = 30
        self.linked_person.date_sql = "2016-11-16T03:20:00Z"
        self.linked_person.lead_status = "MQL"
        self.linked_person.save()
        self.linked_organization.name = "Test Flask Linked Organization"
        self.linked_organization.save()
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.linked_person.id) + self.AUTHENTICATION_PARAM)
            lead = marketo.Lead(sync.get_marketo_client(), self.linked_lead.id)
            self.assertEquals(lead.firstName, "Test Linked Flask")  # Lead has been updated
            self.assertEquals(lead.lastName, "Person")
            self.assertEquals(lead.email, "person@testlinkedflask.com")
            self.assertEquals(lead.externalCompanyId, self.linked_company.externalCompanyId)
            self.assertEquals(lead.title, "Consultant")
            self.assertEquals(lead.phone, "2468013579")
            self.assertEquals(lead.leadSource, "Web Referral")
            self.assertEquals(lead.conversicaLeadOwnerEmail, "hjonin@nuxeo.com")
            self.assertEquals(lead.conversicaLeadOwnerFirstName, "Helene")
            self.assertEquals(lead.conversicaLeadOwnerLastName, "Jonin")
            self.assertEquals(lead.leadStatus, "MQL")

            # Test Company sync
            company = marketo.Company(sync.get_marketo_client(), self.linked_company.externalCompanyId, "externalCompanyId")
            self.assertEquals(company.id, self.linked_company.id)
            self.assertEquals(company.company, "Test Flask Linked Organization")  # Company has been updated

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "updated")
            self.assertEquals(data["id"], lead.id)

    def test_update_lead_in_marketo_no_change(self):
        # Sync values
        self.linked_person.name = "Test Linked Flask Lead"
        self.linked_person.email = "lead@testlinkedflask.com"
        self.linked_person.title = "Accountant"
        self.linked_person.phone = "1357924680"
        # self.linked_person.inferred_country = "Spain"  # Because not updateable
        self.linked_person.lead_source = "Product"
        self.linked_person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.linked_person.created_date = "2016-11-13 04:05:00"
        # self.linked_person.state = "Spain"  # Because not updateable
        # self.linked_person.city = "Barcelona"  # Because not updateable
        self.linked_person.lead_score = 13
        self.linked_person.date_sql = "2016-11-16 04:06:00"
        self.linked_person.lead_status = "Prospect"
        self.linked_person.save()
        self.linked_lead.firstName = "Test Linked Flask"
        self.linked_lead.lastName = "Lead"
        self.linked_lead.email = "lead@testlinkedflask.com"
        self.linked_lead.title = "Accountant"
        self.linked_lead.phone = "1357924680"
        self.linked_lead.leadSource = "Product"
        self.linked_lead.conversicaLeadOwnerFirstName = "Helene"
        self.linked_lead.conversicaLeadOwnerLastName = "Jonin"
        self.linked_lead.conversicaLeadOwnerEmail = "hjonin@nuxeo.com"
        self.linked_lead.leadStatus = "Prospect"
        # self.linked_lead.inferredCountry = "Spain"  # Not updateable
        # self.linked_lead.createdAt = "2016-11-13 04:05:00"  # Not updateable
        # self.linked_lead.inferredStateRegion = "Spain"  # Not updateable
        # self.linked_lead.inferredCity = "Barcelona"  # Not updateable
        self.linked_lead.leadScore = 13
        self.linked_lead.mKTODateSQL = "2016-11-16 04:06:00"
        self.linked_lead.save()
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.linked_person.id) + self.AUTHENTICATION_PARAM)
            lead = marketo.Lead(sync.get_marketo_client(), self.linked_lead.id)

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "skipped")
            self.assertEquals(data["id"], lead.id)

    def test_create_opportunity_and_role_in_marketo(self):
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/deal/' + str(self.deal.id) + self.AUTHENTICATION_PARAM)

            data = json.loads(rv.data)
            opportunity_id = data["opportunity"]["id"]
            opportunity = marketo.Opportunity(sync.get_marketo_client(), opportunity_id)
            self.assertIsNotNone(opportunity)  # Opportunity has been created
            self.assertIsNotNone(opportunity.id)
            self.assertEquals(opportunity.externalOpportunityId, marketo.compute_external_id("deal", self.deal.id))
            self.assertEquals(opportunity.name, "Test Flask Deal")
            self.assertEquals(opportunity.type, "New Business")
            self.assertEquals(opportunity.description, "Dummy description 1")
            self.assertEquals(opportunity.lastActivityDate, "2016-11-14")
            self.assertEquals(opportunity.isClosed, False)
            self.assertEquals(opportunity.isWon, False)
            self.assertEquals(opportunity.amount, 10000)
            self.assertIsNone(opportunity.closeDate)  # Not closed -> no close date
            self.assertEquals(opportunity.stage, "Sales Qualified Lead")
            self.assertIsNone(opportunity.fiscalQuarter)  # Not closed -> no close date
            self.assertIsNone(opportunity.fiscalYear)  # Not closed -> no close date

            role_id = data["role"]["id"]
            role = marketo.Role(sync.get_marketo_client(), role_id)
            self.assertIsNotNone(role)  # Role has been created
            self.assertIsNotNone(role.id)
            self.assertEquals(role.externalOpportunityId, marketo.compute_external_id("deal", self.deal.id))
            self.assertEquals(role.leadId, int(self.linked_person.marketoid))
            self.assertEquals(role.role, "Default Role")

            # Test return data
            self.assertEquals(data["opportunity"]["status"], "created")

            # Delete created resources
            sync.get_marketo_client().delete_resource("opportunity", opportunity.id)
            sync.get_marketo_client().delete_resource("opportunities/role", role.id)

    def test_update_opportunity_in_marketo(self):
        # Set linked deal
        self.linked_deal.title = "Test Flask Linked Deal"
        self.linked_deal.type = "Consulting"
        self.linked_deal.deal_description = "Dummy description 2"
        self.linked_deal.status = "lost"
        self.linked_deal.value = 20000
        self.linked_deal.close_time = "2016-11-16 03:30:00"
        self.linked_deal.stage_id = 34  # First stage id of "NX Subscription (New and Upsell)" pipeline
        self.linked_deal.user_id = 1628545  # my (Helene Jonin) owner id
        self.linked_deal.save()
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/deal/' + str(self.linked_deal.id) + self.AUTHENTICATION_PARAM)

            data = json.loads(rv.data)
            opportunity_id = data["opportunity"]["id"]
            opportunity = marketo.Opportunity(sync.get_marketo_client(), opportunity_id)
            self.assertEquals(opportunity.name, "Test Flask Linked Deal")  # Opportunity has been updated
            self.assertEquals(opportunity.type, "Consulting")
            self.assertEquals(opportunity.description, "Dummy description 2")
            self.assertEquals(opportunity.lastActivityDate, "2016-11-15")
            self.assertEquals(opportunity.isClosed, True)
            self.assertEquals(opportunity.isWon, False)
            self.assertEquals(opportunity.amount, 20000)
            self.assertEquals(opportunity.closeDate, "2016-11-16")
            self.assertEquals(opportunity.stage, "Sales Qualified Lead")
            self.assertEquals(opportunity.fiscalQuarter, 4)
            self.assertEquals(opportunity.fiscalYear, 2016)

            # Test return data
            self.assertEquals(data["opportunity"]["status"], "updated")

    def test_update_opportunity_in_marketo_no_change(self):
        # Sync values
        self.linked_deal.title = "Test Flask Linked Opportunity"
        self.linked_deal.type = "Upsell"
        self.linked_deal.deal_description = "Dummy description 3"
        self.linked_deal.status = "lost"
        self.linked_deal.value = 15000
        self.linked_deal.close_time = "2016-11-16 03:36:00"
        self.linked_deal.stage_id = 34  # First stage id of "NX Subscription (New and Upsell)" pipeline
        self.linked_deal.user_id = 1628545  # my (Helene Jonin) owner id
        self.linked_deal.save()
        self.linked_opportunity.name = "Test Flask Linked Opportunity"
        self.linked_opportunity.type = "Upsell"
        self.linked_opportunity.description = "Dummy description 3"
        self.linked_opportunity.lastActivityDate = "2016-11-15"
        self.linked_opportunity.isClosed = True
        self.linked_opportunity.isWon = False
        self.linked_opportunity.amount = 15000
        self.linked_opportunity.closeDate = "2016-11-16 03:36:00"
        self.linked_opportunity.stage = "Sales Qualified Lead"  # First stage of "NX Subscription (New and Upsell)" pipeline
        self.linked_opportunity.fiscalQuarter = 4
        self.linked_opportunity.fiscalYear = 2016
        self.linked_opportunity.save()
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/deal/' + str(self.linked_deal.id) + self.AUTHENTICATION_PARAM)

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["opportunity"]["status"], "skipped")

    def test_delete_person_in_pipedrive(self):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.person.id) + "/delete" + self.AUTHENTICATION_PARAM)
            person = pipedrive.Person(sync.get_pipedrive_client(), self.person.id)
            self.assertIsNotNone(person)
            self.assertIsNone(person.id)  # Person has been deleted

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "deleted")
            self.assertEquals(data["id"], self.person.id)

    def test_delete_person_in_marketo(self):
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.lead.id) + "/delete" + self.AUTHENTICATION_PARAM)
            lead = marketo.Lead(sync.get_marketo_client(), self.lead.id)
            self.assertIsNotNone(lead)
            self.assertIsNotNone(lead.id)  # Lead has been deleted
            self.assertTrue(lead.toDelete)  # Lead has been deleted

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "Ready for deletion")
            self.assertEquals(data["id"], self.lead.id)

    def test_create_person_in_pipedrive_company_form_fields(self):
        with sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.lead_company_form_fields.id) + self.AUTHENTICATION_PARAM)
            lead = marketo.Lead(sync.get_marketo_client(), self.lead_company_form_fields.id)
            self.assertIsNotNone(lead.externalCompanyId)  # Company has been created
            company = marketo.Company(sync.get_marketo_client(), lead.externalCompanyId, "externalCompanyId")
            self.assertEquals(company.company, "another-flask-company.com")
            self.assertEquals(company.billingCountry, "Canada")

            person_id = lead.pipedriveId
            self.assertIsNotNone(person_id)  # Pipedrive id has been updated

            person = pipedrive.Person(sync.get_pipedrive_client(), person_id)
            self.assertIsNotNone(person)  # Person has been created
            self.assertIsNotNone(person.id)
            self.assertEquals(person.name, "Test Other Flask Lead")
            self.assertEquals(person.email, "lead2@testflask.com")
            self.assertIsNotNone(person.org_id)

            # Test Organization sync
            self.assertIsNotNone(person.organization)  # Organization has been created
            self.assertEquals(person.organization.name, "another-flask-company.com")
            self.assertEquals(person.organization.country, "Canada")

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "created")
            self.assertEquals(data["id"], person.id)

            # Delete created resources
            sync.get_pipedrive_client().delete_resource("person", person.id)
            sync.get_pipedrive_client().delete_resource("organization", person.organization.id)

    def test_update_company_in_marketo_find_by_name(self):
        # Create company and organization with same name but not linked together
        company = marketo.Company(sync.get_marketo_client())
        company.externalCompanyId = "testFlaskUnlinkedOrganization"
        company.company = "Test Flask Unlinked Organization"
        company.numberOfEmployees = 14
        company.save()
        organization = pipedrive.Organization(sync.get_pipedrive_client())
        organization.name = "Test Flask Unlinked Organization"
        organization.number_of_employees = 15
        organization.save()
        with sync.app.test_client() as c:
            rv = c.post('/pipedrive/organization/' + str(organization.id) + self.AUTHENTICATION_PARAM)

            updated_company = marketo.Company(sync.get_marketo_client(), company.externalCompanyId, "externalCompanyId")
            self.assertEquals(updated_company.id, company.id)
            self.assertEquals(updated_company.company, company.company)
            self.assertEquals(updated_company.numberOfEmployees, 15)  # Company has been updated

            # Test return data
            data = json.loads(rv.data)
            self.assertEquals(data["status"], "updated")
            self.assertEquals(data["id"], updated_company.id)

            # Delete created resources
            sync.get_marketo_client().delete_resource("company", company.externalCompanyId, "externalCompanyId")
            sync.get_pipedrive_client().delete_resource("organization", organization.id)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("marketo").setLevel(logging.WARNING)
    logging.getLogger("pipedrive").setLevel(logging.WARNING)
    logging.getLogger("sync").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(SyncTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
