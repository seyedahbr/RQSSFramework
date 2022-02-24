import re
import sys
from typing import Dict, List, NamedTuple

import numpy as np
from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class LiteralSyntaxResult(NamedTuple):
    ref_property: str
    total: int
    fails: int
    errors: int
    regexes: int

    def __repr__(self):
        return "Number of checked values for propety {0}: {1}; fails:{2}; score:{3}; regex errors:{4}; regex not exists:{5}".format(self.ref_property, self.total, self.fails, self.score, self.errors, self.regexes)

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
            # return an empty result (only not_exists tag=true) for properties that have not any regex in Wikidata
            if len(self._regexes[str(prop)]) == 0:
                self.results.append(LiteralSyntaxResult(str(prop), len(
                    self._properties_values[str(prop)]), np.nan, np.nan, 0))
                continue

            num_fails = 0
            errors = []
            for value in self._properties_values[str(prop)]:
                for regex in self._regexes[str(prop)]:
                    if regex in errors:
                        continue
                    try:
                        pattern = re.compile(regex)
                        if bool(re.match(pattern, value)):
                            failed = False
                            break
                    except re.error as err:
                        errors.append(regex)
                        continue
                if failed:
                    num_fails += 1
            self.results.append(LiteralSyntaxResult(str(prop), len(
                self._properties_values[str(prop)]), num_fails, len(errors), len(self._regexes[str(prop)])))
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

    @property
    def score(self):
        if self.results != None:
            return 1 - sum([0 if np.isnan(i.fails) else i.fails for i in self.results])/sum([i.total for i in self.results])
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of properties,total literals,total regexes,total fails,total errors,total not exists regex,score
{0},{1},{2},{3},{4},{5},{6}""".format(len(self.results),
                                      sum([i.total for i in self.results]),
                                      sum([i.regexes for i in self.results]),
                                      sum([
                                          0 if np.isnan(i.fails) else i.fails for i in self.results]),
                                      sum([
                                          0 if np.isnan(i.errors) else i.errors for i in self.results]),
                                      sum([i.total for i in self.results if i.regexes == 0]), self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
