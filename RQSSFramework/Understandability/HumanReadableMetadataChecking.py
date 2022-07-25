import sys
from typing import List, NamedTuple

from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper


class HumanReadableMetadataResult(NamedTuple):
    property: str
    num_label: int
    num_comment: int

    def __repr__(self):
        return "Property {0} has {1} labels and {2} comments".format(
            self.property,
            self.num_label,
            self.num_comment)


class HumanReadableMetadataChecker:
    results: List[HumanReadableMetadataResult] = None
    _ref_properties: List[str]

    def __init__(self, ref_properties: List[str]):
        self._ref_properties = ref_properties

    def check_labels_comments_existance_from_Wikdiata(self) -> List[HumanReadableMetadataResult]:
        self.results = []
        # TODO
        return self.results

    @property
    def human_readable_labeling_score(self):
        if self.results is not None:
            return len([i for i in self.results if i.num_label > 0])/len(self.results) if len(self.results) > 0 else 1
        return None

    @property
    def human_readable_commenting_score(self):
        if self.results is not None:
            return len([i for i in self.results if i.num_comment > 0])/len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results is None:
            return 'Results are not computed'
        return """num of properties,human-readable labeling score,human-readable commenting score
{0},{1},{2},{3}""".format(
            len(self.results),
            self.human_readable_labeling_score,
            self.human_readable_commenting_score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results is None:
            print('Results are not computed')
            return
        for r in self.results:
            print(r)
