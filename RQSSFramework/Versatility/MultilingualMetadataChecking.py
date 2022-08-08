import sys
from typing import List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class MultilingualMetadataResult(NamedTuple):
    property: str
    num_non_en_label: int
    num_non_en_comment: int

    def __repr__(self):
        return "Property {0} has {1} non-English labels and {2} non-English comments".format(
            self.property,
            self.num_non_en_label,
            self.num_non_en_comment)


class MultilingualMetadataChecker:
    results: List[MultilingualMetadataResult] = None
    _ref_properties: List[str]

    def __init__(self, ref_properties: List[str]):
        self._ref_properties = ref_properties

    def check_multilingual_existance_from_Wikdiata(self) -> List[MultilingualMetadataResult]:
        self.results = []
        user_agent = "RQSSFramework Python/%s.%s" % (
            sys.version_info[0], sys.version_info[1])
        sparql = SPARQLWrapper(
            "https://query.wikidata.org/sparql", agent=user_agent)
        for prop in self._ref_properties:
            print('\t Getting number of non-English labels of reference property: ', prop)
            sparql.setQuery(
                RQSS_QUERIES['get_property_non_en_labels_wikidata'].format(prop))
            sparql.setReturnFormat(JSON)
            try:
                results = sparql.query().convert()
                for result in results["results"]["bindings"]:
                    value = result["to_ret"]["value"]
                    if value.isdigit():
                        num_non_en_labels = int(value)
                    else:
                        num_non_en_labels = 0
            except Exception as e:
                print('\t\t ERROR: ', e)
                continue
            print('\t Getting number of non-English comments of reference property: ', prop)
            sparql.setQuery(
                RQSS_QUERIES['get_property_non_en_comments_wikidata'].format(prop))
            sparql.setReturnFormat(JSON)
            try:
                results = sparql.query().convert()
                for result in results["results"]["bindings"]:
                    value = result["to_ret"]["value"]
                    if value.isdigit():
                        num_non_en_comments = int(value)
                    else:
                        num_non_en_comments = 0
            except Exception as e:
                print('\t\t ERROR: ', e)
                continue
            self.results.append(MultilingualMetadataResult(
                prop, num_non_en_labels, num_non_en_comments))
        return self.results

    @property
    def multilingual_labeling_score(self):
        if self.results is not None:
            return len([i for i in self.results if i.num_non_en_label > 0])/len(self.results) if len(self.results) > 0 else 1
        return None

    @property
    def multilingual_commenting_score(self):
        if self.results is not None:
            return len([i for i in self.results if i.num_non_en_comment > 0])/len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results is None:
            return 'Results are not computed'
        return """num of properties,multilingual labeling score,multilingual commenting score
{0},{1},{2}""".format(
            len(self.results),
            self.multilingual_labeling_score,
            self.multilingual_commenting_score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results is None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
