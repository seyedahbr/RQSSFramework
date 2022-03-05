import csv
import datetime
import unittest

from RQSSFramework.Completeness.ClassesPropertiesSchemaCompletenessChecking import *


class TestClassesPropertiesSchemaCompletenessChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'Q35715216': ['P698', 'P2860', 'P2093', 'P1433', 'P356', 'P31'],
        'Q4713960': ['P1412', 'P102', 'P8172', 'P39', 'P31', 'P569'],
        'Q36985': ['P31', 'P234', 'P987', 'P12']} # not real data, only for test
        self.wikidata_schema_info = {'Q35715216': ['P698', 'P2860', 'P91', 'P92', 'P93', 'P31'],
        'Q4713960': ['P1412', 'P102', 'P98', 'P99', 'P31', 'P325'],
        'Q9855587': ['P1412', 'P102', 'P98', 'P99', 'P31', 'P325']} # not real data, only for test

    def test_ref_schema_existance_for_properties_Wikidata(self):
        test_class = ClassesPropertiesSchemaCompletenessChecker(self.data)
        self.assertEqual(test_class.results, None)
        ret = test_class.check_ref_schema_existance_for_properties_Wikidata(self.wikidata_schema_info)
        self.assertEqual(len(ret[0]), len(self.data.keys()))
        self.assertGreaterEqual(test_class.class_schema_completeness_score, 0)
        self.assertLessEqual(test_class.class_schema_completeness_score, 1)
        self.assertGreaterEqual(test_class.property_schema_completeness_score, 0)
        self.assertLessEqual(test_class.property_schema_completeness_score, 1)
        self.assertEqual
        with open('classes_properties_schema_completeness_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('classes_properties_schema_completeness.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
