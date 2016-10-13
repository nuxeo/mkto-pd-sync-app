import unittest
from .context import marketo
from .context import secret
import logging


class MarketoTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.mkto = marketo.MarketoClient(secret.IDENTITY_ENDPOINT, secret.CLIENT_ID, secret.CLIENT_SECRET, secret.API_ENDPOINT)

    def test_get_lead_from_client(self):
        lead = self.mkto.get_resource_by_id("lead", 7591021)
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEqual(lead.firstName, "Marco")
        self.assertEqual(lead.lastName, "Antonio")
        self.assertEqual(lead.email, "emeamarco@gmail.com")

    def test_load_lead(self):
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
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

    def test_add_lead_from_client(self):
        lead = marketo.Lead(self.mkto)
        lead.firstName = "Test"
        lead.lastName = "Lead"
        lead.email = "lead@test.com"
        self.assertIsNone(lead.id)
        lead = self.mkto.add_resource("lead", lead.resource_data)
        self.assertIsNotNone(lead)
        self.assertIsNotNone(lead.id)
        self.assertEquals(lead.firstName, "Test")
        self.assertEquals(lead.lastName, "Lead")
        self.assertEquals(lead.email, "lead@test.com")
        # Delete created person
        self.mkto.delete_resource("lead", lead.id)

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
        # Delete created person
        self.mkto.delete_resource("lead", lead.id)

    def test_get_lead_undefined(self):
        lead = marketo.Lead(self.mkto, -1)
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)

    def test_update_lead(self):
        # Get person first
        lead = marketo.Lead(self.mkto, 7591021)
        self.assertIsNotNone(lead)
        self.assertEqual(lead.firstName, "Marco")
        # Then update
        # NB: For the update to work, field should not block updates from WS API
        # Go to Admin -> Field Management -> search for the field
        # Field Actions ->  Block Field Updates -> disable Web service API
        lead.firstName = "Test 3"
        lead.save()
        self.assertEquals(lead.firstName, "Test 3")
        # Reset updated value
        lead.firstName = "Marco"
        lead.save()


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("marketo").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(MarketoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
