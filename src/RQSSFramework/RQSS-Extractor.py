import sys
from pathlib import Path
from argparse import ArgumentParser
from typing import Optional, Union, List
from rdflib import Graph
from rdflib.namespace import RDF, RDFS
from rdflib import Namespace

def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    group = parser.add_mutually_exclusive_group(required=True)
    #group.add_argument("--input", help="Input RDF file of the dataset")
    group.add_argument("--endpoint", help="The local/public endpoint of the dataset")
    parser.add_argument("-f", "--format", help="Input file RDF format (nt, ttl)", default='nt')
    parser.add_argument("-o", "--output_dir", help="Output destination directory to store extarcted components from the RDF input file", default='./rqss_extractor_output')
    parser.add_argument("-eExt" , "--extract_external", help="Extract all external sources (Wikibase referencing model)", action='store_true')
    return parser

def

def RQSS_Extractor(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])

    Path(opts.output_dir).mkdir(parents=True, exist_ok=True)

    if(opts.input != None): 
        #print('file is specified : {0}'.format(opts.input))
        return extract_from_file(opts)
    if(opts.endpoint != None):
        #print('endpoint is specified: {0}'.format(opts.endpoint))
        return extract_from_endpoint(opts)

    return 0


if __name__ == '__main__':
    RQSS_Extractor(sys.argv[1:])