import unittest
from RQSSFramework.Accuracy.LiteralSyntaxChecking import WikibaseRefLiteralSyntaxChecker

class TestLiteralSyntaxChecking(unittest.TestCase):

    def setUp(self):
        self.data = {'P854':['http://www.example.com'],'P813':['18 Jan 2022']}

    def test_get_property_regex_from_Wikidata(self):
        ret = WikibaseRefLiteralSyntaxChecker(self.data).get_property_regex_from_Wikidata()
        self.assertEqual(ret.keys(), self.data.keys())
    
    def test_check_literals_regex(self):
        ret = WikibaseRefLiteralSyntaxChecker(self.data)
        ret.check_literals_regex()
        ret.print_results()


        

