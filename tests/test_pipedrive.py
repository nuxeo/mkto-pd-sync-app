import unittest
from .context import pipedrive
from .context import secret
import logging


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
        self.assertEqual(getattr(person, "49f0c687b7617aa2e449353f9f5263434f6725d7"), "2016-01-23")

    def test_get_person_custom_field_nice_name(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.created_date, "2016-01-23")

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

    def test_person_no_attribute_name_equal_key(self):
        person = pipedrive.Person(self.pd)
        with self.assertRaises(AttributeError):
            person.name

    def test_add_person_from_client(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        with self.assertRaises(AttributeError):
            person.id
        self.pd.add_resource(person)
        self.assertIsNotNone(person.id)

    def test_add_person(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 2"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        with self.assertRaises(AttributeError):
            person.id
        person.save()
        self.assertIsNotNone(person.id)

if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("pipedrive").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(PipedriveTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
