from typing import Dict, List, Iterator
from SPARQLWrapper import JSON, SPARQLWrapper

from RQSSFramework.Accuracy.TripleSyntaxChecking import SyntxResult
from RQSSFramework.Queries import RQSS_QUERIES

class WikibaseRefLiteralSyntaxChecker:
    result: List[SyntxResult] = None
    _properties_values: Dict
    _regexes: Dict

    def __init__(self, prop_vals: Dict):
        self._properties_values = prop_vals
        self._regexes = self.get_property_regex(prop_vals.keys())
    
    def check_literals_regex(self) -> List[SyntxResult]:
        num_total = 0
        

    def get_property_regex(properties: Iterator) -> Dict:
        ret_val = Dict.fromkeys(properties)
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        for prop in properties:
            ret_val[str(prop)]=list()
            sparql.setQuery(RQSS_QUERIES['get_property_constraints_regex'].format(prop))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value=result["to_ret"]["value"]
                ret_val[str(prop)].append(value)
        return ret_val
    
    def write_to_CSV(self):
        if self.result == None:
            print('Results are not computed')
            return
        
    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print(self.result)