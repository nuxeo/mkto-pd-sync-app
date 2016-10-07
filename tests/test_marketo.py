import unittest
from .context import marketo
from .context import secret
import logging
import requests


class MarketoTestCase(unittest.TestCase):

    def setUp(self):
        self.mkto = marketo.MarketoClient(secret.IDENTITY_ENDPOINT, secret.CLIENT_ID, secret.CLIENT_SECRET, secret.API_ENDPOINT)

    def tearDown(self):
        self.mkto = None

    def test_get_lead_from_client(self):
        lead = self.mkto.get_resource_by_id("lead", 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, "Marco")
        self.assertEqual(lead.lastName, "Antonio")
        self.assertEqual(lead.email, "emeamarco@gmail.com")

    def test_load_lead_from_resource(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, "Marco")
        self.assertEqual(lead.lastName, "Antonio")
        self.assertEqual(lead.email, "emeamarco@gmail.com")

    def test_get_lead_not_default_field(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.pipedriveId, 63080)

    def test_get_lead_undefined_field(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        with self.assertRaises(AttributeError):
            lead.fake_field

    # def test_get_person_related_organization(self):
    #     person = pipedrive.Person(self.mkto, 63080)
    #     self.assertIsNotNone(person)
    #     self.assertIsNotNone(person.organization)
    #     self.assertEqual(person.organization.name, "MyCompany")

    # def test_add_person_from_client(self):
    #     person = pipedrive.Person(self.mkto)
    #     person.name = "Test Person"
    #     person.owner_id = 1628545  # my (Helene Jonin) owner id
    #     self.assertIsNone(person.id)
    #     person = self.mkto.add_resource("person", person.resource_data_to_update)
    #     self.assertIsNotNone(person.id)
    #     self.assertEquals(person.name, "Test Person")
    #     # TODO: delete at tear down
    #
    # def test_add_person(self):
    #     person = pipedrive.Person(self.mkto)
    #     person.name = "Test Person 2"
    #     person.owner_id = 1628545  # my (Helene Jonin) owner id
    #     self.assertIsNone(person.id)
    #     person.save()
    #     self.assertIsNotNone(person.id)
    #     self.assertEquals(person.name, "Test Person 2")
    #     # TODO: delete at tear down

    def test_get_lead_undefined(self):
        lead = marketo.Lead(self.mkto, -1)
        self.assertIsNotNone(lead)
    #
    # def test_update_person(self):
    #     person = pipedrive.Person(self.mkto, 63194)
    #     self.assertEquals(person.name, "Test LN")
    #     person.name = "Test LN 2"
    #     person.save()
    #     self.assertEquals(person.name, "Test LN 2")
    #     # Reset value
    #     person.name = "Test LN"
    #     person.save()


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("marketo").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(MarketoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
