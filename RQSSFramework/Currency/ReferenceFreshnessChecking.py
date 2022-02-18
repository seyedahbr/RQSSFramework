import datetime
from typing import Dict, List, NamedTuple

import requests
from lxml import html


class ReferenceFreshnessResult(NamedTuple):
    item: str
    total: int
    freshness: float

    def __repr__(self):
        return "Number of referenced facts in item {0}: {1}; freshness of references: {2}".format(self.item, self.total, self.freshness)


class ReferenceFreshnessInItemChecker:
    results: List[ReferenceFreshnessResult] = None
    _item_refed_facts: Dict
    _upper_time_limit: datetime.datetime

    def __init__(self, item_referenced_facts: Dict) -> None:
        self._item_refed_facts = item_referenced_facts

    def check_referenced_facts_freshness(self) -> List[ReferenceFreshnessResult]:
        t_now = datetime.datetime.now()
        xpath_create='//*[@id="pagehistory"]/li[./span/span/span/text()="Created claim: " and ./span/a/span/span/text()="({})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        xpath_add='//*[@id="pagehistory"]/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        xpath_change='//*[@id="pagehistory"]/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        item_ctr = 0
        item_total_freshness = 0
        for item in self._item_refed_facts.keys():
            print('for item: {0}'.format(str(item)))
            page = requests.get('https://www.wikidata.org/w/index.php?title={}&offset=&limit=5000&action=history'.format(str(item)))
            tree = html.fromstring(page.content)
            prop_ctr = 0
            prop_total_freshness = 0
            for prop in self._item_refed_facts[str(item)]:
                fact_created_time = tree.xpath(xpath_create.format(str(prop)))
                revisions_added_time = tree.xpath(xpath_add.format(str(prop)))
                revisions_chaned_times = tree.xpath(xpath_change.format(str(prop)))
                # the earlies creation time is neaded
                fact_created_time = self.remove_upper_than_base_time(sorted([datetime.datetime.strptime(i,'%H:%M, %d %B %Y') for i in fact_created_time]))
                # the latest reference addition/change time is needed 
                revisions_added_time = self.remove_upper_than_base_time(sorted([datetime.datetime.strptime(i,'%H:%M, %d %B %Y') for i in revisions_added_time], reverse=True))
                revisions_chaned_times = self.remove_upper_than_base_time(sorted([datetime.datetime.strptime(i,'%H:%M, %d %B %Y') for i in revisions_chaned_times], reverse=True))
                if not fact_created_time or (not revisions_added_time and not revisions_chaned_times):
                    print('Empty')
                    continue
                t_base = fact_created_time[0]
                t_modif = revisions_chaned_times[0] if revisions_chaned_times else revisions_added_time[0]
                prop_total_freshness += (t_now-t_modif).total_seconds()/(t_now-t_base).total_seconds()
                prop_ctr += 1
                
            item_ctr += prop_ctr
            item_total_freshness += prop_total_freshness
            self.results.append(ReferenceFreshnessResult(str(item),prop_ctr,prop_total_freshness/prop_ctr))
            
        return self.results, item_ctr, item_total_freshness

    def remove_upper_than_base_time(self, times: List[datetime.datetime]) -> List[datetime.datetime]:
        return [i for i in times if i <= self._upper_time_limit]

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for result in self.results:
            print(result)

    @property
    def score(self):
        return sum([x.freshness for x in self.results])/len(self.results)
    
    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'            
        return """num of items, num of referenced facts, score
{0},{1},{2}""".format(len(self.results),sum([x.total for x in self.results]),self.score)
