import csv
import unittest

from RQSSFramework.Consistency.TriplesRangeConsistencyChecking import \
    TriplesRangeConsistencyChecker


class TestTripleRangeConsistencyChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'P854': ['Q1', 'Q2', 'Q1', 'Q2', 'Q3', 'Q2'], 'P813': [
            'Q3', 'Q1','Q3', 'Q1','Q3', 'Q1'], 'P248': ['Q4', 'Q5', 'Q6']}

    def test_get_property_regex_from_Wikidata(self):
        ret = TriplesRangeConsistencyChecker(
            self.data).get_property_ranges_from_Wikidata()
        self.assertEqual(ret.keys(), self.data.keys())
    
    def test_get_instances_subclass_of_values_from_Wikidata(self):
        ret = TriplesRangeConsistencyChecker(
            self.data).get_property_ranges_from_Wikidata()
        self.assertEqual(ret.keys(), self.data.keys())

    def test_check_literals_regex(self):
        test_class = TriplesRangeConsistencyChecker(self.data)
        result = test_class.check_all_value_ranges()
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('range_consistency_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('range_consistency.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
