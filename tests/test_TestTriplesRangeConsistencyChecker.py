import unittest
from RQSSFramework.Consistency.TriplesRangeConsistencyChecking import TriplesRangeConsistencyChecker

class TestTripleRangeConsistencyChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'P854':['Q1','Q2'],'P813':['Q3'],'P248':['Q4','Q5','Q6']}

    def test_get_property_regex_from_Wikidata(self):
        ret = TriplesRangeConsistencyChecker(self.data).get_property_ranges_from_Wikidata()
        self.assertEqual(ret.keys(), self.data.keys())
    
    def test_check_literals_regex(self):
        ret = TriplesRangeConsistencyChecker(self.data)
        ret.check_all_value_ranges()
        ret.print_results()


        

