from typing import Iterator, List, NamedTuple
from urllib.parse import urlparse

import pydnsbl
from rdflib import URIRef


class BlacklistedOfDom(NamedTuple):
    domain: URIRef
    blacklisted: bool

    def __repr__(self):
        return "Domain:{0:40}, is in blacklist:{1}".format(self.domain, self.blacklisted)


class DNSBLBlacklistedChecker:
    _domains = []
    results: List[BlacklistedOfDom] = None

    def __init__(self, uris: Iterator[URIRef]):
        _uris = list(dict.fromkeys(uris))  # remove duplicated URIs
        # compute and remove duplicated domains
        self._domains = dict.fromkeys(self.domain_extractor(_uris))

    def domain_extractor(self, uris: Iterator[URIRef]) -> List[URIRef]:
        ret_list = []
        for u in uris:
            ret_list.append(urlparse(u).netloc)
        return ret_list

    def check_domain_blacklisted(self) -> List[BlacklistedOfDom]:
        self.results = []
        domain_checker = pydnsbl.DNSBLDomainChecker()
        for u in self._domains:
            try:
                r = domain_checker.check(u)
                self.results.append(BlacklistedOfDom(u, r.blacklisted))
            except Exception as e:
                self.results.append(BlacklistedOfDom(u, False))
                print(e)
        return self.results

    @property
    def score(self):
        if self.results is not None:
            return 1 - sum([1 for i in self.results if i.blacklisted])/len(self.results)
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of domains,blacklisted,score
{0},{1},{2}""".format(len(self.results), sum([1 for i in self.results if i.blacklisted]), self.score)

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
