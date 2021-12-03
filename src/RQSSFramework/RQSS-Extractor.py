from base64 import encodestring
import sys
import os
from datetime import datetime
from pathlib import Path
from argparse import ArgumentParser
from typing import Optional, Union, List
from SPARQLWrapper import SPARQLWrapper, JSON, CSV
from Queries import RQSS_QUERIES


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--input", help="Input RDF file of the dataset")
    group.add_argument(
        "--endpoint", help="The local/public endpoint of the dataset")
    parser.add_argument(
        "-f", "--format", help="Input file RDF format (nt, ttl)", default='nt')
    parser.add_argument(
        "-o", "--output_dir", help="Output destination directory to store extarcted components from the RDF input file", default='.'+os.sep+'rqss_extractor_output')
    parser.add_argument("-eExt", "--extract_external",
                        help="Extract all external sources (Wikibase referencing model) and save them on output dir", action='store_true')
    return parser


def perform_query(endpoint: str, query: str) -> List[str]:
    ret_val = []
    sparql = SPARQLWrapper(endpoint)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        print('Performing Query ...')
        results = sparql.query().convert()
    except Exception as e:
        print('ERROR in performing query: {0}'.format(e))
        return ret_val

    for result in results["results"]["bindings"]:
        ret_val.append(result["to_ret"]["value"])
    return ret_val


def extract_from_file(opts: ArgumentParser) -> int:
    print('Local file extraction is not supported yet. Please use local/public endpoint.')
    return 1


def extract_from_endpoint(opts: ArgumentParser) -> int:

    if(opts.extract_external):
        start_time=datetime.now()
        
        external_uris=perform_query(opts.endpoint, RQSS_QUERIES["get_all_external_sources_filter_wikimedia"])
        output_file = os.path.join(opts.output_dir + os.sep + 'external_uris.data')
        with open(output_file, 'w') as file_handler:
            for uri in external_uris:
                file_handler.write("{}\n".format(uri))

        end_time=datetime.now()
        print('External URIs have been written in the file: {0}'.format(output_file))
        print('DONE. Duration: {0}'.format(end_time - start_time))
        return 0


def RQSS_Extractor(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])

    Path(opts.output_dir).mkdir(parents=True, exist_ok=True)

    if(opts.input != None):
        return extract_from_file(opts)
    if(opts.endpoint != None):
        return extract_from_endpoint(opts)

    return 0


if __name__ == '__main__':
    RQSS_Extractor(sys.argv[1:])
