import datetime
from typing import Iterator, List, NamedTuple

import requests
from usp.tree import sitemap_tree_for_homepage
from rdflib import URIRef


class VolatilityOfURI(NamedTuple):
    uri: URIRef
    volatility: float = None
    _NONE = '<None>'

    def __repr__(self):
        return "URI:{0:40}, voltility:{1}".format(self.uri, self.volatility)


class ExternalURIsVolatilityChecker:
    _uris = []
    results: List[VolatilityOfURI] = None

    def __init__(self, uris: Iterator[URIRef]):
        self._uris = list(dict.fromkeys(uris))  # remove duplications

    def check_external_uris_volatility(self) -> List[VolatilityOfURI]:
        self.results = []
        for uri in self._uris:
            tree = sitemap_tree_for_homepage(str(uri))
            for page in tree.all_pages():
                print("************** ", page.change_frequency)

        return self.results

    

    @property
    def score(self):
        if self.results != None:
            scored_list = [
                i.volatility for i in self.results if i.volatility != None]
            return sum(scored_list)/len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of uris,volatility score,not found
{0},{1},{2},{3},{4}""".format(len(self.results), self.score,len([i.volatility for i in self.results if i.volatility == None]))

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
