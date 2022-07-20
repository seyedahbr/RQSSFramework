from typing import Iterator, List, NamedTuple
from rdflib import URIRef

class URLLength(NamedTuple):
    url_len: int

class ExternalURLLengthChecking:
    _uris = []
    results = None

    def __init__(self, uris: Iterator[URIRef]):
        self._uris = list(uris)

    def count_length_scores(self) -> List[URLLength]:
        pass

    @property
    def score(self):
        pass

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        pass