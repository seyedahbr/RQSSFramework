import csv
import unittest

from RQSSFramework.Completeness.SchemaBasedRefPropertiesCompletenessChecking import *
from RQSSFramework.EntitySchemaExtractor import *


class TestSchemaBasedRefPropertiesCompletenessChecking(unittest.TestCase):

    def setUp(self):
        self.data = [
            FactRef('s1', 'P31', 'P407'),
            FactRef('s1', 'P31', 'P428'),
            FactRef('s1', 'P31', 'P497'),
            FactRef('s1', 'P31', 'P557'),
            FactRef('s2', 'P31', 'P604'),
            FactRef('s2', 'P31', 'P665'),
            FactRef('s3', 'P31'),
            FactRef('s4', 'P31', 'P407'),
            FactRef('s5', 'P279', 'P428'),
            FactRef('s5', 'P279', 'P604'),
            FactRef('s6', 'P279', 'P716'),
            FactRef('s7', 'P279', 'P797'),
            FactRef('s8', 'P279'),
            FactRef('s8', 'P279'),
            FactRef('s8', 'P279'),
            FactRef('s8', 'P279'),
            FactRef('s9', 'P279'),
            FactRef('s10', 'P279'),
            FactRef('s11', 'P279'),
            FactRef('s12', 'P279'),
            FactRef('s13', 'P279'),
            FactRef('s14', 'P458', 'P428'),
            FactRef('s14', 'P458', 'P604'),
            FactRef('s14', 'P458', 'P716'),
            FactRef('s15', 'P458'),
            FactRef('s16', 'P458'),
            FactRef('s17', 'P458'),
            FactRef('s18', 'P458'),
            FactRef('s19', 'P458'),
            FactRef('s20', 'P27', 'P407'),
            FactRef('s21', 'P27', 'P1025'),
            FactRef('s22', 'P27', 'P1047'),
            FactRef('s22', 'P27', 'P1146'),
            FactRef('s23', 'P27'),
            FactRef('s24', 'P27'),
            FactRef('s25', 'P27'),
            FactRef('s26', 'P27'),
            FactRef('s27', 'P27'),
            FactRef('s28', 'P27'),
            FactRef('s29', 'P27'),
            FactRef('s30', 'P39', 'P716'),
            FactRef('s30', 'P39', 'P716'),
            FactRef('s30', 'P39', 'P716'),
            FactRef('s30', 'P39', 'P716'),
            FactRef('s31', 'P39', 'P604'),
            FactRef('s31', 'P39', 'P716'),
            FactRef('s32', 'P125', 'P797'),
            FactRef('s34', 'P136', 'P797'),
            FactRef('s35', 'P136', 'P1025'),
            FactRef('s36', 'P31', 'P797'),
            FactRef('s36', 'P31', 'P248'),
            FactRef('s37', 'P279', 'P248'),
            FactRef('s38', 'P31', 'P248'),
            FactRef('s39', 'P1000'), ]  # not real data, only for test
        self.wikidata_schema_info = [
            EidRefSummary('E1', ['Q35715216'], ['P31'], [
                RefedFactRef('P2860', ['P604', 'P428']),
                RefedFactRef('P458', ['P604', 'P428']),
                RefedFactRef('P279', ['P604', 'P716']),
                RefedFactRef('P93', [])]),
            EidRefSummary('E2', ['Q4713960'], [], [
                RefedFactRef('P1412', []),
                RefedFactRef('P39', ['P716']),
                RefedFactRef('P27', ['P1025', 'P1146']),
                RefedFactRef('P125', []),
                RefedFactRef(
                    'P31', ['P407', 'P428', 'P497', 'P557', 'P604', 'P665']),
                RefedFactRef('P325', ['P604'])]),
            EidRefSummary('E3', ['Q9855587'], ['P279'], [
                RefedFactRef('P1412', []),
                RefedFactRef('P102', []),
                RefedFactRef('P98', []),
                RefedFactRef('P99', []),
                RefedFactRef('P31', ['P428']),
                RefedFactRef('P325', ['P604'])])]  # not real data, only for test

    def test_check_schema_based_property_completeness_Wikidata(self):
        test_class = SchemaBasedRefPropertiesCompletenessChecker(self.data)
        self.assertEqual(test_class.results, None)
        ret = test_class.check_schema_based_property_completeness_Wikidata(
            self.wikidata_schema_info)
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        self.assertGreaterEqual(test_class.score_including_not_refed, 0)
        self.assertLessEqual(test_class.score_including_not_refed, 1)
        with open('schema_based_property_completeness_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('schema_based_property_completeness.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
