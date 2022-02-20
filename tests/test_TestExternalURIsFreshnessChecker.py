import unittest
from unittest import result
from rdflib import URIRef
from RQSSFramework.Currency.ExternalURIsFreshnessChecking import *

class TestExternalURIsFreshness(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("web.archive.org/web/20130910154049/www.navsource.org/archives/09/08/0801.htm"),\
            URIRef("www.vesseltracking.net/ship/mexico-star-9138800"),\
            URIRef("uboat.net/boats/u558.htm"),\
            URIRef("uboat.net/boats/u136.htm")]

    def test_check_external_uris_freshness(self):
        test_class = ExternalURIsFreshnessChecker(self.test_data)
        self.assertEqual(test_class.results,None)