import csv
import datetime
import unittest

from RQSSFramework.Believability.HumanReferenceInItemChecking import *


class TestHumanReferenceInItemChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'Q4822345': ['P279', 'P1402', 'P1343', 'P1403', 'P2581', 'P3720'], 'Q2': [
            'P910', 'P571', 'P610', 'P1589', 'P1082', 'P2067']}
        self.till = datetime.datetime.strptime('06:41, 15 December 2017', '%H:%M, %d %B %Y')

    def test_check_referenced_facts_human_added(self):
        test_class = HumanReferenceInItemChecker(self.data,self.till)
        self.assertEqual(test_class.results, None)
        ret = test_class.check_referenced_facts_human_added()
        self.assertEqual(len(ret), len(self.data.keys()))
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('human_added_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('human_added.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in ret[0]._fields])
            for result in ret:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
