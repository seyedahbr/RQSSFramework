import sys
from typing import Dict, List, NamedTuple

import numpy as np
from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class RangeConsistencyResult(NamedTuple):
    ref_property: str
    total: int
    fails: int
    ranges: int

    def __repr__(self):
        return "Number of checked values for propety {0}: {1}; fails:{2}; score:{3}; range constrints not exists:{4}".format(self.ref_property, self.total, self.fails, self.score, self.ranges)

    @property
    def score(self):
        return 1-(self.fails/self.total)


class TriplesRangeConsistencyChecker:
    results: List[RangeConsistencyResult] = None
    _properties_values: Dict
    _ranges: Dict
    _instances_subclass_of: Dict

    def __init__(self, prop_vals: Dict, ranges: Dict = None):
        self._properties_values = prop_vals
        self._ranges = self.get_property_ranges_from_Wikidata() if ranges is None else ranges
        self._instances_subclass_of = self.get_instances_subclass_of_values_from_Wikidata()

    def check_all_value_ranges(self) -> List[RangeConsistencyResult]:
        self.results = []
        for prop in self._properties_values.keys():
            if len(self._ranges[str(prop)]) == 0:
                self.results.append(RangeConsistencyResult(
                    str(prop), len(self._properties_values[str(prop)]), np.nan, 0))
                continue
            num_fails = 0
            for value in self._properties_values[str(prop)]:
                failed = True
                for range in self._ranges[str(prop)]:
                    if self.check_range_value(value, range):
                        failed = False
                        break
                if failed:
                    num_fails += 1
            self.results.append(RangeConsistencyResult(str(prop), len(
                self._properties_values[str(prop)]), num_fails, len(self._ranges[str(prop)])))
        return self.results

    def check_range_value(self, value: str, range: str):
        if range in self._instances_subclass_of[value]:
            return True
        return False

    def get_property_ranges_from_Wikidata(self) -> Dict:
        ret_val = Dict.fromkeys(self._properties_values.keys())
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        for prop in self._properties_values.keys():
            ret_val[str(prop)] = list()
            print('\t Getting ranges of reference property: ', prop)
            sparql.setQuery(
                RQSS_QUERIES['get_property_range_wikimedia'].format(prop))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value = result["to_ret"]["value"]
                ret_val[str(prop)].append(value)
        return ret_val

    def get_instances_subclass_of_values_from_Wikidata(self) -> Dict:

        distinct_values = set.union(
            *[set(value) for key, value in self._properties_values.items()])

        ret_val = Dict.fromkeys(distinct_values)
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        for ref_value in distinct_values:
            ret_val[ref_value] = list()
            print('\t Getting instances or subclasses of value: ', ref_value)
            sparql.setQuery(
                RQSS_QUERIES['get_instances_subclass_of_values_wikimedia'].format(ref_value))
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                query_value = result["to_ret"]["value"]
                ret_val[ref_value].append(query_value)
        return ret_val

    @property
    def score(self):
        if self.results is not None:
            return 1 - sum([0 if np.isnan(i.fails) else i.fails for i in self.results])/sum([i.total for i in self.results])
        return None

    def __repr__(self):
        if self.results is None:
            return 'Results are not computed'
        return """num of properties,total values,total ranges,total fails,total not exists ranges,score
{0},{1},{2},{3},{4},{5}""".format(len(self.results),
                                  sum([i.total for i in self.results]),
                                  sum([i.ranges for i in self.results]),
                                  sum([
                                      0 if np.isnan(i.fails) else i.fails for i in self.results]),
                                  sum([i.total for i in self.results if i.ranges == 0]), self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results is None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
