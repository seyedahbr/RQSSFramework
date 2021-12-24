from typing import Iterator, List, NamedTuple
from pyshex.shex_evaluator import ShExEvaluator
from pyshex.user_agent import SlurpyGraphWithAgent
from pyshex.utils.sparql_query import SPARQLQuery

import ShExes, Queries

class WikibaseRefTripleSyntaxChecker:
    _num_fails: int = None
    endpoint: str = None
    file: str = None 

    def __init__(self, endpoint: str = None, file: str = None):
        self.endpoint = endpoint
        self.file = file
    
    def check_shex_over_endpoint(self) -> int:
        num_fails = 0
        result=ShExEvaluator(SlurpyGraphWithAgent(self.endpoint),
        ShExes.SHEX_SCHEMAS['wikibase_reference_reification'],
        SPARQLQuery(self.endpoint,Queries.RQSS_QUERIES['get_all_statement_nodes_wikimedia']).focus_nodes()).evaluate()
        for r in result:
            print(f"{r.focus}: ", end="")
            if not r.result:
                print(f"FAIL: {r.reason}")
            else:
                print("PASS")
        self._num_fails = num_fails
        return num_fails
    
    def print_results(self):
        """
        print self._num_fains if it is already computed
        """
        if self._num_fails == None:
            print('Results are not computed')
            return
        print("Number of syntax fails:{1}".format(self._num_fails))