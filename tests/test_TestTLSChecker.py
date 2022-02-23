import csv
import unittest
from unittest import result

from rdflib import URIRef
from RQSSFramework.Security.TLSExistanceChecking import TLSChecker


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
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('security_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('security.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
