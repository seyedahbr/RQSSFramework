from typing import List, NamedTuple


class RefSharingResult(NamedTuple):
    total: int
    shared: int

    def __repr__(self):
        return "Number of reference nodes: {0}; shared references:{1}; ratio: {2}".format(self.total, self.shared, round(self.ratio, 2))

    @property
    def ratio(self):
        return (self.shared/self.total)


class RefNodeIncomings(NamedTuple):
    refnode: str
    num_of_incomes: int


class ReferenceSharingChecker:
    result: RefSharingResult = None
    ref_nodes: List[RefNodeIncomings]

    def __init__(self, ref_nodes: List[RefNodeIncomings]) -> None:
        self.ref_nodes = ref_nodes

    def count_seperate_shared_references(self) -> List[RefNodeIncomings]:
        ret_val:List[RefNodeIncomings] = []
        for record in self.ref_nodes:
            if int(record.num_of_incomes) > 1:
                ret_val.append(record)
        self.result = RefSharingResult(len(self.ref_nodes), len(ret_val))
        return ret_val

    @property
    def score(self):
        if self.result is not None:
            return self.result.ratio
        return None

    def __repr__(self):
        if self.result == None:
            return 'Results are not computed'
        return """num of ref nodes,shared nodes,score
{0},{1},{2}""".format(self.result.total, self.result.shared, self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print(self.result)
