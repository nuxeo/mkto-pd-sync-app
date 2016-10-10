import unittest
from .context import marketo
from .context import secret
import logging


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

    def test_dump_lead_from_client(self):
        lead = marketo.Lead(self.mkto)
        lead.firstName = "Test"
        lead.lastName = "Lead"
        lead.email = "lead@test.com"
        self.assertIsNone(lead.id)
        lead = self.mkto.add_resource("lead", lead.resource_data)
        self.assertIsNotNone(lead.id)
        self.assertEquals(lead.firstName, "Test")
        self.assertEquals(lead.lastName, "Lead")
        self.assertEquals(lead.email, "lead@test.com")
        # TODO: delete at tear down

    def test_add_lead(self):
        lead = marketo.Lead(self.mkto)
        lead.firstName = "Test"
        lead.lastName = "Lead 2"
        lead.email = "lead@test2.com"
        self.assertIsNone(lead.id)
        lead.save()
        self.assertIsNotNone(lead.id)
        self.assertEquals(lead.firstName, "Test")
        self.assertEquals(lead.lastName, "Lead 2")
        self.assertEquals(lead.email, "lead@test2.com")
        # TODO: delete at tear down

    def test_get_lead_undefined(self):
        lead = marketo.Lead(self.mkto, -1)
        self.assertIsNotNone(lead)
        self.assertIsNone(lead.id)

    # Update call does not seem to work for now - sent an E-mail to support
    # def test_update_lead(self):
    #     # Create a lead first
    #     lead = marketo.Lead(self.mkto)
    #     lead.firstName = "Test"
    #     lead.lastName = "Lead 3"
    #     lead.email = "lead@test3.com"
    #     self.assertIsNone(lead.id)
    #     lead.save()
    #     self.assertIsNotNone(lead.id)
    #     lead_id = lead.id  # Save id for later
    #     self.assertEquals(lead.firstName, "Test")
    #     # Then update
    #     lead.firstName = "Test 2"
    #     lead.save()
    #     lead = marketo.Lead(self.mkto, lead_id)
    #     self.assertEquals(lead.firstName, "Test 2")
    #     # TODO: delete at tear down


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger("marketo").setLevel(logging.DEBUG)
    suite = unittest.TestLoader().loadTestsFromTestCase(MarketoTestCase)
    unittest.TextTestRunner(verbosity=2).run(suite)
