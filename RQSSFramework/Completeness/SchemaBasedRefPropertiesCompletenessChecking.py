from dataclasses import dataclass
from typing import List, NamedTuple

from EntitySchemaExtractor import EidRefSummary


class SchemaBasedCompletenessResult(NamedTuple):
    fact: str
    ref_predicate: str
    total_instances: int
    total_instances_not_refed: int
    total_refed_instances: int

    @property
    def score(self):
        return self.total_refed_instances / self.total_instances if self.total_instances > 0 else 1
    @property
    def score_including_not_refed(self):
        including_not_refed = self.total_instances + self.total_instances_not_refed
        return self.total_refed_instances / including_not_refed if including_not_refed > 0 else 1
    def __repr__(self):
        return '''For fact {0} and reference properties {1} in the schema-level,\n
\tTotal fact instances: {2}
\tTotal not referenced fact instances: {3}
\tTotal referenced fact (with {1}) instances: {4}
\tScore: {5}
\tScore (including not referenced instances): {6}'''.format(self.fact, self.ref_predicate, self.total_instances, self.total_instances_not_refed, self.total_refed_instances, self.score, self.score_including_not_refed)

@dataclass
class ClassRefedFactRef:
    class_id: str
    fact: str
    ref_predicate: str = None

    def __repr__(self) -> str:
        return "Class id: {0}, Fact: {1}, Reference Property: {2}".format(self.class_id, self.fact, self.ref_predicate)


class SchemaBasedRefPropertiesCompletenessChecker:
    results: List[SchemaBasedCompletenessResult] = None
    _input: List[ClassRefedFactRef]

    def __init__(self, dataset: List[ClassRefedFactRef]):
        self._input = dataset

    def check_schema_based_property_completeness_Wikidata(self, wikidata_entityschemas_ref_summery: List[EidRefSummary]) -> List[SchemaBasedCompletenessResult]:
        self.results = []
        for schema in wikidata_entityschemas_ref_summery:
            for fact_ref in schema.refed_facts_refs:
                for ref in fact_ref.ref_predicates:
                    total_instances = len([x for x in self._input if x.fact == fact_ref.refed_fact and x.ref_predicate is not None])
                    total_instances_not_refed = len([x for x in self._input if x.fact == fact_ref.refed_fact])
                    total_refed_instances = len([x for x in self._input if x.fact == fact_ref.refed_fact and x.ref_predicate is not None and x.ref_predicate == ref ])
                    self.results.append(SchemaBasedCompletenessResult(fact_ref.refed_fact, ref,total_instances,total_instances_not_refed, total_refed_instances))

        return self.results

    @property
    def score(self):
        if self.results != None:
            total = sum([i.total_instances for i in self.results])
            return sum([i.total_refed_instances for i in self.results])/total if total > 0 else 1
        return None

    @property
    def score_including_not_refed(self):
        if self.results != None:
            total_including_not_refed = sum([(i.total_instances + i.total_instances_not_refed) for i in self.results])
            return sum([i.total_refed_instances for i in self.results])/total_including_not_refed if total_including_not_refed > 0 else 1
        return None

#     def __repr__(self):
#         if self.results == None:
#             return 'Results are not computed'
#         return """num of classes, total classes with defined schema, total referenced facts,total reference-specific predicates mentioned in schema level,total fact instances,total referenced fact instances,score
# {0},{1},{2},{3},{4},{5},{6}""".format(len(list(dict.fromkeys([i.class_id for i in self._refed_facts]))),
#                                   len(list(dict.fromkeys([i.class_id for i in self.results]))),
#                                   len(list(dict.fromkeys(
#                                       [i.fact_predicate_id for i in self.results]))),
#                                   len(list(dict.fromkeys(
#                                       [i.ref_predicate_id for i in self.results]))),
#                                   sum([i.total_instances for i in self.results]),
#                                   sum([i.total_refed_instances for i in self.results]),
#                                   self.score)

    def print_results(self):
        """
        print self._resultsif it is already computed
        """
        if self._results == None:
            print('results are not computed')
            return
        for r in self._results:
            print(r)
