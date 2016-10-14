import unittest
from .context import pipedrive
from .context import secret
import logging
import requests


class PipedriveTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pd = pipedrive.PipedriveClient(secret.PD_API_TOKEN)

    def test_get_person_from_client(self):
        person = self.pd.get_resource_by_id("person", 63080)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEqual(person.name, "Marco Antonio")
        self.assertEqual(person.email, "emeamarco@gmail.com")  # Test email was "flattened"

    def test_load_person(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEqual(person.name, "Marco Antonio")
        self.assertEqual(person.email, "emeamarco@gmail.com")

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
        self.assertIsNotNone(person)
        with self.assertRaises(AttributeError):
            person.name

    def test_add_person_from_client(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person = self.pd.add_resource("person", person.resource_data)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, "Test Person")
        # Delete created person
        self.pd.delete_resource("person", person.id)

    def test_save_person(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 2"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, "Test Person 2")
        # Delete created person
        self.pd.delete_resource("person", person.id)

    def test_get_person_undefined(self):
        with self.assertRaises(requests.HTTPError):
            pipedrive.Person(self.pd, -1)

    def test_update_person(self):
        # Get person first
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.name, "Marco Antonio")
        # Then update
        person.name = "Test Person 4"
        person.save()
        self.assertEquals(person.name, "Test Person 4")
        # Reset updated value
        person.name = "Marco Antonio"
        person.save()

    def test_add_person_custom_field(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 5"
        person.lead_score = 10
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.lead_score, 10)
        # Delete created person
        self.pd.delete_resource("person", person.id)

    def test_update_person_custom_field(self):
        # Get person first
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.lead_score, 0)
        # Then update
        person.lead_score = 10
        person.save()
        self.assertEquals(person.lead_score, 10)
        # Reset updated value
        person.lead_score = 0
        person.save()

    def test_get_organization_with_name(self):
        organization = self.pd.find_resource_by_name("organization", "MyCompany")
        self.assertIsNotNone(organization)
        self.assertIsNotNone(organization.id)
        self.assertEqual(organization.name, "MyCompany")

    def test_save_person_related_organization(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        # Load organization
        self.assertIsNotNone(person.organization)
        self.assertEqual(person.organization.name, "MyCompany")
        # Try to save
        person.save()

    def test_load_deal(self):
        deal = pipedrive.Deal(self.pd, 1653)
        self.assertIsNotNone(deal)
        self.assertIsNotNone(deal.id)
        self.assertEqual(deal.title, "MyCompany deal test")
        self.assertIsNotNone(deal.contact_person)
        self.assertEqual(deal.contact_person.name, "Marco Antonio")

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("pipedrive").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(PipedriveTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
