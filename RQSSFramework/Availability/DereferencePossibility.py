from typing import Iterator, List, NamedTuple

import requests
from rdflib import URIRef


class DerefOfURI(NamedTuple):
    uri: URIRef
    deref: bool

    def __repr__(self):
        return "URI:{0:40}, Deref:{1}".format(self.uri, self.deref)


class DerefrenceExplorer:
    _uris = []
    results = None

    def __init__(self, uris: Iterator[URIRef]):
        self._uris = list(dict.fromkeys(uris))  # remove duplications

    def check_dereferencies(self) -> List[DerefOfURI]:
        """
        check the accssessibility of each URI in the class
        """
        self.results = []
        for u in self._uris:
            try:
                r = requests.get(u, timeout=(10, 60))
                if r.status_code == 200:
                    self.results.append(DerefOfURI(u, True))
                else:
                    self.results.append(DerefOfURI(u, False))
            except Exception as e:
                self.results.append(DerefOfURI(u, False))
                print(e)
        return self.results

    @property
    def score(self):
        if self.results is not None:
            return sum([1 for i in self.results if i.deref])/len(self.results)
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of uris,available uris,score
{0},{1},{2}""".format(len(self.results), sum([1 for i in self.results if i.deref]), self.score)

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
