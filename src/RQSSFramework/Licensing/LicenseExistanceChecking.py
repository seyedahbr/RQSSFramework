from typing import Iterator, List, NamedTuple
from urllib.parse import urlparse

import requests
from rdflib import URIRef


class LicExistOfDom(NamedTuple):
    domain: URIRef
    license: bool

known_licensed_domains=[
    'wikidata.org',
    'wikimediafoundation.org',
    'wikipedia.org',
    'uniprot.org'
]

# covering most popular license terms according to 
# https://www.synopsys.com/blogs/software-security/top-open-source-licenses/
licensing_keywords=[
    'link rel="license"',
    'creativecommons.org/licenses',
    'creativecommons',
    'creative commons',
    'licenses/eupl',
    'european union public license',
    'licenses/mit',
    'mit-license',
    'mit license',
    'gnu.org/licenses',
    'gnu general public license',
    'gnu lesser general public license',
    'gnu affero general public license',
    'gnu free documentation license',
    'apache.org/licenses',
    'apache license',
    'licenses/bsd',
    'bsd license',
    'isc.org/licenses',
    'isc license',
    'perl.org/licenses',
    'artistic license',
    'eclipse.org/legal',
    'eclipse public license',
    'licenses/ms-pl',
    'microsoft public license',
    'codeproject.com/info/cpol',
    'code project open license',
    'mozilla.org/en-us/mpl',
    'mozilla public license',
    'licenses/cddl',
    'common development and distribution license',
    'licenses/ms-rl',
    'microsoft reciprocal license',
    'openjdk.java.net/legal',
    'sun gpl with classpath',
    'zlib/libpng license',
    'licenses/zlib',
    'antlr.org/license',
    'antlr license',
    'boost.org/users/license',
    'boost software license',
    'spdx.org/licenses',
    'icu license',
    'infozip.sourceforge.net/license',
    'info-zip license',
    'jaxen license',
    'licenses/cpal',
    'common public attribution license',
    'licenses/cpl',
    'common public license',
    'licenses/ipl',
    'iBM public license',
    'mozilla.org/mpl',
    'mozilla public license',
    
]

class LicenseChecker:
    _domains=[]
    results=None
    def __init__(self, uris: Iterator[URIRef]):
        _uris = list(dict.fromkeys(uris)) # remove duplicated URIs
        self._domains = list(dict.fromkeys(self.domain_extractor(_uris))) # compute and remove duplicated domains
    
    def domain_extractor(uris: Iterator[URIRef]) -> List[URIRef]:
        ret_list=[]
        for u in uris:
            ret_list.append(urlparse(u).netloc)
        return ret_list

    def check_license_existance(self) -> List[LicExistOfDom]:
        """
        check the accssessibility of each URI in the class
        """
        self.results=[]
        for u in self._domains:
            try:
                if u.lower() in known_licensed_domains:
                    self.results.append(LicExistOfDom(u,True))
                    continue
                r = requests.get(u)
                if (r.status_code == 200 and self.html_contains_license(r.text.lower())):
                    self.results.append(LicExistOfDom(u,True))
                else:
                    self.results.append(LicExistOfDom(u,False))
            except Exception as e:
                print(e)
        return self.results
    
    def html_contains_license(html: str):
        return any(licensing_keyword in html for licensing_keyword in licensing_keywords)
                
    def print_results(self):
        """
        print self.results if it is already computed
        """
        if self.results == None:
            print('Results are not computed')
            return
        for r in self.results:
            print("Domain:{0}, License Existed:{1}".format(r.domain, r.license))
