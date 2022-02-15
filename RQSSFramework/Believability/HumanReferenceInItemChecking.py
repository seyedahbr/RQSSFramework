import datetime
from typing import Dict, List, NamedTuple

import requests
from lxml import html


class HumanAddedResult(NamedTuple):
    item: str
    total: int
    human_added: int

    def __repr__(self):
        return "Number of references in item {0}: {1}; human_added references:{2}; score: {3}".format(self.item, self.total, self.human_added, self.score)

    @property
    def score(self):
        return self.human_added/self.total


class HumanReferenceInItemChecker:
    results: List[HumanAddedResult] = None
    _item_refed_facts: Dict
    _upper_time_limit: datetime.datetime

    def __init__(self, item_referenced_facts: Dict, upper_time_limit:datetime.datetime) -> None:
        self._item_refed_facts = item_referenced_facts
        self._upper_time_limit = upper_time_limit

    def check_referenced_facts_human_added(self) -> List[HumanAddedResult]:
        self.results = []
        for item in self._item_refed_facts.keys():
            num_human_added = 0
            history_page = requests.get('https://www.wikidata.org/w/index.php?title={}&offset=&limit=5000&action=history'.format(str(item)))
            tree = html.fromstring(history_page.content)
            for prop in self._item_refed_facts[str(item)]:
                xpath_1='//*[@id="pagehistory"]/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({0})"]/span[@class="history-user"]/a/bdi/text() | //*[@id="pagehistory"]/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({1})"]/a[@class="mw-changeslist-date"]/text()'.format(str(prop),str(prop))
                xpath_2='//*[@id="pagehistory"]/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({0})"]/span[@class="history-user"]/a/bdi/text() | //*[@id="pagehistory"]/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({1})"]/a[@class="mw-changeslist-date"]/text()'.format(str(prop),str(prop))
                revisions_adder = tree.xpath(xpath_1)
                revisions_chanr = tree.xpath(xpath_2)
                revisions_adder.extend(revisions_chanr)
                it = iter(revisions_adder)
                editor_time_pairs= [(i,next(it)) for i in it]
                for pair in editor_time_pairs:
                    pair_date = pair[0]
                    pair_editor = pair[1]
                    pair_date_datetime = None
                    try:
                        pair_date_datetime = datetime.datetime.strptime(pair_date,'%H:%M, %d %B %Y')
                    except:
                        pair_date = pair[1]
                        pair_editor = pair[0]
                        pair_date_datetime = datetime.datetime.strptime(pair_date,'%H:%M, %d %B %Y')
                    if pair_date_datetime > self._upper_time_limit:
                        print ('time is higer than till in pair:',pair)
                        continue
                    if 'bot' not in pair_editor.lower():
                        print('MATCH!! in pair:', pair)
                        num_human_added += 1
                        break
                    
            self.results.append(HumanAddedResult(str(item),len(self._item_refed_facts[str(item)]),num_human_added))
        return self.results

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
        return sum([x.score for x in self.results])/len(self.results)
    
    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'            
        return """num of items, num of referenced facts, score
{0},{1},{2}""".format(len(self.results),sum([x.total for x in self.results]),self.score)
