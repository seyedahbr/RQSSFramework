from typing import Iterator, List, NamedTuple

import requests
from rdflib import URIRef


class DerefOfURI(NamedTuple):
    uri: URIRef
    deref: bool
    
class DerefrenceExplorer:
    _uris=[]
    results=None
    def __init__(self, uris: Iterator[URIRef]):
        self._uris = list(dict.fromkeys(uris)) # remove duplications
    
    def check_dereferencies(self) -> List[DerefOfURI]:
        """
        check the accssessibility of each URI in the class
        """
        self.results=[]
        for u in self._uris:
            try:
                r = requests.get(u)
                if r.status_code == 200:
                    self.results.append(DerefOfURI(u,True))
                else:
                    self.results.append(DerefOfURI(u,False))
            except Exception as e:
                print(e)
        return self.results
                
    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print("URI:{0:40}, Deref:{1}".format(r.uri,r.deref))
