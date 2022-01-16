import unittest
from unittest import result
from rdflib import URIRef
from six import assertCountEqual
from RQSSFramework.Accuracy.LiteralSyntaxChecking import WikibaseRefLiteralSyntaxChecker

class TestLiteralSyntaxChecking(unittest.TestCase):

    def setUp(self):
        self.properties = {'P854','P813'}

    def test_get_property_regex(self):
        ret = WikibaseRefLiteralSyntaxChecker.get_property_regex(self.properties)
        self.assertEqual(ret.keys(), self.properties)
        

