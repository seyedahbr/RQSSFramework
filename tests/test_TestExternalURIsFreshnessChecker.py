import csv
import unittest
from unittest import result

from rdflib import URIRef
from RQSSFramework.Currency.ExternalURIsFreshnessChecking import *


class TestExternalURIsFreshness(unittest.TestCase):

    def setUp(self):
        self.test_data = [URIRef("web.archive.org/web/20130910154049/www.navsource.org/archives/09/08/0801.htm"),\
            URIRef("www.vesseltracking.net/ship/mexico-star-9138800"),\
            URIRef("uboat.net/boats/u558.htm"),\
            URIRef("uboat.net/boats/u136.htm"),\
            URIRef("https://www.carnival.com/cruise-ships/carnival-dream.aspx")]

    def test_check_external_uris_freshness(self):
        test_class = ExternalURIsFreshnessChecker(self.test_data)
        self.assertEqual(test_class.results,None)
        test_ret = test_class.check_external_uris_freshness()
        self.assertEqual(len(test_ret),len(self.test_data))
        self.assertEqual(len(test_class.results),len(self.test_data))
        if test_class.last_modif_score != '<None>': self.assertGreaterEqual(test_class.last_modif_score, 0)
        if test_class.last_modif_score != '<None>': self.assertLessEqual(test_class.last_modif_score, 1)
        with open('external_uris_freshness_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('external_uris_freshness.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._NONE if result._asdict()[field] == None else result._asdict()[field] for field in result._fields]
                w.writerow(row)

    def test_check_external_uris_freshness_with_google_cache(self):
        test_class = ExternalURIsFreshnessChecker(self.test_data,extract_google_cache=True)
        self.assertEqual(test_class.results,None)
        test_ret = test_class.check_external_uris_freshness()
        self.assertEqual(len(test_ret),len(self.test_data))
        self.assertEqual(len(test_class.results),len(self.test_data))
        if test_class.last_modif_score != '<None>': self.assertGreaterEqual(test_class.last_modif_score, 0)
        if test_class.last_modif_score != '<None>': self.assertLessEqual(test_class.last_modif_score, 1)
        if test_class.google_cache_score != '<None>': self.assertGreaterEqual(test_class.google_cache_score, 0)
        if test_class.google_cache_score != '<None>': self.assertLessEqual(test_class.google_cache_score, 1)
        with open('external_uris_freshness_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('external_uris_freshness.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = [result._NONE if result._asdict()[field] == None else result._asdict()[field] for field in result._fields]
                w.writerow(row)