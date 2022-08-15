import sys
from typing import Dict, List, NamedTuple, Tuple

import requests
from lxml import html
from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class MultilingualSourceResult(NamedTuple):
    source: str
    lang: str

    def __repr__(self):
        return "Language of source {0}: {1}".format(self.source, self.lang)


class MultilingualFactResult(NamedTuple):
    statement_id: str
    num_non_en_refs: int

    def __repr__(self):
        return "Number of non-English sources of stateemnt {0}: {1}".format(self.statement_id, self.num_non_en_refs)


class MultilingualFactsAndSourcesChecker:
    results_sources: List[MultilingualSourceResult] = None
    results_facts: List[MultilingualFactResult] = None
    _statements_sources: Dict

    def __init__(self, statements_sources: Dict):
        self._statements_sources = statements_sources

    def _get_distinct_sources_empty_dict(self) -> Dict:
        distinct_sources = set.union(
            *[set(value) for key, value in self._statements_sources.items()])
        ret_val = Dict.fromkeys(distinct_sources)
        ret_val = {key: [] for key in ret_val}
        return ret_val

    def _extract_lang(self, src: str) -> List[str]:
        if src.startswith('Q'):
            return self._ask_wikidata(RQSS_QUERIES['get_source_languages_code_wikidata'].format(src))
        else:
            return self._extract_html_lang_attribute(src)

    def _ask_wikidata(self, query: str) -> List[str]:
        ret_val = []
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
                ret_val.append(value)
        except Exception as e:
            print('\t\t ERROR: ', e)
        finally:
            return ret_val

    def _extract_html_lang_attribute(self, url: str) -> List[str]:
        try:
            page = requests.get(url, timeout=(10, 60))
            tree = html.fromstring(page.content)
            return tree.xpath('/html/@lang')
        except:
            print('FAILED: getting HTML content of: {0}'.format(url))
            return []

    def check_fact_sources_multilingualism(self) -> Tuple[List[MultilingualSourceResult], List[MultilingualFactResult]]:
        self.results_sources = []
        self.results_facts = []
        print('Getting distinct internal/external sources ...')
        distinct_sources = self._get_distinct_sources_empty_dict()
        ctr = 0
        all = len(distinct_sources.keys())
        print(
            'Starts extracting language of {0} external/internal sources:'.format(all))
        for key, value in distinct_sources.items():
            [value.append(i)
             for i in self._extract_lang(key) if i not in value]
            ctr += 1
            if ctr % 5000 == 0:
                print('\t{0} of {1} extracted'.format(ctr, all))
        for key, value in distinct_sources.items():
            self.results_sources.append(MultilingualSourceResult(key, None)) if not value else [
                self.results_sources.append(MultilingualSourceResult(key, lang)) for lang in value]
        print('Language extraction done')
        ctr = 0
        all = len(self._statements_sources.keys())
        print('Starts computing {0} facts multilingualism:'.format(all))
        for key, value in self._statements_sources.items():
            non_en_langs = set()
            for refs in value:
                [non_en_langs.add(i) for i in distinct_sources[refs]]
            num_non_en_langs = len([i for i in non_en_langs if 'en' not in i])
            self.results_facts.append(
                MultilingualFactResult(key, num_non_en_langs))
            ctr += 1
            if ctr % 5000 == 0:
                print('\t{0} of {1} computed'.format(ctr, all))

        return self.results_sources, self.results_facts

    @property
    def multilingual_sources_score(self):
        if self.results_sources is not None:
            distinct_sources_found = set()
            [distinct_sources_found.add(
                i) for i in self.results_sources if i.lang is not None]
            distinct_non_eng_sources = set()
            [distinct_non_eng_sources.add(
                i) for i in self.results_sources if i.lang is not None and 'en' not in i.lang]
            return len(distinct_non_eng_sources)/len(distinct_sources_found) if len(distinct_sources_found) > 0 else 1
        return None

    @property
    def multilingual_referenced_facts_score(self):
        if self.results_facts is not None:
            return len([i for i in self.results_facts if i.num_non_en_refs > 0])/len(self.results_facts) if len(self.results_facts) > 0 else 1
        return None

    def __repr__(self):
        if self.results_sources is None or self.results_facts is None:
            return 'Results are not computed'
        distinct_sources = set()
        [distinct_sources.add(i) for i in self.results_sources]
        distinct_sources_not_found = set()
        [distinct_sources_not_found.add(
            i) for i in self.results_sources if i.lang is None]
        distinct_non_eng_sources = set()
        [distinct_non_eng_sources.add(
            i) for i in self.results_sources if i.lang is not None and 'en' not in i.lang]
        return """num of internal/external sources,num of non-English sources,num of not found language of source,num of referenced statements (internal/external sources),num of referenced statements with non-English sources,multilingual sources score,multilingual referenced facts score
{0},{1},{2},{3},{4},{5},{6}""".format(
            len(distinct_sources),
            len(distinct_non_eng_sources),
            len(distinct_sources_not_found),
            len(self._statements_sources),
            len([i for i in self.results_facts if i.num_non_en_refs > 0]),
            self.multilingual_sources_score,
            self.multilingual_referenced_facts_score
        )
