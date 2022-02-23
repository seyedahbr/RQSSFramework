import csv
import unittest
from unittest import result

from rdflib import URIRef
from RQSSFramework.Availability.DereferencePossibility import \
    DerefrenceExplorer


class TestDereferency(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("https://www.wikidata.org/wiki/Q1"),
                          URIRef("https://www.wikidata.org/wiki/Q1"),
                          URIRef("https://www.wikidata.org/wiki/Qabc"),
                          URIRef("https://www2.macs.hw.ac.uk/~sh200/")]  # dereference of redirects

    def test_not_computed(self):
        """
        Test the type of a non computed class be NoneType
        """
        test_class = DerefrenceExplorer(self.test_data)
        self.assertEqual(test_class.results, None)
        self.assertEqual(test_class.score, None)

    def test_remove_duplication(self):
        """
        Test that the constructor will remove the duplicated URIs
        """
        test_class = DerefrenceExplorer(self.test_data)
        result = test_class.check_dereferencies()
        self.assertEqual(len(result), 3)
        self.assertEqual(len(test_class.results), 3)

    def test_check_dereferencies(self):
        """
        Test that it results are according to the real world data for a few
        set of URIs 
        """
        test_class = DerefrenceExplorer(self.test_data)
        test_ret = test_class.check_dereferencies()
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('dereferencing_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('dereferencing.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
