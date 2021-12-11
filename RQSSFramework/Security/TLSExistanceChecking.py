from typing import Iterator, List, NamedTuple

import requests
from rdflib import URIRef


class TLSExist(NamedTuple):
    uri: URIRef
    support: bool

class TLSChecker:
    _uris=[]
    results=None
    def __init__(self, uris: Iterator[URIRef]):
        _tmp_uri = list(dict.fromkeys(uris)) # remove duplicated URIs
        for u in _tmp_uri:
            self._uris.append(u.replace('http://','https://')) # deliberately change all URIs to HTTPS to check support for TLS.
    
    def check_support_tls(self) -> List[TLSExist]:
        """
        check the accssessibility of https:// for each URI in the class
        """
        self.results=[]
        for u in self._uris:
            try:
                r = requests.get(u, verify=True)
                if (r.status_code == 200):
                    self.results.append(TLSExist(u,True))
                else:
                    self.results.append(TLSExist(u,False))
            except Exception as e:
                self.results.append(TLSExist(u,False))
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
            print("URI:{0:85}, TLS:{1}".format(r.uri, r.support))
