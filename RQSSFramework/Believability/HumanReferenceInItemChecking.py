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

    def __init__(self, item_referenced_facts: Dict) -> None:
        self._item_refed_facts = item_referenced_facts

    def check_referenced_facts_human_added(self) -> List[HumanAddedResult]:
        self.results = []
        for item in self._item_refed_facts.keys():
            num_human_added = 0
            history_page = requests.get('https://www.wikidata.org/w/index.php?title={}&offset=&limit=5000&action=history'.format(str(item)))
            tree = html.fromstring(history_page.content)
            for prop in self._item_refed_facts[str(item)]:
                revisions_adder = tree.xpath('//*[@id="pagehistory"]/li[./span/span/span/text()="Added reference to claim: " and ./span/a/span/span/text()="({})"]/span[@class="history-user"]/a/bdi/text()'.format(prop))
                revisions_chanr = tree.xpath('//*[@id="pagehistory"]/li[./span/span/span/text()="Changed reference of claim: " and ./span/a/span/span/text()="({})"]/span[@class="history-user"]/a/bdi/text()'.format(prop))
                revisions_adder.extend(revisions_chanr)
                for editor in revisions_adder:
                    if 'bot' not in editor.lower():
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