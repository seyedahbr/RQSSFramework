from re import S
import unittest
from unittest import result
from rdflib import URIRef
from RQSSFramework.Reputation.DNSBLBlacklistedChecking import DNSBLBlacklistedChecker

class TestLicensing(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("https://en.wikipedia.org/wiki/Albert_Einstein"),
         URIRef("https://en.wikipedia.org/wiki/Ernest_Rutherford"),
         URIRef("http://www.patient.co.uk/patientplus/h.htm"),
         URIRef("http://www.jstor.org/stable/795378"),
         URIRef("https://www.einstein-website.de/z_information/verschiedenes.html"),
         URIRef("https://data.bnf.fr/en/11901607/albert_einstein/"),
         URIRef("https://www.uniprot.org/uniprot/P38398")]

    def test_not_computed(self):
        """
        Test the type of a non computed class be NoneType
        """
        test_class = DNSBLBlacklistedChecker(self.test_data)
        self.assertEqual(test_class.results,None)
    
    def test_remove_duplication(self):
        """
        Test that the constructor will remove the duplicated URIs
        """
        test_class = DNSBLBlacklistedChecker(self.test_data)
        result = test_class.check_domain_blacklisted()
        self.assertEqual(len(result),6)
        self.assertEqual(len(test_class.results),6)
        test_class.print_results()
