import unittest
from RQSSFramework.Accuracy.TripleSemanticChecking import RefTripleSemanticChecker,RefPropValue,TripleSemanticResult

class TestRefTripleSemanticChecking(unittest.TestCase):

    def setUp(self):
        self.GSdata = {'P21':[RefPropValue('P248','Q36578'),RefPropValue('P248','Q77541206')],
        'P27':[RefPropValue('P3865','Q83900')],
        'P1412':[RefPropValue('P248','Q19938912')]}
        self.data = {'P21':[(),(),()]}

    def test_check_semantic_to_gold_standard(self):
        ret = RefTripleSemanticChecker(self.GSdata, self.data).check_semantic_to_gold_standard()
        self.assertEqual(ret.keys(), self.data.keys())

        

