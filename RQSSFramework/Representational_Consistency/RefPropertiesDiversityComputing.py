from typing import List, NamedTuple

class RefPropInstances(NamedTuple):
    ref_prop: str
    num_instances: int

class RefPropertyDiversityComputer:
    _prop_dist: List[RefPropInstances]
    _num_ref_property: int
    _num_ref_triple: int

    def __init__(self, prop_dist: List[RefPropInstances], num_ref_property: int, num_ref_triple: int):
        self._prop_dist = prop_dist
        self._num_ref_property = num_ref_property
        self._num_ref_triple = num_ref_triple
    
    @property
    def score(self):
        return 1 - self._num_ref_property / self._num_ref_triple if self._num_ref_triple > 0 else 1
    
    def __repr__(self):
        return """total ref properties,total ref triples,score
{0},{1},{2}""".format(
            self._num_ref_property,
            self._num_ref_triple,
            self.score)
