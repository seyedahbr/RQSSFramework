import datetime
import re
import time
from random import randint
from typing import Iterator, List, NamedTuple

import requests
from fake_useragent import UserAgent
from lxml import html
from rdflib import URIRef


class FreshnessOfURI(NamedTuple):
    uri: URIRef
    freshness_last_modif: float = None
    freshness_google_cache: float = None
    _NONE = '<None>'

    def __repr__(self):
        return "URI:{0:40}, freshness from lastModified tag:{1}; freshness from Google Cache:{2}".format(self.uri, self.freshness_last_modif, self.freshness_google_cache)


class ExternalURIsFreshnessChecker:
    _uris = []
    _base_time: datetime.datetime
    _extract_google_cache: bool
    results: List[FreshnessOfURI] = None

    def __init__(self, uris: Iterator[URIRef], base_time: datetime.datetime = datetime.datetime(2012, 10, 29), extract_google_cache: bool = False):
        self._uris = list(dict.fromkeys(uris))  # remove duplications
        self._base_time = base_time
        self._extract_google_cache = extract_google_cache

    def check_external_uris_freshness(self) -> List[FreshnessOfURI]:
        self.results = []
        t_now = datetime.datetime.now()
        t_base = (t_now - self._base_time).total_seconds()
        for uri in self._uris:
            last_modif_freshness = None
            google_cache_freshness = None

            last_modif_time = self.get_last_modified_tag(uri)
            if last_modif_time != None:
                last_modif_freshness = (
                    t_now - last_modif_time).total_seconds()/t_base
            if self._extract_google_cache:
                google_cache_time = self.get_google_cache_last_indexed(uri)
                if google_cache_time != None:
                    google_cache_freshness = (
                        t_now - google_cache_time).total_seconds()/t_base
            self.results.append(FreshnessOfURI(
                uri, last_modif_freshness, google_cache_freshness))

        return self.results

    def get_last_modified_tag(self, uri: URIRef) -> datetime.datetime:
        try:
            response = requests.head(uri)
        except:
            return None
        if response.headers.get('Last-Modified') != None:
            ret_date_str = response.headers.get('Last-Modified')
            return datetime.datetime.strptime(ret_date_str, '%a, %d %b %Y %H:%M:%S %Z')
        return None

    def get_google_cache_last_indexed(self, uri: URIRef) -> datetime.datetime:
        query_str = 'https://google.com/search?q=cache:{}'
        xpath_str = '/html/body/div[1]/div[1]/span[2]/text()'
        datetime_regex = '[0-9]{1,2}\s[a-zA-z]{3}\s[0-9]{4}\s[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}\sGMT'
        uri = uri.replace('https://', '')
        uri = uri.replace('http://', '')
        ua = UserAgent()
        header = {"user-agent": ua.chrome}
        response = requests.get(query_str.format(uri), headers=header)
        print('External URI: {0}; Google Cache query response code: {1}'.format(
            uri, response.status_code))
        if response.status_code == 200:
            tree = html.fromstring(response.content)
            cache_div = tree.xpath(xpath_str)
            getcache = re.search(datetime_regex, str(cache_div))
            ret_date_str = getcache.group(0)
            delay = randint(1, 6)
            time.sleep(delay)
            return datetime.datetime.strptime(ret_date_str, '%d %b %Y %H:%M:%S %Z')
        return None

    @property
    def last_modif_score(self):
        if self.results != None:
            scored_list = [
                i.freshness_last_modif for i in self.results if i.freshness_last_modif != None]
            return sum(scored_list)/len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    @property
    def google_cache_score(self):
        if self.results != None:
            scored_list = [
                i.freshness_google_cache for i in self.results if i.freshness_google_cache != None]
            return sum(scored_list)/len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    @property
    def num_last_modif_tag(self):
        if self.results != None:        
            scored_list = [
                i.freshness_last_modif for i in self.results if i.freshness_last_modif != None]
            return len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    @property
    def num_google_cache(self):
        if self.results != None:
            scored_list = [
                i.freshness_google_cache for i in self.results if i.freshness_google_cache != None]
            return len(scored_list) if len(scored_list) > 0 else '<None>'
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of uris, last modif score, google cache score, num of uris with last modif, num of uris with google cache
{0},{1},{2},{3},{4}""".format(len(self.results), self.last_modif_score, self.google_cache_score, self.num_last_modif_tag, self.num_google_cache)

    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print(str(r))
