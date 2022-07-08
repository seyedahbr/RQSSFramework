from typing import List, NamedTuple


class RefNodeOutgoing(NamedTuple):
    ref_node: str
    num_out: int


class AmountOfDataComputer:
    _triple_dist: List[RefNodeOutgoing]
    _literal_dist: List[RefNodeOutgoing]
    _num_statement_node: int
    _num_ref_node: int

    def __init__(self, triple_dist: List[RefNodeOutgoing], literal_dist: List[RefNodeOutgoing], num_of_statement_node: int, num_of_ref_node: int):
        self._triple_dist = triple_dist
        self._literal_dist = literal_dist
        self._num_statement_node = num_of_statement_node
        self._num_ref_node = num_of_ref_node

    @property
    def ref_node_per_statement_ratio(self):
        return self._num_ref_node / self._num_statement_node

    @property
    def ref_triple_per_statement_ratio(self):
        num_ref_triple = sum([i.num_out for i in self._triple_dist])
        return num_ref_triple / self._num_statement_node

    @property
    def ref_triple_per_ref_node_ratio(self):
        num_ref_triple = sum([i.num_out for i in self._triple_dist])
        return num_ref_triple / self._num_statement_node

    @property
    def ref_literal_per_ref_node_ratio(self):
        num_ref_literal = sum([i.num_out for i in self._literal_dist])
        return num_ref_literal / self._num_statement_node

    def __repr__(self):
        return """ref node per statement ratio,ref triple per statement ratio,ref triple per ref node ratio,ref literal per ref node ratio
{0},{1},{2},{3}""".format(
            self.ref_node_per_statement_ratio,
            self.ref_triple_per_statement_ratio,
            self.ref_triple_per_ref_node_ratio,
            self.ref_literal_per_ref_node_ratio)
