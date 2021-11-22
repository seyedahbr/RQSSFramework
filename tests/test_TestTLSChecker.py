import unittest
from unittest import result
from rdflib import URIRef
from src.RQSSFramework.Security.TLSExistanceChecking import TLSChecker

class TestTLSChecking(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("http://go.com/"),
         URIRef("http://go.com/"),
         URIRef("http://www.washington.edu/"),
         URIRef("http://people.com.cn/"),
         URIRef("https://www.uniprot.org/uniprot/P38398")]

    def test_not_computed(self):
        """
        Test the type of a non computed class be NoneType
        """
        test_class = TLSChecker(self.test_data)
        self.assertEqual(test_class.results,None)
    
    def test_remove_duplication(self):
        """
        Test that the constructor will remove the duplicated URIs
        """
        test_class = TLSChecker(self.test_data)
        result = test_class.check_support_tls()
        self.assertEqual(len(result),4)
        self.assertEqual(len(test_class.results),4)

    def test_check_tls(self):
        """
        Test that it results are according to the real world data for a few
        set of URIs 
        """
        test_class = TLSChecker(self.test_data)
        result = test_class.check_support_tls()
        self.assertFalse(result[0].support)
        self.assertFalse(test_class.results[0].support)
        self.assertTrue(result[1].support)
        self.assertTrue(test_class.results[1].support)
        self.assertFalse(result[2].support)
        self.assertFalse(test_class.results[2].support)
        self.assertTrue(result[3].support)
        self.assertTrue(test_class.results[3].support)