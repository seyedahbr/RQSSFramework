from re import S
from typing import Iterator, List, NamedTuple
from pyshex.shex_evaluator import ShExEvaluator
from pyshex.user_agent import SlurpyGraphWithAgent
from pyshex.utils.sparql_query import SPARQLQuery

import ShExes, Queries

class SyntxResult(NamedTuple):
    total: int
    fails: int
    score: float = 1-(fails/total)

class WikibaseRefTripleSyntaxChecker:
    result:SyntxResult = None
    endpoint: str = None
    file: str = None 

    def __init__(self, endpoint: str = None, file: str = None):
        self.endpoint = endpoint
        self.file = file
    
    def check_shex_over_endpoint(self) -> int:
        num_total = 0
        num_fails = 0
        results=ShExEvaluator(SlurpyGraphWithAgent(self.endpoint),
        ShExes.SHEX_SCHEMAS['wikibase_reference_reification'],
        SPARQLQuery(self.endpoint,Queries.RQSS_QUERIES['get_all_statement_nodes_wikimedia']).focus_nodes()).evaluate()
        num_total = len(results)
        for r in results:
            if not r.result: num_fails += 1
        self.result = SyntxResult(num_total, num_fails)
        return self.result
    
    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print("Number of checked items: {0:10} fails:{1:10} score{2}".format(self.result.total, self.result.fails, self.result.score))