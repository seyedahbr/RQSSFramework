from dataclasses import dataclass
from typing import List, NamedTuple
import pandas as pd

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
    _input: List[FactRef]

    def __init__(self, dataset_facts_refs: List[FactRef]):
        self._input = dataset_facts_refs
        self._df = pd.DataFrame(
            columns=['statement_id', 'fact', 'ref_predicate'])
        for x in self._input:
            self._df = self._df.append({
                'statement_id': x.statement_id,
                'fact': x.fact,
                'ref_predicate': x.ref_predicate if x.ref_predicate is not None else np.nan}, ignore_index=True)

    def check_property_completeness_Wikidata(self) -> List[PropertyCompletenessResult]:
        self.results = []
        return self.results
        

    @property
    def score(self):
        if self.results != None:
            total = len(
                [i for i in self._input if i.ref_predicate is not None])
            return sum([i.score for i in self.results])/total if total > 0 else 1
        return None

    @property
    def score_including_not_refed(self):
        if self.results != None:
            total_including_not_refed = len(self._input)
            return sum([i.score_including_not_refed for i in self.results])/total_including_not_refed if total_including_not_refed > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """total fact-reference pairs,total facts without reference,total facts (distinct),total referenced facts (distinct),total reference properties (distinct),score,score including not refed
{0},{1},{2},{3},{4},{5},{6},{7},{8}""".format(
            len([i for i in self._input if i.ref_predicate is not None]),
            len([i for i in self._input if i.ref_predicate is None]),
            len(list(dict.fromkeys([i.fact for i in self._input]))),
            len(list(dict.fromkeys(
                [i.fact for i in self._input if i.ref_predicate is not None]))),
            len(list(dict.fromkeys([i.ref_predicate for i in self._input]))),
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
