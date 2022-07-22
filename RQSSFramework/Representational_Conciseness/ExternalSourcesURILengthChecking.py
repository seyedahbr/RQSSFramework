from typing import Iterator, List, NamedTuple
from urllib.parse import quote_plus

from rdflib import URIRef


class URLLength(NamedTuple):
    url_len: int


class ExternalURLLengthChecking:
    _uris = []
    results: List[URLLength] = None

    def __init__(self, uris: Iterator[URIRef]):
        self._uris = list(uris)

    def count_length_scores(self) -> List[URLLength]:
        self.results = []
        [self.results.append(URLLength(len(quote_plus(uri))))
         for uri in self._uris]
        return self.results

    @property
    def score(self):
        if self.results is not None:
            total_less_than_80 = len(
                [i for i in self.results if i.url_len <= 80])
            total_between_80_2083 = len(
                [i for i in self.results if i.url_len > 80 and i.url_len <= 2083])
            total_between_2083_4096 = len(
                [i for i in self.results if i.url_len > 2083 and i.url_len <= 4096])
            return (total_less_than_80 + (total_between_80_2083 * 0.75) + (total_between_2083_4096 * 0.5)) / len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of uris,num of uris with len<=80,num of uris with 80<len<=2083,num of uris with 2083<len<=4096,num of uris with len>4096,score
{0},{1},{2},{3},{4},{5}""".format(
            len(self.results),
            len([i for i in self.results if i.url_len <= 80]),
            len([i for i in self.results if i.url_len > 80 and i.url_len <= 2083]),
            len([i for i in self.results if i.url_len > 2083 and i.url_len <= 4096]),
            len([i for i in self.results if i.url_len > 4096]),
            self.score)
