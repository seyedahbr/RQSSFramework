import re
import sys
from typing import Iterator, List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class ExternalSourceHandyScore(NamedTuple):
    source: str
    handy_score: float = None

    def __repr__(self):
        return "source:{0:40}, handy score:{1}".format(self.source, self.handy_score)


class HandyExternalSourcesChecker:
    _sources = []
    results: List[ExternalSourceHandyScore] = None

    def __init__(self, sources: Iterator[str]):
        self._sources = list(sources)

    def check_handy_external_sources_wikidata(self) -> List[ExternalSourceHandyScore]:
        self.results = []
        for src in self._sources:
            score = 0
            if re.match(r"http(.*)#(.+)", src):
                score = 1
            elif re.match(r"http(.*)", src):
                score = 0.75
            elif src.startswith('Q'):
                print('\tGetting metadata of item: ', src)
                if self._ask_wikidata(RQSS_QUERIES['is_item_internal_source_wikidata'].format(src)) == 'true':
                    continue
                elif self._ask_wikidata(RQSS_QUERIES['is_item_online_available_dataset_wikidata'].format(src)) == 'true':
                    score = 0.5
                else:
                    score = 0.25
            self.results.append(ExternalSourceHandyScore(src, score))

        return self.results

    def _ask_wikidata(self, query: str):
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        value = None
        try:
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value = result["to_ret"]["value"]
        except Exception as e:
            print('\t\t ERROR: ', e)
        finally:
            return value

    @property
    def score(self):
        if self.results is not None:
            return sum([i.handy_score for i in self.results])/len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of external sources,num of urls with anchor,num of urls (without anchor),num of online-available,num of offline sources,score
{0},{1},{2},{3},{4},{5}""".format(
            len(self.results),
            len([i for i in self.results if i.handy_score == 1]),
            len([i for i in self.results if i.handy_score == 0.75]),
            len([i for i in self.results if i.handy_score == 0.5]),
            len([i for i in self.results if i.handy_score == 0.25]),
            self.score)

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
