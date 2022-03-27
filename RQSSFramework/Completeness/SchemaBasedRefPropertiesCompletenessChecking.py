from dataclasses import dataclass
from typing import Dict, List, NamedTuple

from EntitySchemaExtractor import EidRefSummary, RefedFactRef


class SchemaBasedCompletenessResult(NamedTuple):
    class_id: str
    fact_predicate_id: str
    ref_predicate_id: str
    total_instances: int = 0
    # total number of instances with the ref_predicate_id
    total_refed_instances: int = 0

    def __repr__(self):
        return "Class {0}, with fact predicate: {1}, has a reference predicate: {2} in the schema level (E-ids); total instances: {3}; total referenced instances: {4} ".format(self.class_id, self.fact_predicate_id, self.ref_predicate_id, self.total_instances, self.total_refed_instances)


@dataclass
class ClassRefedFactRef:
    class_id: str
    refed_fact: str
    ref_predicates: List[str]

    def __repr__(self) -> str:
        return '''\n
\tclass id: {0}
\treferenced fact: {1}
\tref-specific properties: {2}
        '''.format(self.class_id, self.refed_fact, self.ref_predicates)


class SchemaBasedRefPropertiesCompletenessChecker:
    results: List[SchemaBasedCompletenessResult] = None
    _refed_facts: List[ClassRefedFactRef]

    def __init__(self, dataset_refed_facts: List[ClassRefedFactRef]):
        self._refed_facts = dataset_refed_facts

    def check_schema_based_property_completeness_Wikidata(self, wikidata_entityschemas_ref_summery: List[EidRefSummary]) -> List[SchemaBasedCompletenessResult]:
        self.results = []
        return self.results

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """"""

    def print_results(self):
        """
        print self.resultsif it is already computed
        """
        if self.results == None:
            print('results are not computed')
            return
        for r in self.results:
            print(r)
