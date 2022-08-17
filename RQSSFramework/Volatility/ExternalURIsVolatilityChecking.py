from typing import Iterator, List, NamedTuple

from rdflib import URIRef
from usp.objects.page import SitemapPageChangeFrequency
from usp.tree import sitemap_tree_for_homepage


class VolatilityOfURI(NamedTuple):
    uri: URIRef
    volatility: float = None

    def __repr__(self):
        return "URI:{0:40}, voltility:{1}".format(self.uri, self.volatility)


class ExternalURIsVolatilityChecker:
    _uris: List[URIRef] = []
    results: List[VolatilityOfURI] = None

    def __init__(self, uris: Iterator[URIRef]):
        self._uris = list(dict.fromkeys(uris))  # remove duplications

    def check_external_uris_volatility(self) -> List[VolatilityOfURI]:
        self.results = []
        for uri in self._uris:
            not_found = True
            tree = sitemap_tree_for_homepage(str(uri))
            for page in tree.all_pages():
                if str(uri) in str(page):
                    not_found = False
                    self.results.append(VolatilityOfURI(uri, self.get_volatility_from_change_freq(
                        page.change_frequency) if page.change_frequency is not None else None))
                    break
            if not_found:
                self.results.append(VolatilityOfURI(uri, None))

        return self.results

    def get_volatility_from_change_freq(self, change_freq: SitemapPageChangeFrequency) -> float:
        if change_freq.has_value('always'):
            return 1.0
        if change_freq.has_value('hourly'):
            return 0.9
        if change_freq.has_value('daily'):
            return 0.8
        if change_freq.has_value('weekly'):
            return 0.6
        if change_freq.has_value('monthly'):
            return 0.4
        if change_freq.has_value('yearly'):
            return 0.1
        return 0

    @property
    def score(self):
        if self.results is not None:
            scored_list = [
                i.volatility for i in self.results if i.volatility is not None]
            return sum(scored_list)/len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of uris,number of always changed-feq,number of hourly changed-feq,number of daily changed-feq,number of weekly changed-feq,number of monthly changed-feq,number of yearly changed-feq,not found,score
{0},{1},{2},{3},{4},{5},{6},{7},{8}""".format(
    len(self.results),
    len([i for i in self.results if i.volatility is not None and i.volatility == 1]),
    len([i for i in self.results if i.volatility is not None and i.volatility == 0.9]),
    len([i for i in self.results if i.volatility is not None and i.volatility == 0.8]),
    len([i for i in self.results if i.volatility is not None and i.volatility == 0.6]),
    len([i for i in self.results if i.volatility is not None and i.volatility == 0.4]),
    len([i for i in self.results if i.volatility is not None and i.volatility == 0.1]),
    len([i for i in self.results if i.volatility is None]),
    self.score
    )

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
