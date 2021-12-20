from typing import Iterator, List, NamedTuple
import pyshex
import ShExes

class WikibaseSyntaxChecker:
    _num_fails = None

    def __init__(self):
        self._num_fails = 0
    
    def check_shex_schema(self) -> int:
        num_fails = 0
        results=pyshex.ShExEvaluator.evaluate(None,ShExes.SHEX_SCHEMAS['wikibase_reference_reification'])
        self._num_fails = num_fails
        return num_fails
    
    def print_results(self):
        """
        print self._num_fains if it is already computed
        """
        if self._num_fails == None:
            print('Results are not computed')
            return
        print("Number of syntax fails:{1}".format(self._num_fails))