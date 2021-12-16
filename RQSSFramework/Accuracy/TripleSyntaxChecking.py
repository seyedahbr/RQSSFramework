from typing import Iterator, List, NamedTuple

class WikibaseSyntaxChecker:
    _num_fails = None

    def __init__(self):
        self._num_fails = 0
    
    def print_results(self):
        """
        print self._num_fains if it is already computed
        """
        if self._num_fails == None:
            print('Results are not computed')
            return
        print("Number of syntax fails:{1}".format(self._num_fails))