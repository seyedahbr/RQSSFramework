from typing import Dict, List, NamedTuple

import pandas as pd
import math

from Completeness.SchemaBasedRefPropertiesCompletenessChecking import FactRef


class PropertyCompletenessResult(NamedTuple):
    fact: str
    ref_predicate: str
    total_instances: int
    total_instances_not_refed: int
    total_refed: int

    @property
    def score(self):
        return self.total_refed / self.total_instances if self.total_instances > 0 else math.nan

    @property
    def score_including_not_refed(self):
        including_not_refed = self.total_instances_not_refed
        return self.total_refed / including_not_refed if including_not_refed > 0 else math.nan

    def __repr__(self):
        return '''For reference property {0} and fact {1} in the schema-level,\n
\tTotal fact instances: {2}
\tTotal not referenced fact instances: {3}
\tTotal referenced fact (with {1}) instances: {4}
\tScore: {5}
\tScore (including not referenced instances): {6}'''.format(self.ref_predicate, self.fact, self.total_instances, self.total_instances_not_refed, self.total_refed, self.score, self.score_including_not_refed)


class PropertyCompletenessChecker:
    results: List[PropertyCompletenessResult] = None
    _input: List[FactRef]

    def __init__(self, dataset_facts_refs: List[FactRef]):
        self._input = dataset_facts_refs
        if not self._input:
            pass
        self._df = pd.DataFrame.from_records(
            self._input, columns=self._input[0]._fields)

    def check_property_completeness_Wikidata(self) -> List[PropertyCompletenessResult]:
        self.results = []
        fact_equivalence_classes_refs = self._get_distinct_fact_and_ref_predicates()
        for fact in fact_equivalence_classes_refs:
            for ref in fact_equivalence_classes_refs[fact]:
                print('computing fact {0}, ref {1}'.format(fact, ref))
                total_instances = len(self._df.loc[(self._df['fact'] == fact) & ~(
                    self._df['ref_predicate'].isna())].drop_duplicates('statement_id'))
                total_instances_not_refed = len(self._df.loc[(
                    self._df['fact'] == fact)].drop_duplicates('statement_id'))
                total_refed = len(self._df.loc[(self._df['fact'] == fact) & (
                    self._df['ref_predicate'] == ref)].drop_duplicates('statement_id'))
                self.results.append(PropertyCompletenessResult(
                    fact, ref, total_instances, total_instances_not_refed, total_refed))
        return self.results

    def _get_distinct_fact_and_ref_predicates(self) -> Dict:
        ret_dict = {}
        for fact_ref in self._input:
            if fact_ref.ref_predicate is None:
                continue
            if fact_ref.fact not in ret_dict.keys():
                ret_dict[fact_ref.fact] = []
            if fact_ref.ref_predicate not in ret_dict[fact_ref.fact]:
                ret_dict[fact_ref.fact].append(fact_ref.ref_predicate)
        return ret_dict

    @property
    def score(self):
        if self.results is not None:
            total = sum([i.score for i in self.results if not math.isnan(i.score)])
            return total / len(self.results) if len(self.results) > 0 else 1
        return None

    @property
    def score_including_not_refed(self):
        if self.results is not None:
            total = sum([i.score_including_not_refed for i in self.results if not math.isnan(i.score_including_not_refed)])
            return total / len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """total fact-reference pairs,total facts without reference,total facts (distinct),total referenced facts (distinct),total reference properties (distinct),total property-reference pairs,score,score including not refed
{0},{1},{2},{3},{4},{5},{6},{7}""".format(
            len([i for i in self._input if i.ref_predicate is not None]),
            len([i for i in self._input if i.ref_predicate is None]),
            len(list(dict.fromkeys([i.fact for i in self._input]))),
            len(list(dict.fromkeys(
                [i.fact for i in self._input if i.ref_predicate is not None]))),
            len(list(dict.fromkeys([i.ref_predicate for i in self._input]))),
            len(self.results),
            self.score,
            self.score_including_not_refed)

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('results are not computed')
            return
        for r in self.results:
            print(r)
