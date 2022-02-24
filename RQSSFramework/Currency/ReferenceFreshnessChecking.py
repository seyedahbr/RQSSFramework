import datetime
from typing import Dict, List, NamedTuple

import requests
from lxml import html


class ReferenceFreshnessResult(NamedTuple):
    item: str
    total: int
    freshness: float
    not_found: int

    def __repr__(self):
        return "Number of referenced facts in item {0}: {1}; not found facts:{2}; freshness of references: {3}".format(self.item, self.total, self.not_found, self.freshness)


class ReferenceFreshnessInItemChecker:
    results: List[ReferenceFreshnessResult] = None
    # because of the nature of the metric (average of ratios) we compute
    # keep a total average of entire dataset (beside the average of self.results) 
    num_checked_facts = None
    total_freshness = None
    _item_refed_facts: Dict
    _upper_time_limit: datetime.datetime

    def __init__(self, item_referenced_facts: Dict, upper_time_limit:datetime.datetime) -> None:
        self._item_refed_facts = item_referenced_facts
        self._upper_time_limit = upper_time_limit

    def check_referenced_facts_freshness(self) -> List[ReferenceFreshnessResult]:
        self.results = []
        t_now = datetime.datetime.now()
        xpath_create='//*[@id="pagehistory"]/ul/li[./span/span/span/text()="Created claim: " and ./span/a/span/span/text()="({})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        xpath_add='//*[@id="pagehistory"]/ul/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        xpath_change='//*[@id="pagehistory"]/ul/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({})"]/a[contains(@class,\'mw-changeslist-date\')]/text()'
        self.num_checked_facts = 0
        self.total_freshness = 0
        for item in self._item_refed_facts.keys():
            not_found_facts = 0
            print('getting history of item: {0}'.format(str(item)))
            page = requests.get('https://www.wikidata.org/w/index.php?title={}&offset=&limit=5000&action=history'.format(str(item)))
            tree = html.fromstring(page.content)
            prop_ctr = 0
            prop_total_freshness = 0
            for prop in self._item_refed_facts[str(item)]:
                fact_created_time = tree.xpath(xpath_create.format(str(prop)))
                revisions_added_time = tree.xpath(xpath_add.format(str(prop)))
                revisions_changed_times = tree.xpath(xpath_change.format(str(prop)))
                # the earlies creation time is neaded
                fact_created_time = self.remove_upper_than_base_time(sorted([datetime.datetime.strptime(i,'%H:%M, %d %B %Y') for i in fact_created_time]))
                # the latest reference addition/change time is needed 
                revisions_added_time = self.remove_upper_than_base_time(sorted([datetime.datetime.strptime(i,'%H:%M, %d %B %Y') for i in revisions_added_time], reverse=True))
                revisions_changed_times = self.remove_upper_than_base_time(sorted([datetime.datetime.strptime(i,'%H:%M, %d %B %Y') for i in revisions_changed_times], reverse=True))
                if not fact_created_time or (not revisions_added_time and not revisions_changed_times):
                    print('\t fact {0} : found NO historical info'.format(prop))
                    not_found_facts += 1
                    continue
                t_base = fact_created_time[0]
                t_modif = revisions_changed_times[0] if revisions_changed_times else revisions_added_time[0]
                print('\t fact {0} : Ref Freshness = {1}'.format(prop,(t_now-t_modif).total_seconds()/(t_now-t_base).total_seconds()))
                prop_total_freshness += (t_now-t_modif).total_seconds()/(t_now-t_base).total_seconds()
                prop_ctr += 1
            if prop_ctr:    
                self.num_checked_facts += prop_ctr
                self.total_freshness += prop_total_freshness
            
            self.results.append(ReferenceFreshnessResult(str(item),prop_ctr,prop_total_freshness/prop_ctr if prop_ctr > 0 else 1.0,not_found_facts))
        return self.results, self.num_checked_facts, self.total_freshness/self.num_checked_facts

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
        return self.total_freshness/self.num_checked_facts if self.num_checked_facts > 0 else 1
    
    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'            
        return """num of items,num of checked referenced facts,num of not found,score
{0},{1},{2},{3}""".format(len(self.results),self.num_checked_facts,sum([i.not_found for i in self.results]),self.score)
