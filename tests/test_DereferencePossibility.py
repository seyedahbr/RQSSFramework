import unittest
from rdflib import URIRef
from src.RQSSFramework.Availability.DereferencePossibility import check_dereferencies

class TestDereferency(unittest.TestCase):
    def test_check_dereferencies(self):
        """
        Test that it results are according to the real world data for a few
        set of URIs 
        """
        data1 = {URIRef("https://www.wikidata.org/wiki/Q1")}
        data2 = {URIRef("https://www.wikidata.org/wiki/Qabc")}
        data3 = {URIRef("https://www.wikidata.org/wiki/Q25")}
        result = check_dereferencies(data1)
        self.assertTrue(result[0].deref)
        result = check_dereferencies(data2)
        self.assertFalse(result[0].deref)
        result = check_dereferencies(data3)
        self.assertTrue(result[0].deref)