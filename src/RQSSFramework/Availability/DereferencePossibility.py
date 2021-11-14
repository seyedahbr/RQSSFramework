import requests
from typing import Tuple, List, Iterator, NamedTuple
from rdflib import URIRef

class DerefOfURI(NamedTuple):
    uri: URIRef
    deref: bool
    
def check_dereferencies(uris: List[URIRef]) -> List[DerefOfURI]:
    """
    check the accssessibility of each URI in the class
    """
    results=[]
    for u in uris:
        try:
            r = requests.get(u)
            if r.status_code == 200:
                results.append(DerefOfURI(u,True))
            else:
                results.append(DerefOfURI(u,False))
        except Exception as e:
            print(e)
    return results
            
def print_results(results: List[DerefOfURI]):
    """
    print results of a computed dereferenced checking 
    """
    for r in results:
        print("URI : {0}, Deref : {1}".format(r.uri,r.deref))