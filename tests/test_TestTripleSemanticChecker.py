import unittest
from RQSSFramework.Accuracy.TripleSemanticChecking import RefTripleSemanticChecker, FactReference, TripleSemanticResult


class TestRefTripleSemanticChecking(unittest.TestCase):

    def setUp(self):
        self.GSdata = [FactReference('Q1', 'P21', 'P248', 'Q36578'), FactReference('Q1', 'P21', 'P248', 'Q77541206'),
                       FactReference('Q1', 'P27', 'P3865', 'Q83900'), FactReference('Q1', 'P1412', 'P248', 'Q19938912')]
        self.data =[
            FactReference('Q1','P21','P248', 'Q77541206'), FactReference('Q1','P21','P248', 'Q36578'), FactReference('Q1','P21','P248', 'Q1'),
            FactReference('Q1','P21','P248', 'Q2'), FactReference('Q1','P21','P248', 'Q3'), FactReference('Q1','P21','P1', 'Q2'), FactReference('Q1','P21','P2', 'Q3'),
            FactReference('Q1','P27','P1', 'Q2'), FactReference('Q1','P27','P2', 'Q3'), FactReference('Q1','P27','P3', 'Q4'),
            FactReference('Q1','P1412','P248', 'Q2'), FactReference('Q1','P1412','P248', 'Q3'), FactReference('Q1','P1412','P248', 'Q4')]

    def test_check_semantic_to_gold_standard(self):
        ret = RefTripleSemanticChecker(self.GSdata, self.data)
        ret.check_semantic_to_gold_standard()
        for result in ret.results:
            # note that in P21 example, there are two similar specified ref triples in the gold standard and 5 exact matches in data 
            # but we count every 5 in data twice (for each gold standard triple)
            # The higer non-exact-match ref values, the lower accuracy we will have
            # The higer specified values in gold standard, the higher impact and expectation of exact we will have
            if result.property == 'P21':
                self.assertEqual(result.half_matches,10)
                self.assertEqual(result.full_matches,2)
                self.assertEqual(result.score,0.2)
            if result.property == 'P27':
                self.assertEqual(result.half_matches,0)
                self.assertEqual(result.full_matches,0)
                self.assertEqual(result.score,1.0)
            if result.property == 'P1412':
                self.assertEqual(result.half_matches,3)
                self.assertEqual(result.full_matches,0)
                self.assertEqual(result.score,0)


        
