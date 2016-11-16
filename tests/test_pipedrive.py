from .context import pipedrive
from .context import secret

import logging
import unittest


class PipedriveTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.pd = pipedrive.PipedriveClient(secret.PD_API_TOKEN)

    def test_load_person(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEqual(person.name, "Marco Antonio")
        self.assertEqual(person.email, "emeamarco@gmail.com")

    def test_load_person_get_custom_field(self):  # i.e. hash field
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(getattr(person, "88ec7b3fd70f2fbdabe9aded639e316ff29174ce"), 0)  # Lead score

    def test_load_person_get_custom_field_nice_name(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.lead_score, 0)

    def test_load_person_get_undefined_field(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        with self.assertRaises(AttributeError):
            person.fake_field

    def test_load_person_get_enum(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertEqual(person.lead_status, "Recycled")

    def test_load_person_undefined(self):
        person = pipedrive.Person(self.pd, -1)
        self.assertIsNotNone(person)
        self.assertIsNone(person.id)

    def test_load_person_undefined_2(self):
        person = pipedrive.Person(self.pd, "")
        self.assertIsNotNone(person)
        self.assertIsNone(person.id)

    def test_empty_person_get_field(self):
        person = pipedrive.Person(self.pd)
        self.assertIsNotNone(person)
        self.assertIsNone(person.id)
        self.assertIsNone(person.name)

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

    def test_save_person_custom_field(self):
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

    def test_save_person_no_name(self):
        person = pipedrive.Person(self.pd)
        person.name = ""
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, "Unknown Unknown")
        # Delete created person
        self.pd.delete_resource("person", person.id)

    def test_save_person_enum(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 6"
        person.lead_status = "Recycled"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.lead_status, "Recycled")
        # Delete created person
        self.pd.delete_resource("person", person.id)

    def test_save_person_undefined_enum(self):
        person = pipedrive.Person(self.pd)
        person.name = "Test Person 7"
        person.lead_status = "Fake status"
        person.owner_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(person.id)
        person.save()
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.id)
        self.assertEquals(person.name, "Test Person 7")
        self.assertEquals(person.lead_status, None)
        # Delete created person
        self.pd.delete_resource("person", person.id)

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

    def test_load_person_related_owner(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.owner)
        self.assertIsNotNone(person.owner.id)

    def test_load_organization_with_name(self):
        organization = pipedrive.Organization(self.pd, "Test company", "name")
        self.assertIsNotNone(organization)
        self.assertIsNotNone(organization.id)
        self.assertEqual(organization.name, "Test company")
        self.assertEqual(organization.number_of_employees, 10)

    def test_load_organization_with_name_non_unique_result(self):
        organization = pipedrive.Organization(self.pd, "MyCompany", "name")
        self.assertIsNotNone(organization)
        self.assertIsNone(organization.id)

    def test_load_organization_with_email_domain(self):
        organization = pipedrive.Organization(self.pd, "test-company.com", "email_domain")
        self.assertIsNotNone(organization)
        self.assertIsNotNone(organization.id)
        self.assertEqual(organization.name, "Test company")

    def test_load_organization_undefined_with_name(self):
        organization = pipedrive.Organization(self.pd, "MyCompany2", "name")
        self.assertIsNotNone(organization)
        self.assertIsNone(organization.id)

    def test_load_person_related_organization(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        self.assertIsNotNone(person.organization)
        self.assertEqual(person.organization.name, "MyCompany")

    def test_save_person_related_updated_organization(self):
        person = pipedrive.Person(self.pd, 63080)
        self.assertIsNotNone(person)
        # Load organization
        self.assertIsNotNone(person.organization)
        self.assertEqual(person.organization.name, "MyCompany")
        person.organization.name = "MyCompany2"
        # Try to save
        person.save()
        self.assertEqual(person.organization.name, "MyCompany")  # Related resources are read-only so no update

    def test_load_deal(self):
        deal = pipedrive.Deal(self.pd, 1653)
        self.assertIsNotNone(deal)
        self.assertIsNotNone(deal.id)
        self.assertEqual(deal.title, "MyCompany deal test")
        self.assertIsNotNone(deal.contact_person)
        self.assertEqual(deal.contact_person.name, "Marco Antonio")

    def test_save_deal(self):
        deal = pipedrive.Deal(self.pd)
        deal.title = "Test deal 1"
        deal.person_id = 63080
        deal.user_id = 1628545  # my (Helene Jonin) owner id
        self.assertIsNone(deal.id)
        deal.save()
        self.assertIsNotNone(deal)
        self.assertIsNotNone(deal.id)
        self.assertEquals(deal.title, "Test deal 1")
        # Delete created person
        self.pd.delete_resource("deal", deal.id)

    def test_create_and_use_filter(self):
        filter_data = self.pd.get_organization_email_domain_filter("test-company.com")
        self.assertTrue(filter_data)  # Assert not empty
        self.assertEquals(filter_data["name"], "Real Time API filter")
        filtered_data_array = self.pd.get_resource_data("organization", None, {"filter_id": filter_data["id"]})
        self.assertEquals(len(filtered_data_array), 1)
        self.assertEquals(filtered_data_array[0]["name"], 'Test company')


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("pipedrive").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(PipedriveTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
