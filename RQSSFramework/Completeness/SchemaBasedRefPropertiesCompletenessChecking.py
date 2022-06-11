from typing import Dict, List, NamedTuple

import pandas as pd
from EntitySchemaExtractor import EidRefSummary


class SchemaBasedCompletenessResult(NamedTuple):
    fact: str
    ref_predicate: str
    total_instances: int
    total_instances_not_refed: int
    total_refed_instances_schema_based: int

    @property
    def score(self):
        return self.total_refed_instances_schema_based / self.total_instances if self.total_instances > 0 else 1

    @property
    def score_including_not_refed(self):
        including_not_refed = self.total_instances + self.total_instances_not_refed
        return self.total_refed_instances_schema_based / including_not_refed if including_not_refed > 0 else 1

    def __repr__(self):
        return '''For fact {0} and reference property {1} in the schema-level,\n
\tTotal fact instances: {2}
\tTotal not referenced fact instances: {3}
\tTotal referenced fact (with {1}) instances: {4}
\tScore: {5}
\tScore (including not referenced instances): {6}'''.format(self.fact, self.ref_predicate, self.total_instances, self.total_instances_not_refed, self.total_refed_instances_schema_based, self.score, self.score_including_not_refed)


class FactRef(NamedTuple):
    statement_id: str
    fact: str
    ref_predicate: str = None

    def __repr__(self) -> str:
        return "Fact: {1}, Reference Property: {2}".format(self.fact, self.ref_predicate)


class SchemaBasedRefPropertiesCompletenessChecker:
    results: List[SchemaBasedCompletenessResult] = None
    _input: List[FactRef]  # it is equivalent to the set "H" in the manuscript

    def __init__(self, dataset: List[FactRef]):
        self._input = dataset
        if not self._input:
            pass
        self._df = pd.DataFrame.from_records(
            self._input, columns=self._input[0]._fields)

    def check_schema_based_property_completeness_Wikidata(self, wikidata_entityschemas_ref_summery: List[EidRefSummary]) -> List[SchemaBasedCompletenessResult]:
        self.results = []
        eschema_facts_refs = self._get_eschema_distinct_properties_and_ref_predicates(
            wikidata_entityschemas_ref_summery)
        print('len of eschema_fact_refs: ', len(eschema_facts_refs.keys()))
        for fact in eschema_facts_refs.keys():
            for ref in eschema_facts_refs[fact]:
                print('computing fact {0}, ref {1}'.format(fact, ref))
                total_instances = len(self._df.loc[(self._df['fact'] == fact) & ~(
                    self._df['ref_predicate'].isna())].drop_duplicates('statement_id'))
                total_instances_not_refed = len(self._df.loc[(
                    self._df['fact'] == fact)].drop_duplicates('statement_id'))
                total_refed_instances_schema_based = len(self._df.loc[(self._df['fact'] == fact) & (
                    self._df['ref_predicate'] == ref)].drop_duplicates('statement_id'))
                self.results.append(SchemaBasedCompletenessResult(
                    fact, ref, total_instances, total_instances_not_refed, total_refed_instances_schema_based))
        return self.results

    def _get_eschema_distinct_properties_and_ref_predicates(self, wikidata_entityschemas_ref_summery: List[EidRefSummary]) -> Dict:
        ret_dict = {}
        for schema in wikidata_entityschemas_ref_summery:
            for fact_ref in schema.refed_facts_refs:
                if not fact_ref.ref_predicates:
                    continue
                if fact_ref.refed_fact not in ret_dict.keys():
                    ret_dict[str(fact_ref.refed_fact)] = []
                for ref in fact_ref.ref_predicates:
                    if ref not in ret_dict[str(fact_ref.refed_fact)]:
                        ret_dict[str(fact_ref.refed_fact)].append(ref)
        return ret_dict

    @property
    def score(self):
        if self.results is not None:
            total = len(
                [i for i in self._input if i.ref_predicate is not None])
            return sum([i.score for i in self.results])/total if total > 0 else 1
        return None

    @property
    def score_including_not_refed(self):
        if self.results is not None:
            total_including_not_refed = len(self._input)
            return sum([i.score_including_not_refed for i in self.results])/total_including_not_refed if total_including_not_refed > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """total fact-reference pairs,total facts without reference,total facts (distinct),total referenced facts (distinct),total reference properties (distinct),total reference-specific predicates mentioned in schema level (distinct),total facts that are referenced with a reference-specific property mentioned in the schema level,score,score including not refed
{0},{1},{2},{3},{4},{5},{6},{7},{8}""".format(
            len([i for i in self._input if i.ref_predicate is not None]),
            len([i for i in self._input if i.ref_predicate is None]),
            len(list(dict.fromkeys([i.fact for i in self._input]))),
            len(list(dict.fromkeys(
                [i.fact for i in self._input if i.ref_predicate is not None]))),
            len(list(dict.fromkeys([i.ref_predicate for i in self._input]))),
            len(list(dict.fromkeys([i.ref_predicate for i in self.results]))),
            sum([i.total_refed_instances_schema_based for i in self.results]),
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
