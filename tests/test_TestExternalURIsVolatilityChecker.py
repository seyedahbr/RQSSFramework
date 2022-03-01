import csv
import unittest
from unittest import result

from rdflib import URIRef
from RQSSFramework.Volatility.ExternalURIsVolatilityChecking import *


class TestExternalURIsFreshness(unittest.TestCase):

    def setUp(self):
        #self.test_data = [URIRef('https://understandingdata.com/')]
        self.test_data = [URIRef("https://web.archive.org/web/20130910154049/www.navsource.org/archives/09/08/0801.htm"),
                          URIRef(
                              "https://www.vesseltracking.net/ship/mexico-star-9138800"),
                          URIRef("https://uboat.net/boats/u558.htm"),
                          URIRef("https://uboat.net/boats/u136.htm"),
                          URIRef(
                              "https://www.carnival.com/cruise-ships/carnival-dream.aspx"),
                          URIRef('https://understandingdata.com/')]

    def test_check_external_uris_freshness(self):
        test_class = ExternalURIsVolatilityChecker(self.test_data)
        self.assertEqual(test_class.results, None)
        test_ret = test_class.check_external_uris_volatility()
        self.assertEqual(len(test_ret), len(self.test_data))
        self.assertEqual(len(test_class.results), len(self.test_data))
        if test_class.score != '<None>':
            self.assertGreaterEqual(test_class.score, 0)
        if test_class.score != '<None>':
            self.assertLessEqual(test_class.score, 1)
        with open('external_uris_volatility_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('external_uris_volatility.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = ['<None>' if result._asdict()[field] == None else result._asdict()[
                    field] for field in result._fields]
                w.writerow(row)
