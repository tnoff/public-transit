from datetime import datetime
import httpretty
import unittest

from transit import client
from transit.exceptions import TransitException
from transit.common.urls import bart

from tests.data.bart import bsa

class TestClient(unittest.TestCase):

    @httpretty.activate
    def test_bsa(self):
        test_url = bart.service_advisory()
        httpretty.register_uri(httpretty.GET,
                               test_url,
                               body=bsa.text,
                               content_type='application/xml')

        advisories = client.bart.service_advisory()
        self.assertNotEqual(len(advisories[0].descriptions), 0)
        self.assertTrue(isinstance(advisories[0].expires, datetime))
