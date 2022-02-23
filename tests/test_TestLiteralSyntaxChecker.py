import csv
import unittest

from RQSSFramework.Accuracy.LiteralSyntaxChecking import \
    WikibaseRefLiteralSyntaxChecker


class TestLiteralSyntaxChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'P854': ['http://www.example.com','http://www.github.com','http://hw.ac.uk'],
                     'P813': ['18 Jan 2022', '04 Jun 2019']}

    def test_get_property_regex_from_Wikidata(self):
        ret = WikibaseRefLiteralSyntaxChecker(
            self.data).get_property_regex_from_Wikidata()
        self.assertEqual(ret.keys(), self.data.keys())

    def test_check_literals_regex(self):
        test_class = WikibaseRefLiteralSyntaxChecker(self.data)
        result = test_class.check_literals_regex()
        self.assertGreaterEqual(test_class.score, 0)
        self.assertLessEqual(test_class.score, 1)
        with open('ref_literal_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('ref_literal.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._asdict()[field] for field in result._fields]
                w.writerow(row)
