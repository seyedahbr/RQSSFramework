import unittest
from unittest import result
from rdflib import URIRef
from src.RQSSFramework.Availability.DereferencePossibility import DerefrenceExplorer

class TestDereferency(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("https://www.wikidata.org/wiki/Q1"),\
            URIRef("https://www.wikidata.org/wiki/Q1"),\
            URIRef("https://www.wikidata.org/wiki/Qabc"),\
            URIRef("https://www2.macs.hw.ac.uk/~sh200/")] # dereference of redirects

    def test_not_computed(self):
        """
        Test the type of a non computed class be NoneType
        """
        test_class = DerefrenceExplorer(self.test_data)
        self.assertEqual(test_class.results,None)
    
    def test_remove_duplication(self):
        """
        Test that the constructor will remove the duplicated URIs
        """
        test_class = DerefrenceExplorer(self.test_data)
        result = test_class.check_dereferencies()
        self.assertEqual(len(result),3)
        self.assertEqual(len(test_class.results),3)

    def test_check_dereferencies(self):
        """
        Test that it results are according to the real world data for a few
        set of URIs 
        """
        test_class = DerefrenceExplorer(self.test_data)
        result = test_class.check_dereferencies()
        self.assertTrue(result[0].deref)
        self.assertTrue(test_class.results[0].deref)
        self.assertFalse(result[1].deref)
        self.assertFalse(test_class.results[1].deref)
        self.assertTrue(result[2].deref)
        self.assertTrue(test_class.results[2].deref)