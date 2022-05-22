from dataclasses import dataclass
from typing import List, NamedTuple

from EntitySchemaExtractor import EidRefSummary


class SchemaBasedCompletenessResult(NamedTuple):
    class_id: str
    fact_predicate_id: str
    ref_predicate_id: str
    total_instances: int
    # total number of instances with the ref_predicate_id
    total_refed_instances: int

    def __repr__(self):
        return "Class {0}, with fact predicate: {1}, has a reference predicate: {2} in the schema level (E-ids); total instances: {3}; total referenced instances: {4} ".format(self.class_id, self.fact_predicate_id, self.ref_predicate_id, self.total_instances, self.total_refed_instances)


@dataclass
class SchemaBasedCompleteness:
    class_id: str
    fact_predicate_id: str
    ref_predicate_id: str
    total_instances: int
    # total number of instances with the ref_predicate_id
    total_refed_instances: int


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
    _results: List[SchemaBasedCompleteness] = None
    _refed_facts: List[ClassRefedFactRef]

    def __init__(self, dataset_refed_facts: List[ClassRefedFactRef]):
        self._refed_facts = dataset_refed_facts

    def check_schema_based_property_completeness_Wikidata(self, wikidata_entityschemas_ref_summery: List[EidRefSummary]) -> List[SchemaBasedCompletenessResult]:
        self._results = []
        schema_classes = []
        for match in wikidata_entityschemas_ref_summery:
            schema_classes.extend(match.related_classes)
        for item in self._refed_facts:
            if item.class_id not in schema_classes:
                continue
            for ref in item.ref_predicates:
                if len([x for x in self._results if x.class_id == item.class_id and x.fact_predicate_id == item.refed_fact and x.ref_predicate_id == ref]) == 0:
                    self._results.append(SchemaBasedCompleteness(
                        item.class_id, item.refed_fact, ref, 0, 0))
                refed_instance = 0
                for match in wikidata_entityschemas_ref_summery:
                    if item.class_id in match.related_classes:
                        for pred in match.refed_facts_refs:
                            if item.refed_fact == pred.refed_fact:
                                for schema_ref in pred.ref_predicates:
                                    if schema_ref == ref:
                                        refed_instance = 1
                self._update_result_entry(
                    item.class_id, item.refed_fact, ref, refed_instance)

        return self.results

    def _update_result_entry(self, class_id, fact, ref, num_instance_increment):
        for index, item in enumerate(self._results):
            if item.class_id == class_id and item.fact_predicate_id == fact and item.ref_predicate_id == ref:
                self._results[index].total_instances += 1
                self._results[index].total_refed_instances += num_instance_increment

    @property
    def score(self):
        if self.results != None:
            total = sum([i.total_instances for i in self.results])
            return sum([i.total_refed_instances for i in self.results])/total if total > 0 else 1
        return None

    @property
    def results(self) -> List[SchemaBasedCompletenessResult]:
        if self._results == None:
            return None
        ret_val: List[SchemaBasedCompletenessResult] = []
        for item in self._results:
            ret_val.append(SchemaBasedCompletenessResult(item.class_id, item.fact_predicate_id,
                                                         item.ref_predicate_id, item.total_instances, item.total_refed_instances))
        return ret_val

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of classes, total classes with defined schema, total referenced facts,total reference-specific predicates mentioned in schema level,total fact instances,total referenced fact instances,score
{0},{1},{2},{3},{4},{5},{6}""".format(len(list(dict.fromkeys([i.class_id for i in self._refed_facts]))),
                                  len(list(dict.fromkeys([i.class_id for i in self.results]))),
                                  len(list(dict.fromkeys(
                                      [i.fact_predicate_id for i in self.results]))),
                                  len(list(dict.fromkeys(
                                      [i.ref_predicate_id for i in self.results]))),
                                  sum([i.total_instances for i in self.results]),
                                  sum([i.total_refed_instances for i in self.results]),
                                  self.score)

    def print_results(self):
        """
        print self._resultsif it is already computed
        """
        if self._results == None:
            print('results are not computed')
            return
        for r in self._results:
            print(r)
