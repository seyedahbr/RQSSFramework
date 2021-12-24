from re import S
from typing import Iterator, List, NamedTuple
from pyshex.shex_evaluator import ShExEvaluator
from pyshex.user_agent import SlurpyGraphWithAgent
from pyshex.utils.sparql_query import SPARQLQuery
from rdflib import URIRef
from rdflib.term import Statement

import ShExes, Queries

class SyntxResult(NamedTuple):
    total: int
    fails: int
    def __repr__(self):
        return "Number of checked items: {0:10} fails:{1:10} score{2}".format(self.total, self.fails, self.score)
    @property
    def score(self):
        return 1-(self.fails/self.total)

class WikibaseRefTripleSyntaxChecker:
    statements = []
    result:SyntxResult = None
    endpoint: str = None
    file: str = None 

    def __init__(self, statements: List[URIRef], endpoint: str = None, file: str = None):
        self.statements = statements
        self.endpoint = endpoint
        self.file = file
    
    def check_shex_over_endpoint(self) -> int:
        num_total = 0
        num_fails = 0
        for statement_node in self.statements:
            num_total += 1
            try:
                result=ShExEvaluator(SlurpyGraphWithAgent(self.endpoint),
                ShExes.SHEX_SCHEMAS['wikibase_reference_reification'],
                statement_node).evaluate()
                if not result[0].result: num_fails += 1
            except Exception as e:
                num_fails += 1
                print(e)
                continue
        self.result = SyntxResult(num_total, num_fails)
        return self.result
    
    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print(self.result)