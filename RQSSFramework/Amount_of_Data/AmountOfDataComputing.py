from typing import List, NamedTuple


class RefNodeOutgoing(NamedTuple):
    ref_node: str
    num_of_out: int


class AmountOfDataComputer:
    _triple_dist: List[RefNodeOutgoing]
    _literal_dist: List[RefNodeOutgoing]
    _num_of_statement_node: int
    _num_of_ref_node: int

    def __init__(self, triple_dist: List[RefNodeOutgoing], literal_dist: List[RefNodeOutgoing], num_of_statement_node: int, num_of_ref_node: int):
        self._triple_dist = triple_dist
        self._literal_dist = literal_dist
        self._num_of_statement_node = num_of_statement_node
        self._num_of_ref_node = num_of_ref_node

    @property
    def ref_node_per_statement_ratio(self):
        pass

    @property
    def ref_triple_per_statement_ratio(self):
        pass

    @property
    def ref_triple_per_ref_node_ratio(self):
        pass

    @property
    def ref_literal_per_ref_node_ratio(self):
        pass

    def __repr__(self):
        pass
