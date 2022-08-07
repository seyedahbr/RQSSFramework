from typing import NamedTuple

from Queries import RQSS_QUERIES
from RQSS_Extractor import perform_query


class BlankNodeResults(NamedTuple):
    num_ref_node: int
    num_ref_predicate: int
    num_ref_value: int
    num_ref_node_bn: int
    num_ref_predicate_bn: int
    num_ref_value_bn: int

    def __repr__(self):
        return "Total checked uris: {0}; Blank nodes in ref nodes :{1}; Blank nodes in ref predicates :{2}; Blank nodes in ref values :{3} score: {4}".format(self.total, self.fails, self.score)

    @property
    def score(self):
        return 1 - (self.num_ref_node_bn + self.num_ref_predicate_bn + self.num_ref_value_bn) / (self.num_ref_node + self.num_ref_predicate + self.num_ref_value) if (self.num_ref_node + self.num_ref_predicate + self.num_ref_value) > 0 else 1


class BlankNodeChecker:
    result: BlankNodeResults = None
    _endpoint: str = None

    def __init__(self, endpoint: str = None):
        self._endpoint = endpoint

    def check_blank_nodes_over_endpoint(self) -> BlankNodeResults:
        print('Running query:')
        print('\tGet number of reference nodes ...')
        num_ref_node = int(perform_query(
            self._endpoint, RQSS_QUERIES['get_num_of_provWasDerivedFrom_wikimedia'])[0][0])
        print('\tGet number of reference predicates ...')
        num_ref_predicate = int(perform_query(
            self._endpoint, RQSS_QUERIES['get_num_of_ref_predicate_wikimedia'])[0][0])
        print('\tGet number of reference values ...')
        num_ref_value = int(perform_query(
            self._endpoint, RQSS_QUERIES['get_num_of_ref_value_wikimedia'])[0][0])
        print('\tGet number of blank reference nodes ...')
        num_ref_node_bn = int(perform_query(
            self._endpoint, RQSS_QUERIES['get_num_of_BN_provWasDerivedFrom_wikimedia'])[0][0])
        print('\tGet number of blank reference predicates ...')
        num_ref_predicate_bn = int(perform_query(
            self._endpoint, RQSS_QUERIES['get_num_of_BN_ref_predicate_wikimedia'])[0][0])
        print('\tGet number of blank reference values ...')
        num_ref_value_bn = int(perform_query(
            self._endpoint, RQSS_QUERIES['get_num_of_BN_ref_value_wikimedia'])[0][0])
        self.result = BlankNodeResults(
            num_ref_node,
            num_ref_predicate,
            num_ref_value,
            num_ref_node_bn,
            num_ref_predicate_bn,
            num_ref_value_bn)
        return self.result

    @property
    def score(self):
        if self.result is not None:
            return self.result.score
        return None

    def __repr__(self):
        if self.result is None:
            return 'Results are not computed'
        return """num of ref nodes,num of ref predicates,num of ref values,num of BLANK ref nodes,num of BLANK ref predicates,num of BLANK ref values,score
{0},{1},{2},{3},{4},{5},{6}""".format(
            self.result.num_ref_node,
            self.result.num_ref_predicate,
            self.result.num_ref_value,
            self.result.num_ref_node_bn,
            self.result.num_ref_predicate_bn,
            self.result.num_ref_value_bn,
            self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result is None:
            print('Results are not computed')
            return
        print(self.result)
