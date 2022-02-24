import sys
from typing import List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class PropConsistencyResult(NamedTuple):
    property: str
    is_ref_specific: bool

    def __repr__(self):
        return "Property {0} is reference-specific: {1}".format(self.property, self.is_ref_specific)


class RefPropertiesConsistencyChecker:
    results: List[PropConsistencyResult] = None
    _ref_properties: List[str]

    def __init__(self, ref_properties: List[str]):
        self._ref_properties = ref_properties

    def check_reference_specificity_from_Wikdiata(self) -> List[PropConsistencyResult]:
        self.results = []
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        for prop in self._ref_properties:
            sparql.setQuery(
                RQSS_QUERIES['get_property_constraints_specificity'].format(prop))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value = result["to_ret"]["value"]
                if value == 'true':
                    self.results.append(PropConsistencyResult(prop, True))
                else:
                    self.results.append(PropConsistencyResult(prop, False))
        return self.results

    @property
    def score(self):
        if self.results != None:
            return sum([1 for i in self.results if i.is_ref_specific])/len(self.results)
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of properties,num of refspecifics,score
{0},{1},{2}""".format(len(self.results), sum([1 for i in self.results if i.is_ref_specific]),self.score)


    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
