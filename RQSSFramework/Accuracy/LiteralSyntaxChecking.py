import re
import sys
from typing import Dict, List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class LiteralSyntaxResult(NamedTuple):
    ref_property: str
    total: int
    fails: int
    errors: int

    def __repr__(self):
        return "Number of checked values for propety {0}: {1}; fails:{2}; score:{3}; regex errors:{4}".format(self.ref_property, self.total, self.fails, self.score, self.errors)

    @property
    def score(self):
        return 1-(self.fails/self.total)


class WikibaseRefLiteralSyntaxChecker:
    results: List[LiteralSyntaxResult] = None
    _properties_values: Dict
    _regexes: Dict

    def __init__(self, prop_vals: Dict, regexes: Dict = None):
        self._properties_values = prop_vals
        if regexes == None:
            self._regexes = self.get_property_regex_from_Wikidata()
        else:
            self._regexes = regexes

    def check_literals_regex(self) -> List[LiteralSyntaxResult]:
        self.results = []
        for prop in self._properties_values.keys():
            num_fails = 0
            num_errors = 0
            for value in self._properties_values[str(prop)]:
                failed = True
                for regex in self._regexes[str(prop)]:
                    try:
                        pattern = re.compile(regex)
                        if bool(re.match(pattern, value)):
                            failed = False
                            break
                    except re.error as err:
                        num_errors += 1
                        continue
                if failed:
                    num_fails += 1
            self.results.append(LiteralSyntaxResult(str(prop), len(
                self._properties_values[str(prop)]), num_fails, num_errors))
        return self.results

    def get_property_regex_from_Wikidata(self) -> Dict:
        ret_val = Dict.fromkeys(self._properties_values.keys())
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        for prop in self._properties_values.keys():
            ret_val[str(prop)] = list()
            sparql.setQuery(
                RQSS_QUERIES['get_property_constraints_regex'].format(prop))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value = result["to_ret"]["value"]
                ret_val[str(prop)].append(value)
        return ret_val

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
