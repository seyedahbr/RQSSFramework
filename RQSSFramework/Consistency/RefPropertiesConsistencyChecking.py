import re
from typing import List, NamedTuple
from SPARQLWrapper import JSON, SPARQLWrapper

from Queries import RQSS_QUERIES


class PropConsistencyResult(NamedTuple):
    property: str
    is_ref_specific: str
    def __repr__(self):
        return "Property {0} is reference-specific: {1}".format(self.property, self.is_ref_specific)

class RefPropertiesConsistencyChecker:
    results: List[PropConsistencyResult] = None
    _ref_properties: List[str]

    def __init__(self, ref_properties:List[str]):
        self._ref_properties = ref_properties
    
    def check_reference_specificity_from_Wikdiata(self) -> List[PropConsistencyResult]:
        self.results = []
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
        for prop in self._ref_properties:
            sparql.setQuery(RQSS_QUERIES['get_property_constraints_specificity'].format(prop))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value=result["to_ret"]["value"]
                if value == 'ref':
                    self.results.append(PropConsistencyResult(prop, 'True'))
                elif value == '':
                    self.results.append(PropConsistencyResult(prop, 'NKN'))
                else:
                    self.results.append(PropConsistencyResult(prop, 'False'))
        return self.results

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
