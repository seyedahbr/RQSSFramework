from typing import Iterator, List, NamedTuple

from Currency.ExternalURIsFreshnessChecking import FreshnessOfURI
from rdflib import URIRef
from usp.objects.page import SitemapPageChangeFrequency
from Volatility.ExternalURIsVolatilityChecking import VolatilityOfURI


class TimelinessOfURI(NamedTuple):
    uri: URIRef
    timeliness: float = None

    def __repr__(self):
        return "URI:{0:40}, Timeliness:{1}".format(self.uri, self.timeliness)


class ExternalURIsTimelinessChecker:
    _freshnesses: List[FreshnessOfURI] = []
    _volatilities: List[VolatilityOfURI] = []
    results: List[TimelinessOfURI] = None

    def __init__(self, freshness_list: Iterator[FreshnessOfURI], volatility_list: Iterator[VolatilityOfURI]):
        self._freshnesses = list(freshness_list)
        self._volatilities = list(volatility_list)

    def check_external_uris_timeliness(self) -> List[TimelinessOfURI]:
        self.results = []
        for uf in self._freshnesses:
            #not_found = True
            if uf.freshness_last_modif == None:
                self.results.append(TimelinessOfURI(uf.uri, None))
                continue
            for uv in self._volatilities:
                if uf.uri == uv.uri:
                    if uv.volatility == None:
                        self.results.append(TimelinessOfURI(uf.uri, None))
                        break
                    self.results.append(TimelinessOfURI(
                        uf.uri, uf.freshness_last_modif/uv.volatility if uv.volatility > 0 and uv.volatility > uf.freshness_last_modif else 1.0))
        return self.results

    def get_volatility_from_change_freq(self, change_freq: SitemapPageChangeFrequency) -> float:
        print('** A change_freq value is found **')
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
                i.timeliness for i in self.results if i.timeliness is not None]
            return sum(scored_list)/len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of uris,timeliness score,not found
{0},{1},{2}""".format(len(self.results), self.score, len([i.timeliness for i in self.results if i.timeliness == None]))

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
