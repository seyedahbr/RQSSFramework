import unittest
from RQSSFramework.Consistency.RefPropertiesConsistencyChecking import RefPropertiesConsistencyChecker

class TestPropertyConsistencyChecking(unittest.TestCase):

    def setUp(self):
        self.data = ['P854','P813','P31']

    def test_check_reference_specificity_from_Wikdiata(self):
        ret = RefPropertiesConsistencyChecker(self.data)
        result=ret.check_reference_specificity_from_Wikdiata()
        self.assertEqual(result[0].is_ref_specific, True)
        self.assertEqual(result[1].is_ref_specific, True)
        self.assertEqual(result[2].is_ref_specific, False)



        

