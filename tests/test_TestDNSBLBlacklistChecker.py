import csv
import unittest
from re import S
from unittest import result

from rdflib import URIRef
from RQSSFramework.Reputation.DNSBLBlacklistedChecking import \
    DNSBLBlacklistedChecker


class TestLicensing(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("https://en.wikipedia.org/wiki/Albert_Einstein"),
                          URIRef("https://en.wikipedia.org/wiki/Ernest_Rutherford"),
                          URIRef("http://www.patient.co.uk/patientplus/h.htm"),
                          URIRef("http://www.jstor.org/stable/795378"),
                          URIRef(
                              "https://www.einstein-website.de/z_information/verschiedenes.html"),
                          URIRef(
                              "https://data.bnf.fr/en/11901607/albert_einstein/"),
                          URIRef("https://www.uniprot.org/uniprot/P38398")]

    def test_not_computed(self):
        """
        Test the type of a non computed class be NoneType
        """
        test_class = DNSBLBlacklistedChecker(self.test_data)
        self.assertEqual(test_class.results, None)

    def test_remove_duplication(self):
        """
        Test that the constructor will remove the duplicated URIs
        """
        test_class = DNSBLBlacklistedChecker(self.test_data)
        result = test_class.check_domain_blacklisted()
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('dnsbl_reputation_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('dnsbl_reputation.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
