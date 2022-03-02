import csv
import unittest
from unittest import result

from rdflib import URIRef
from RQSSFramework.Currency.ExternalURIsFreshnessChecking import *
from RQSSFramework.Timeliness.ExternalURIsTimelinessChecking import *
from RQSSFramework.Volatility.ExternalURIsVolatilityChecking import *


class TestExternalURIsFreshness(unittest.TestCase):

    def setUp(self):
        #self.test_data = [URIRef('https://understandingdata.com/')]
        self.test_data_freshness = [FreshnessOfURI(URIRef('https://web.archive.org/web/20130910154049/www.navsource.org/archives/09/08/0801.htm'),None),
            FreshnessOfURI(URIRef('https://www.vesseltracking.net/ship/mexico-star-9138800'),None),
            FreshnessOfURI(URIRef('https://uboat.net/boats/u558.htm'),1.0),
            FreshnessOfURI(URIRef('https://uboat.net/boats/u136.htm'),0.35), # test data, not real
            FreshnessOfURI(URIRef('https://www.carnival.com/cruise-ships/carnival-dream.aspx'),0.25), # test data, not real
            FreshnessOfURI(URIRef('https://understandingdata.com/'),None)]
        self.test_data_volatility =[VolatilityOfURI(URIRef('https://web.archive.org/web/20130910154049/www.navsource.org/archives/09/08/0801.htm'),None),
            VolatilityOfURI(URIRef('https://www.vesseltracking.net/ship/mexico-star-9138800'),None),
            VolatilityOfURI(URIRef('https://uboat.net/boats/u558.htm'),None),
            VolatilityOfURI(URIRef('https://uboat.net/boats/u136.htm'),0), # test data, not real
            VolatilityOfURI(URIRef('https://www.carnival.com/cruise-ships/carnival-dream.aspx'),1.0),
            VolatilityOfURI(URIRef('https://understandingdata.com/'),0.8)]

    def test_check_external_uris_freshness(self):
        test_class = ExternalURIsTimelinessChecker(self.test_data_freshness,self.test_data_volatility)
        self.assertEqual(test_class.results, None)
        test_ret = test_class.check_external_uris_timeliness()
        self.assertEqual(len(test_ret), len(self.test_data_freshness))
        self.assertEqual(len(test_class.results), len(self.test_data_freshness))
        if test_class.score != '<None>':
            self.assertGreaterEqual(test_class.score, 0)
        if test_class.score != '<None>':
            self.assertLessEqual(test_class.score, 1)
        with open('external_uris_timeliness_ratio.test.csv', 'w') as file_handler:
            file_handler.write(str(test_class))
        with open('external_uris_timeliness.test.csv', 'w', newline='') as f:
            w = csv.writer(f)
            # write header from NamedTuple fields
            w.writerow([field for field in test_class.results[0]._fields])
            for result in test_class.results:
                row = ['<None>' if result._asdict()[field] == None else result._asdict()[
                    field] for field in result._fields]
                w.writerow(row)
