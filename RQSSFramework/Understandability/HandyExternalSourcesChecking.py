from typing import Iterator, List, NamedTuple


class ExternalSourceHandyScore(NamedTuple):
    source: str
    handy_score: float = None

    def __repr__(self):
        pass


class ExternalURIsVolatilityChecker:
    
    def __init__(self):
        pass

    

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
