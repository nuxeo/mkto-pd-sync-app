import unittest
from .context import marketo_pipedrive_sync
from .context import marketo
from .context import pipedrive
import logging
from flask import g


class SyncTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        with marketo_pipedrive_sync.app.app_context():
            # Create Lead in Marketo not linked with any person in Pipedrive
            lead = marketo.Lead(marketo_pipedrive_sync.get_marketo_client())
            lead.firstName = "Test Flask"
            lead.lastName = "Lead"
            lead.email = "lead@testflask.com"
            lead.save()
            cls.lead = lead

            # Create Person in Pipedrive not linked with any lead in Marketo
            person = pipedrive.Person(marketo_pipedrive_sync.get_pipedrive_client())
            person.name = "Test Flask Person"
            person.email = "person@testflask.com"
            person.owner_id = 1628545  # my (Helene Jonin) owner id
            person.save()
            cls.person = person

            # Create Lead in Marketo linked with a person in Pipedrive
            linked_lead = marketo.Lead(marketo_pipedrive_sync.get_marketo_client())
            linked_lead.firstName = "Test Linked Flask"
            linked_lead.lastName = "Lead"
            linked_lead.email = "lead@testlinkedflask.com"
            linked_lead.save()
            cls.linked_lead = linked_lead

            # Create Person in Pipedrive linked with a lead in Marketo
            linked_person = pipedrive.Person(marketo_pipedrive_sync.get_pipedrive_client())
            linked_person.name = "Test Linked Flask Person"
            linked_person.email = "person@testlinkedflask.com"
            linked_person.owner_id = 1628545  # my (Helene Jonin) owner id
            linked_person.save()
            cls.linked_person = linked_person

            # Set the links
            cls.linked_lead.pipedriveId = cls.linked_person.id
            cls.linked_person.marketoid = cls.linked_lead.id

    @classmethod
    def tearDownClass(cls):
        with marketo_pipedrive_sync.app.app_context():
            # Delete created Leads and Persons
            marketo_pipedrive_sync.get_marketo_client().delete_resource("lead", cls.lead.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("person", cls.person.id)
            marketo_pipedrive_sync.get_marketo_client().delete_resource("lead", cls.linked_lead.id)
            marketo_pipedrive_sync.get_pipedrive_client().delete_resource("person", cls.linked_person.id)

    def setUp(self):
        # Assert Persons and Leads are created
        self.assertIsNotNone(self.lead)
        self.assertIsNotNone(self.person)
        self.assertIsNotNone(self.linked_lead)
        self.assertIsNotNone(self.linked_person)

    def test_create_person_in_pipedrive(self):
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.lead.id))
            person_id = g.marketo_client.get_resource_by_id("lead", self.lead.id, ["firstName", "lastName", "email", "pipedriveId"]).pipedriveId
            self.assertIsNotNone(person_id)  # Pipedrive ID has been updated
            person = g.pipedrive_client.get_resource_by_id("person", person_id)
            self.assertIsNotNone(person)  # Person has been created
            self.assertIsNotNone(person.id)
            self.assertEquals(person.name, "Test Flask Lead")
            self.assertEquals(person.email, "lead@testflask.com")

    def test_update_person_in_pipedrive(self):
        # Update lead in Marketo
        self.linked_lead.firstName = "Foo Flask"
        self.linked_lead.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/marketo/lead/' + str(self.linked_lead.id))
            person = g.pipedrive_client.get_resource_by_id("person", self.linked_person.id)
            self.assertEquals(person.name, "Foo Flask Lead")  # Person has been updated

    @unittest.skip("Test when webhook will be disabled to prevent from conflicts")
    def test_create_lead_in_marketo(self):
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.person.id))
            lead_id = g.pipedrive_client.get_resource_by_id("person", self.lead.id).marketoid
            self.assertIsNotNone(lead_id)  # Marketo ID has been updated
            lead = g.marketo_client.get_resource_by_id("lead", lead_id, ["firstName", "lastName", "email", "pipedriveId"])
            self.assertIsNotNone(lead)  # Lead has been created
            self.assertIsNotNone(lead.id)
            self.assertEquals(lead.firstName, "Test Flask")
            self.assertEquals(lead.lastName, "Person")
            self.assertEquals(lead.email, "person@testflask.com")

    def test_update_lead_in_marketo(self):
        # Update person in Pipedrive
        self.linked_person.name = "Bar Flask Lead"
        self.linked_person.save()
        with marketo_pipedrive_sync.app.test_client() as c:
            rv = c.post('/pipedrive/person/' + str(self.linked_person.id))
            lead = g.marketo_client.get_resource_by_id("lead", self.linked_lead.id)
            self.assertEquals(lead.firstName, "Bar Flask")  # Lead has been updated

    # TODO: test "Nothing to do"

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("pipedrive").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(SyncTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
