from typing import List, NamedTuple, Dict

from sqlalchemy import true


class TripleSemanticResult(NamedTuple):
    property: int       # the property at the heart of the fact
    half_matches: int   # number of subject-relation matches in reference triples
    full_matches: int   # number of exact matches in reference triples

    def __repr__(self):
        return "For propety {0}: number of subject_relation matches: {1}; exact matches:{2}; score:{3}".format(self.property, self.half_matches, self.full_matches, self.score)

    @property
    def score(self):
        return (self.full_matches/self.half_matches) if self.half_matches != 0 else 1.0


class FactReference(NamedTuple):
    subject: str
    property: str
    ref_property: str
    ref_value: str


class RefTripleSemanticChecker:
    results: List[TripleSemanticResult] = None
    _gold_standard: List[FactReference]
    _fact_ref_triples: List[FactReference]

    def __init__(self, gold_standard: List[FactReference], fact_ref_triples: List[FactReference]):
        self._gold_standard = gold_standard
        self._fact_ref_triples = fact_ref_triples

    def check_semantic_to_gold_standard(self) -> List[TripleSemanticResult]:
        self.results = []
        prop_results = {}
        for fact_gs in self._gold_standard:
            if fact_gs.property not in prop_results.keys():
                prop_results[str(fact_gs.property)] = [0, 0]
            for ref_triple in self._fact_ref_triples:
                if self.is_sub_rel_match(ref_triple, fact_gs):
                    prop_results[str(fact_gs.property)][0] += 1
                    if self.is_triple_exact_match(ref_triple, fact_gs):
                        prop_results[str(fact_gs.property)][1] += 1
        for prop in prop_results.keys():
            self.results.append(TripleSemanticResult(str(prop), prop_results[str(prop)][0], prop_results[str(prop)][1]))
        return self.results

    def is_sub_rel_match(self, ref_triple: FactReference, fact_gs: FactReference) -> bool:
        if ref_triple.subject == fact_gs.subject and\
           ref_triple.property == fact_gs.property and\
           ref_triple.ref_property == fact_gs.ref_property:
            return true
        # other equivalency conditions can be placed here
        # for example doing :sameAs searchs

    def is_triple_exact_match(self, ref_triple: FactReference, fact_gs: FactReference) -> bool:
        if ref_triple.subject == fact_gs.subject and\
           ref_triple.property == fact_gs.property and\
           ref_triple.ref_property == fact_gs.ref_property and\
           ref_triple.ref_value == fact_gs.ref_value:
            return true
        # other equivalency conditions can be placed here
        # for example doing :sameAs searchs

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for result in self.results:
            print(result)
