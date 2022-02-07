import sys
from typing import Dict, List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class RangeConsistencyResult(NamedTuple):
    ref_property: str
    total: int
    fails: int
    not_exixts: int

    def __repr__(self):
        return "Number of checked values for propety {0}: {1}; fails:{2}; score:{3}; range constrints not exists:{4}".format(self.ref_property, self.total, self.fails, self.score, self.not_exixts)

    @property
    def score(self):
        return 1-(self.fails/self.total)


class TriplesRangeConsistencyChecker:
    results: List[RangeConsistencyResult] = None
    _properties_values: Dict
    _ranges: Dict

    def __init__(self, prop_vals: Dict, ranges: Dict = None):
        self._properties_values = prop_vals
        if ranges == None:
            self._ranges = self.get_property_ranges_from_Wikidata()
            print(self._ranges)
        else:
            self._ranges = ranges

    def check_all_value_ranges(self) -> List[RangeConsistencyResult]:
        self.results = []
        for prop in self._properties_values.keys():
            num_fails = 0
            num_not_exists = 0
            for value in self._properties_values[str(prop)]:
                if len(self._ranges[str(prop)]) == 0:
                    num_not_exists += 1
                    continue
                failed = True
                for range in self._ranges[str(prop)]:
                    if self.check_range_value(value, range):
                        failed = False
                        break
                if failed:
                    num_fails += 1
            self.results.append(RangeConsistencyResult(str(prop), len(
                self._properties_values[str(prop)]), num_fails, num_not_exists))
        return self.results

    def check_range_value(self, value: str, range: str):
        if value == range:
            return True
        return False

    def get_property_ranges_from_Wikidata(self) -> Dict:
        ret_val = Dict.fromkeys(self._properties_values.keys())
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper("https://query.wikidata.org/sparql",agent=user_agent)
        for prop in self._properties_values.keys():
            ret_val[str(prop)] = list()
            sparql.setQuery(
                RQSS_QUERIES['get_property_range_wikimedia'].format(prop))
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