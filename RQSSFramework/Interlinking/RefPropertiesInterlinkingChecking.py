import sys
from typing import List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class PropInterlinkingResult(NamedTuple):
    property: str
    num_equivalent: int

    def __repr__(self):
        return "Property {0} has {1} equivalents".format(self.property, self.num_equivalent)


class RefPropertiesInterlinkingChecker:
    results: List[PropInterlinkingResult] = None
    _ref_properties: List[str]

    def __init__(self, ref_properties: List[str]):
        self._ref_properties = ref_properties

    def check_reference_interlinking_from_Wikdiata(self) -> List[PropInterlinkingResult]:
        self.results = []
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        for prop in self._ref_properties:
            print('\t Getting equivalents of reference property: ', prop)
            sparql.setQuery(
                RQSS_QUERIES['get_property_equivalents_Wikidata'].format(prop))
            sparql.setReturnFormat(JSON)
            try:
                results = sparql.query().convert()
                for result in results["results"]["bindings"]:
                    value = result["to_ret"]["value"]
                    if value.isdigit():
                        self.results.append(
                            PropInterlinkingResult(prop, int(value)))
                    else:
                        raise Exception(
                            'Non-integer value was returned from Wikidata')
            except Exception as e:
                print('\t\t ERROR: ', e)
                continue
        return self.results

    @property
    def score(self):
        if self.results is not None:
            return len([i for i in self.results if i.num_equivalent > 0])/len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of properties,score
{0},{1}""".format(
            len(self.results),
            self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results is None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
