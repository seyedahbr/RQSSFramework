import csv
import unittest

from RQSSFramework.Consistency.RefPropertiesConsistencyChecking import \
    RefPropertiesConsistencyChecker


class TestPropertyConsistencyChecking(unittest.TestCase):

    def setUp(self):
        self.data = ['P854', 'P813', 'P31', 'P248']

    def test_check_reference_specificity_from_Wikdiata(self):
        test_class = RefPropertiesConsistencyChecker(self.data)
        result = test_class.check_reference_specificity_from_Wikdiata()
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('ref_consistency_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('ref_consistency.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
