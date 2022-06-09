from dataclasses import dataclass
from typing import List, NamedTuple

from EntitySchemaExtractor import EidRefSummary
from SchemaBasedRefPropertiesCompletenessChecking import FactRef


class PropertyCompletenessResult(NamedTuple):
    fact: str
    ref_predicate: str
    total_instances: int
    total_instances_not_refed: int
    total_refed: int

    @property
    def score(self):
        return self.total_refed / self.total_instances if self.total_instances > 0 else 1

    @property
    def score_including_not_refed(self):
        including_not_refed = self.total_instances + self.total_instances_not_refed
        return self.total_refed / including_not_refed if including_not_refed > 0 else 1

    def __repr__(self):
        return '''For reference property {0} and fact {1} in the schema-level,\n
\tTotal fact instances: {2}
\tTotal not referenced fact instances: {3}
\tTotal referenced fact (with {1}) instances: {4}
\tScore: {5}
\tScore (including not referenced instances): {6}'''.format(self.ref_predicate, self.fact, self.total_instances, self.total_instances_not_refed, self.total_refed, self.score, self.score_including_not_refed)



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

    def __repr__(self):
        pass

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('results are not computed')
            return
        for r in self.results:
            print(r)
