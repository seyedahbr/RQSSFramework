from typing import List, NamedTuple

import ShExes
from pyshex.shex_evaluator import ShExEvaluator
from pyshex.user_agent import SlurpyGraphWithAgent
from rdflib import URIRef


class SyntxResult(NamedTuple):
    total: int
    fails: int
    def __repr__(self):
        return "Number of checked items: {0}; fails:{1}; score: {2}".format(self.total, self.fails, self.score)
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
    
    def check_shex_over_endpoint(self) -> SyntxResult:
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
    
    @property
    def score(self):
        if self.result != None:
            return self.result.score
        return None

    def __repr__(self):
        if self.result == None:
            return 'Results are not computed'
        return """num of ref nodes, num of fails, score
{0},{1},{2}""".format(self.result.total, self.result.fails, self.score)
    
    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print(self.result)