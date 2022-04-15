import csv
import unittest

from RQSSFramework.Completeness.SchemaBasedRefPropertiesCompletenessChecking import *


class TestSchemaBasedRefPropertiesCompletenessChecking(unittest.TestCase):

    def setUp(self):
        self.data = [ClassRefedFactRef('Q35715216', 'P31', ['P407', 'P428', 'P497', 'P557', 'P604', 'P665']),
                     ClassRefedFactRef('Q35715216', 'P279', [
                                       'P428', 'P604', 'P716', 'P797']),
                     ClassRefedFactRef('Q35715216', 'P458', [
                                       'P428', 'P604', 'P716']),
                     ClassRefedFactRef('Q4713960', 'P27', [
                                       'P407', 'P1025', 'P1047', 'P1146']),
                     ClassRefedFactRef('Q4713960', 'P39', ['P716', 'P604']),
                     ClassRefedFactRef('Q4713960', 'P125', ['P797']),
                     ClassRefedFactRef('Q4713960', 'P136', ['P797', 'P1025']),
                     ClassRefedFactRef('Q36985', 'P31', ['P797', 'P248']),
                     ClassRefedFactRef('Q36997', 'P279', ['P248']),
                     ClassRefedFactRef('Q36997', 'P31', ['P248'])]  # not real data, only for test
        self.wikidata_schema_info = [EidRefSummary(
            'E1', ['Q35715216'], ['P31'], [
                RefedFactRef('P2860', ['P604', 'P428']),
                RefedFactRef('P458', ['P604', 'P428']),
                RefedFactRef('P279', ['P604', 'P716']),
                RefedFactRef('P93', [])]),
            EidRefSummary('E2', ['Q4713960'], [], [RefedFactRef('P1412', []), RefedFactRef('P39', ['P716']), RefedFactRef(
                'P27', ['P1025','P1146']), RefedFactRef('P125', []), RefedFactRef('P31', ['P407', 'P428', 'P497', 'P557', 'P604', 'P665']), RefedFactRef('P325', [])]),
            EidRefSummary('E3', ['Q9855587'], ['P279'], [RefedFactRef('P1412', []), RefedFactRef('P102', []), RefedFactRef('P98', []), RefedFactRef('P99', []), RefedFactRef('P31', []), RefedFactRef('P325', [])])]  # not real data, only for test

    def check_schema_based_property_completeness_Wikidata(self):
        test_class = SchemaBasedRefPropertiesCompletenessChecker(self.data)
        self.assertEqual(test_class.results, None)
        ret = test_class.check_schema_based_property_completeness_Wikidata(
            self.wikidata_schema_info)
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
