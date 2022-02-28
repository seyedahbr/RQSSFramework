import datetime
from typing import Dict, List, NamedTuple, Tuple
from urllib import response

import requests
from lxml import html


class HumanAddedResult(NamedTuple):
    item: str
    total: int
    human_added: int
    not_found: int      # numbers that historical info was found for them

    def __repr__(self):
        return "Number of references in item {0}: {1}; human_added references:{2}; Not found facts: {3};score: {4}".format(self.item, self.total, self.human_added, self.not_found, self.score)

    @property
    def score(self):
        return self.human_added/self.total


class HumanReferenceInItemChecker:
    results: List[HumanAddedResult] = None
    _item_refed_facts: Dict
    _upper_time_limit: datetime.datetime

    def __init__(self, item_referenced_facts: Dict, upper_time_limit: datetime.datetime) -> None:
        self._item_refed_facts = item_referenced_facts
        self._upper_time_limit = upper_time_limit

    def check_referenced_facts_human_added(self) -> List[HumanAddedResult]:
        self.results = []
        wikidata_item_history_url = 'https://www.wikidata.org/w/index.php?title={}&offset=&limit=5000&action=history'
        xpath_added = '//*[@id="pagehistory"]/ul/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({0})"]/span[@class="history-user"]/a/bdi/text() | //*[@id="pagehistory"]/ul/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({1})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        xpath_changed = '//*[@id="pagehistory"]/ul/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({0})"]/span[@class="history-user"]/a/bdi/text() | //*[@id="pagehistory"]/ul/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({1})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        for item in self._item_refed_facts.keys():
            print('getting history of item: {0}'.format(str(item)))
            num_not_found = 0
            num_human_added = 0
            try:
                history_page = requests.get(
                    wikidata_item_history_url.format(str(item)))
            except:
                print('FAILED: getting history of item: {0}'.format(str(item)))
                self.results.append(HumanAddedResult(str(item), len(self._item_refed_facts[str(item)]), 0, 0))
                continue
            tree = html.fromstring(history_page.content)
            for prop in self._item_refed_facts[str(item)]:
                # we get both added and edited times, combine them,
                # then will pick up the latest time/user pair
                revisions_adder = tree.xpath(
                    xpath_added.format(str(prop), str(prop)))
                revisions_chanr = tree.xpath(
                    xpath_changed.format(str(prop), str(prop)))
                revisions_adder.extend(revisions_chanr)
                it = iter(revisions_adder)
                editor_time_pairs = [(i, next(it)) for i in it]
                editor_time_pairs = self.remove_upper_than_base_time_sort(
                    editor_time_pairs)
                if not editor_time_pairs:
                    print(
                        '\t fact {0} : found NO historical info'.format(prop))
                    num_not_found += 1
                    continue
                if 'bot' not in editor_time_pairs[0][1].lower():
                    print(
                        '\t fact {0} : latest edited by a human account'.format(prop))
                    num_human_added += 1
            self.results.append(HumanAddedResult(str(item), len(
                self._item_refed_facts[str(item)]), num_human_added, num_not_found))
        return self.results

    def remove_upper_than_base_time_sort(self, tuples: List[Tuple[datetime.datetime, str]]) -> List[Tuple[datetime.datetime, str]]:
        ret_val = []
        for pair in tuples:
            # error handler in case of date/user pair be user/pair !!
            try:
                pair_date_datetime = datetime.datetime.strptime(
                    pair[0], '%H:%M, %d %B %Y')
                if pair_date_datetime <= self._upper_time_limit:
                    ret_val.append((pair_date_datetime, pair[1]))
            except:
                pair_date_datetime = datetime.datetime.strptime(
                    pair[1], '%H:%M, %d %B %Y')
                if pair_date_datetime <= self._upper_time_limit:
                    ret_val.append((pair_date_datetime, pair[0]))
        return sorted(ret_val, key=lambda a: a[0], reverse=True)

    @property
    def score(self):
        total_found = sum([x.total - x.not_found for x in self.results])
        total_human_added = sum([x.human_added for x in self.results])
        return total_human_added/total_found if total_found > 0 else 1

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of items,num of referenced facts,num of human-added refed facts,num of not found facts,score
{0},{1},{2},{3},{4}""".format(len(self.results),
sum([x.total for x in self.results]),
sum([x.human_added for x in self.results]),
sum([x.not_found for x in self.results]),
self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for result in self.results:
            print(result)
