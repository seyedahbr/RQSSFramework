import csv
import unittest

from RQSSFramework.Completeness.ClassesPropertiesSchemaCompletenessChecking import *
from RQSSFramework.EntitySchemaExtractor import *


class TestClassesPropertiesSchemaCompletenessChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'Q35715216': ['P698', 'P2860', 'P2093', 'P1433', 'P356', 'P31'],
                     'Q4713960': ['P1412', 'P102', 'P8172', 'P791', 'P39', 'P31', 'P569'],
                     'Q36985': ['P31', 'P234', 'P987', 'P12']}  # not real data, only for test
        self.wikidata_schema_info = [EidRefSummary('E1', ['Q35715216'], ['P698'], [RefedFactRef('P2860', []), RefedFactRef('P91', []), RefedFactRef('P92', []), RefedFactRef('P93', []), RefedFactRef('P31', [])]),
                                     EidRefSummary('E2', ['Q4713960'], [], [RefedFactRef('P1412', []), RefedFactRef('P102', []), RefedFactRef(
                                         'P98', []), RefedFactRef('P99', []), RefedFactRef('P31', []), RefedFactRef('P325', [])]),
                                     EidRefSummary('E3', ['Q9855587'], ['P12'], [RefedFactRef('P1412', ['P31']), RefedFactRef('P102', []), RefedFactRef('P98', []), RefedFactRef('P99', []), RefedFactRef('P31', []), RefedFactRef('P325', [])])]  # not real data, only for test

    def test_ref_schema_existance_for_properties_Wikidata(self):
        test_class = ClassesPropertiesSchemaCompletenessChecker(
            self.data, self.wikidata_schema_info)
        self.assertEqual(test_class.results, None)
        ret = test_class.check_ref_schema_existance_for_properties_Wikidata()
        self.assertEqual(len(ret[0]), len(self.data.keys()))
        self.assertGreaterEqual(test_class.class_schema_completeness_score, 0)
        self.assertLessEqual(test_class.class_schema_completeness_score, 1)
        self.assertGreaterEqual(
            test_class.property_schema_completeness_score, 0)
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
