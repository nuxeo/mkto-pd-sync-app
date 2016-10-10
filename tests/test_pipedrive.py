import unittest
from .context import pipedrive
from .context import secret
import logging
import requests


class PipedriveTestCase(unittest.TestCase):

    def setUp(self):
        self.pd = pipedrive.PipedriveClient(secret.PD_API_TOKEN)

    def tearDown(self):
        self.pd = None

    def test_get_person_from_client(self):
        person = self.pd.get_resource_by_id("person", 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Marco Antonio")
        self.assertIsNotNone(person.email)
        self.assertEqual(person.email[0]["value"], "emeamarco@gmail.com")

    def test_load_person_from_resource(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Marco Antonio")
        self.assertIsNotNone(person.email)
        self.assertEqual(person.email[0]["value"], "emeamarco@gmail.com")

    def test_get_person_custom_field(self):  # i.e. hash field
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(getattr(person, "88ec7b3fd70f2fbdabe9aded639e316ff29174ce"), 0)  # Lead score

    def test_get_person_custom_field_nice_name(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.lead_score, 0)

    def test_get_person_undefined_field(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        with self.assertRaises(AttributeError):
            person.fake_field

    def test_get_person_related_organization(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.organization)
        self.assertEqual(person.organization.name, "MyCompany")

    def test_empty_person_with_field_name_equals_key(self):
        person = pipedrive.Person(self.pd)
        with self.assertRaises(AttributeError):
            person.name

    def test_dump_person_from_client(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person = self.pd.add_resource("person", person.resource_data)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, "Test Person")
        # TODO: delete at tear down

    def test_add_person(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 2"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, "Test Person 2")
        # TODO: delete at tear down

    def test_get_person_undefined(self):
        with self.assertRaises(requests.HTTPError):
            pipedrive.Person(self.pd, -1)

    def test_update_person(self):
        # Create a person first
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 3"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person.id)
        person_id = person.id  # Save id for later
        self.assertEquals(person.name, "Test Person 3")
        # Then update
        person.name = "Test Person 4"
        person.save()
        person = pipedrive.Person(self.pd, person_id)
        self.assertEquals(person.name, "Test Person 4")
        # TODO: delete at tear down


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("pipedrive").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(PipedriveTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
