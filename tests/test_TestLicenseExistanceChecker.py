import csv
import unittest
from unittest import result

from rdflib import URIRef
from RQSSFramework.Licensing.LicenseExistanceChecking import LicenseChecker


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
        test_class = LicenseChecker(self.test_data)
        self.assertEqual(test_class.results, None)

    def test_remove_duplication(self):
        """
        Test that the constructor will remove the duplicated URIs
        """
        test_class = LicenseChecker(self.test_data)
        result = test_class.check_license_existance()
        self.assertEqual(len(result), 6)
        self.assertEqual(len(test_class.results), 6)

    def test_check_licensing(self):
        """
        Test that it results are according to the real world data for a few
        set of URIs 
        """
        test_class = LicenseChecker(self.test_data)
        result = test_class.check_license_existance()
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('licensing_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('licensing.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
