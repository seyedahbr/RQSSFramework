import sys
from typing import Iterator, List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class SourceVerifiabilityScore(NamedTuple):
    source: str
    verifiability_score: float = None

    def __repr__(self):
        return "source:{0:40}, verifiability score:{1}".format(self.source, self.verifiability_score)


class TypeOfSourcesChecker:
    _sources = List[str]
    _known_datasets_keywords = List[str]
    results: List[SourceVerifiabilityScore] = None

    def __init__(self, sources: Iterator[str], known_datasets_keywords: List[str] = []):
        self._sources = list(sources)
        self._known_datasets_keywords = known_datasets_keywords

    def check_type_of_sources_wikidata(self) -> List[SourceVerifiabilityScore]:
        self.results = []
        for src in self._sources:
            score = 0
            if src.startswith('http'):
                for key in self._known_datasets_keywords:
                    if key in src:
                        score = 0.75
                        break
            elif src.startswith('Q'):
                print('\tGetting type of item: ', src)
                instances = self._ask_wikidata(
                    RQSS_QUERIES['get_instances_wikidata'].format(src))
                if 'Q13442814' in instances:
                    score = 1
                elif 'Q8513' in instances:
                    score = 0.75
                elif any(i in ['Q571', 'Q5292', 'Q13433827'] for i in instances):
                    score = 0.5
                elif any(i in ['Q41298', 'Q30849', 'Q17928402'] for i in instances):
                    score = 0.25
            self.results.append(SourceVerifiabilityScore(src, score))

        return self.results

    def _ask_wikidata(self, query: str):
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        values = []
        try:
            results = sparql.query().convert()
            for result in results["results"]["bindings"]:
                value = result["to_ret"]["value"]
                values.append(value)
        except Exception as e:
            print('\t\t ERROR: ', e)
        finally:
            return values

    @property
    def score(self):
        if self.results is not None:
            return sum([i.verifiability_score for i in self.results])/len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results is None:
            return 'Results are not computed'
        return """num of sources,num of scholarly articles,num of well-known datasets,num of book or encyclopedia or encyclopedic article,num of magazine or blog or blog post,score
{0},{1},{2},{3},{4},{5}""".format(
            len(self.results),
            len([i for i in self.results if i.verifiability_score == 1]),
            len([i for i in self.results if i.verifiability_score == 0.75]),
            len([i for i in self.results if i.verifiability_score == 0.5]),
            len([i for i in self.results if i.verifiability_score == 0.25]),
            self.score)

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results is None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
