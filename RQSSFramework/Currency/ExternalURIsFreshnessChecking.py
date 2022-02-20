import datetime
import re
import time
from typing import Iterator, List, NamedTuple

import numpy as np
import requests
from fake_useragent import UserAgent
from lxml import html
from rdflib import URIRef


class FreshnessOfURI(NamedTuple):
    uri: URIRef
    freshness_last_modif: float = None
    freshness_google_cache: float = None
    def __repr__(self):
        return "URI:{0:40}, freshness from lastModified tag:{1}; freshness from Google Cache:{2}".format(self.uri,self.freshness_last_modif,self.freshness_google_cache)

class ExternalURIsFreshnessChecker:
    _uris=[]
    _base_time: datetime.datetime
    num_last_modif_tag = 0
    num_google_cache = 0
    results: List[FreshnessOfURI]=None
    
    def __init__(self, uris: Iterator[URIRef], base_time: datetime.datetime = datetime.datetime(2012,10,29)):
        self._uris = list(dict.fromkeys(uris)) # remove duplications
        self._base_time = base_time
    
    def check_external_uris_freshness(self) -> List[FreshnessOfURI]:
        t_now = datetime.datetime.now()
        t_base = (t_now - self._base_time).total_seconds()
        self.num_last_modif_tag = 0
        self.num_google_cache = 0
        for uri in self._uris:
            last_modif_time = self.get_last_modified_tag(uri)
            google_cache_time = self.get_google_cache_last_indexed(uri)
            last_modif_freshness = None
            google_cache_freshness = None
            if last_modif_time != None:
                last_modif_freshness = (t_now - last_modif_time).total_seconds()/t_base
                self.num_last_modif_tag += 1
            if google_cache_time != None:
                google_cache_freshness = (t_now - google_cache_time).total_seconds/t_base
                self.num_google_cache += 1
            
            self.results.append(FreshnessOfURI(uri,last_modif_freshness,google_cache_freshness))
                
        return self.results
    
    def get_last_modified_tag(self, uri:URIRef) -> datetime.datetime:
        return None
    
    def get_google_cache_last_indexed(self, uri:URIRef) -> datetime.datetime:
        return None
    

                
    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
