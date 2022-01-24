from re import S
from typing import List, NamedTuple, Dict

class TripleSemanticResult(NamedTuple):
    property: str
    total: int
    matches: int
    def __repr__(self):
        return "Number of checked values for propety {0}: {1}; exact matches:{2}; score:{3}".format(self.property, self.total, self.matches, self.score)
    @property
    def score(self):
        return (self.matches/self.total)

class RefPropValue(NamedTuple):
    ref_property: str
    ref_value: str

class RefTripleSemanticChecker:
    results: List[TripleSemanticResult] = None
    _gold_standard: Dict
    _statement_ref_value: Dict
    
    def __init__(self,gold_standard: Dict, statement_ref_value: Dict):
        self._gold_standard = gold_standard
        self._statement_ref_value = statement_ref_value
    
    def check_semantic_to_gold_standard(self) -> List[TripleSemanticResult]:
        self.results = []
        for prop in self._statement_ref_value.keys():
            num_matches = 0
            num_fails = 0
            



    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        for result in self.results:
            print(self.result)