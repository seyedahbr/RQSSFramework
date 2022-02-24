import csv
import datetime
import unittest

from RQSSFramework.Currency.ReferenceFreshnessChecking import *


class TestReferenceFreshnessChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'Q35715216': ['P698', 'P2860', 'P2093', 'P1433', 'P356', 'P31'], 'Q4713960': [
            'P1412', 'P102', 'P8172', 'P39', 'P31', 'P569']}
        # self.data = {'Q4822345': ['P279', 'P1402', 'P1343', 'P1403', 'P2581', 'P3720'], 'Q2': [
        #     'P910', 'P571', 'P610', 'P1589', 'P1082', 'P2067']}
        self.till = datetime.datetime.strptime('06:41, 15 December 2021', '%H:%M, %d %B %Y')

    def test_check_referenced_facts_freshness(self):
        test_class = ReferenceFreshnessInItemChecker(self.data,self.till)
        self.assertEqual(test_class.results, None)
        ret = test_class.check_referenced_facts_freshness()
        self.assertEqual(len(ret[0]), len(self.data.keys()))
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        self.assertEqual
        with open('fact_freshness_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('fact_freshness.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
