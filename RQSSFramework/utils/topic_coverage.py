import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import Dict, List, Optional, Union
#from Queries import RQSS_QUERIES
from SPARQLWrapper import JSON, SPARQLWrapper

# input: Qids list of items Q-ids (rdf:type item)
# output: topic coverage pie chart (like Wikdiata statistics https://www.wikidata.org/wiki/Wikidata:Statistics)

def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument("--qids", help="Input file of items of the subset", required=True)
    parser.add_argument("--output", help="Where to save the chart", required=True)
    return parser

def main(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])
    opts.qids = Path(opts.qids)
    opts.output = Path(opts.output)
    if not opts.qids.is_file():
        print('File not existed: {0}'.format(opts.qids))
        return 1
    with open(opts.qids) as file:
        QIDs = file.read().splitlines()
    
    # keys are QIDs, values are list of classess
    print('Getting instances-subclassses of items...')
    QID_class_dict = Dict.fromkeys(QIDs)
    for q in QID_class_dict.keys():
        QID_class_dict[q] = set(get_instances_subclass_of_values_from_Wikidata(q))
    
    # test
    # print("QIDs and Classes: ", QID_class_dict)

    print('Fetching distinct classes ...')
    distinct_classes = set.union(*[set(value) for key, value in QID_class_dict.items()])
    # keys are classes values are lists of QIDS
    CLASS_QID_dict = Dict.fromkeys(distinct_classes)
    
    print('Relating each Qid into relative classes, still are not disjoint ...')
    # relating each Qid into relative classes, still are not disjoint
    for cl in CLASS_QID_dict.keys():
        CLASS_QID_dict[cl] = list()
        for q in QID_class_dict.keys():
            if cl in QID_class_dict[q]:
                CLASS_QID_dict[cl].append(q)
    
    # test
    # print("Classes and QIDs: ", CLASS_QID_dict)
    
    # sorting 
    print('Sorting classes based on frequency ...')
    CLASS_QID_dict = sorted(CLASS_QID_dict.keys(), reverse=True, key=lambda s: len(CLASS_QID_dict[s]))

    # test
    # print("Sorted classes and QIDs: ", CLASS_QID_dict)

    

def get_instances_subclass_of_values_from_Wikidata(qid) -> List:
    ret_val = []
    user_agent = "RQSSFramework Python/%s.%s" % (
        sys.version_info[0], sys.version_info[1])
    sparql = SPARQLWrapper(
        "https://query.wikidata.org/sparql", agent=user_agent)
    print('\t Getting instances or subclasses of value: ', qid)
    sparql.setQuery(
        '''SELECT DISTINCT (REPLACE(STR(?item),".*Q","Q") AS ?to_ret) WHERE{{
  {{wd:{0} wdt:P279+ ?item.}}
  UNION{{
    wd:{0} wdt:P31/wdt:279* ?item.
  }}
}}'''.format(qid))
    try:
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        for result in results["results"]["bindings"]:
            query_value = result["to_ret"]["value"]
            ret_val.append(query_value)
    except Exception as e:
        print('\t\t ERROR: ', e)
    return ret_val


if __name__ == '__main__':
    main(sys.argv[1:])