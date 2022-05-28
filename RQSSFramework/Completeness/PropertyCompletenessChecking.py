from dataclasses import dataclass
from typing import List, NamedTuple

from EntitySchemaExtractor import EidRefSummary


class PropertyCompletenessResult(NamedTuple):
    fact_predicate_id: str
    ref_predicate_id: str
    total_instances: int
    total_refed_instances: int

    def __repr__(self):
        return "Fact predicate: {0}, has at least one reference predicate: {1} in instance-level; total instances: {2}; total referenced instances: {3} ".format(self.fact_predicate_id, self.ref_predicate_id, self.total_instances, self.total_refed_instances)


class FactRef(NamedTuple):
    fact_predicate_id: str
    ref_predicate_id: str

class PropertyCompletenessChecker:
    results: List[PropertyCompletenessResult] = None
    _facts_refs: List[FactRef]

    def __init__(self, dataset_facts_refs: List[FactRef]):
        self._facts_refs = dataset_facts_refs

    def check_property_completeness_Wikidata(self) -> List[PropertyCompletenessResult]:
        self.results = []
        return self.results

    @property
    def score(self):
        pass

    @property
    def results(self) -> List[PropertyCompletenessResult]:
        pass

    def __repr__(self):
        pass

    def print_results(self):
        """
        print self.resultsif it is already computed
        """
        if self.results == None:
            print('results are not computed')
            return
        for r in self.results:
            print(r)
