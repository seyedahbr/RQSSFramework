from typing import Dict, List, NamedTuple


class HumanAddedResult(NamedTuple):
    item: str
    total: int
    human_added: int

    def __repr__(self):
        return "Number of references in item {0}: {1}; human_added references:{2}; score: {3}".format(self.item, self.total, self.human_added, self.score)

    @property
    def score(self):
        return self.human_added/self.total


class HumanReferenceInItemChecker:
    results: List[HumanAddedResult] = None
    _item_refed_facts: Dict

    def __init__(self, item_referenced_facts: Dict) -> None:
        self._item_refed_facts = item_referenced_facts

    def check_referenced_facts_human_added(self) -> List[HumanAddedResult]:
        return self.results

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for result in self.results:
            print(result)
