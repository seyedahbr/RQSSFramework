import csv
import unittest

from RQSSFramework.Versatility.MultilingualSourcesAndFactsChecking import *


class TestMultilingualSourcesAndFactsChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'Q227151-D42140B1-2731-4AD7-A305-DB4ECDC8E5D0': ['http://www.example.com', 'http://www.github.com', 'https://fr.wikipedia.org/wiki/Commerce_triangulaire'],
                     'q1473121-39CF4752-51BF-45DE-B0CC-01B172119819': ['Q48183', 'Q328', 'https://www.bbc.com/arabic']}

    def test_check_multilingualism(self):
        test_class = MultilingualFactsAndSourcesChecker(self.data)
        result = test_class.check_fact_sources_multilingualism()
        self.assertGreaterEqual(test_class.multilingual_sources_score, 0)
        self.assertLessEqual(test_class.multilingual_sources_score, 1)
        self.assertGreaterEqual(test_class.multilingual_referenced_facts_score, 0)
        self.assertLessEqual(test_class.multilingual_referenced_facts_score, 1)
        with open('sources_facts_multilingualism_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('sources_multilingualism.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow(
                [field for field in test_class.results_sources[0]._fields])
            for result in test_class.results_sources:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
        with open('facts_multilingualism.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow(
                [field for field in test_class.results_Facts[0]._fields])
            for result in test_class.results_Facts:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
