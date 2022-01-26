from multiprocessing.context import Process
import os
import sys
import csv
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from SPARQLWrapper import JSON, SPARQLWrapper

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
        "-o", "--output_dir", help="Output destination directory to store extarcted components from the RDF input file", default=os.getcwd()+os.sep+'rqss_extractor_output')
    parser.add_argument("-eExt", "--extract_external",
                        help="Extract all external sources uris (Wikibase referencing model) and save them on output dir. Collects data for computing Dimensions: Availability, Licensing, Security", action='store_true')
    parser.add_argument("-sn", "--statement_nodes",
                        help="Extract all statement nodes uris (Wikibase referencing model) and save them on output dir. Collects data for computing Metric: Syntactic validity of reference triples", action='store_true')
    parser.add_argument("-l", "--literals",
                        help="Extract all literal values in reference triples and save them on output dir. Collects data for computing Metric: Syntactic validity of references’ literals", action='store_true')
    parser.add_argument("-fr", "--factreftriples",
                        help="Extract all facts and their reference triples and save them on output dir. Collects data for computing Metric: Semantic validity of reference triples", action='store_true')
    return parser


def perform_query(endpoint: str, query: str) -> List[List[str]]:
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
        row = []
        for value in result:
            row.append(result[str(value)]["value"])
        ret_val.append(row)
    return ret_val


def extract_external_uris(opts: ArgumentParser) -> int:
    print('Started extracting External Sources’ URIs')
    start_time = datetime.now()

    external_uris = perform_query(
        opts.endpoint, RQSS_QUERIES["get_all_external_sources_filter_wikimedia_distinct"])
    output_file = os.path.join(opts.output_dir + os.sep + 'external_uris.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for uri in external_uris:
            csv_writer.writerow(uri)

    end_time = datetime.now()
    print('External URIs have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting External URIs, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_statement_nodes_uris(opts: ArgumentParser) -> int:
    print('Started extracting Statement Nodes URIs')
    start_time = datetime.now()

    statement_uris = perform_query(
        opts.endpoint, RQSS_QUERIES["get_all_statement_nodes_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'statement_nodes_uris.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for uri in statement_uris:
            csv_writer.writerow(uri)

    end_time = datetime.now()
    print('Statement Nodes URIs have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting Statement Nodes URIs, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_refrence_literals(opts: ArgumentParser) -> int:
    print('Started extracting literal values in reference triples')
    start_time = datetime.now()

    ref_literals = perform_query(
        opts.endpoint, RQSS_QUERIES["get_reference_literals_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'reference_literals.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for lit in ref_literals:
            csv_writer.writerow(lit)

    end_time = datetime.now()
    print('References’ literal values have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting literal values in reference triples, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_fact_ref_triples(opts: ArgumentParser) -> int:
    print('Started extracting fact subjects, predicate, and reference triples')
    start_time = datetime.now()

    fact_ref_triples = perform_query(
        opts.endpoint, RQSS_QUERIES["get_fact_ref_triples_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'fact_ref_triples.data')
    with open(output_file, 'w') as file_handler:
        for row in fact_ref_triples:
            file_handler.write("{}\n".format(row.replace(
                'http://www.wikidata.org/prop/reference/', '')))  # TODO

    end_time = datetime.now()
    print('Facts and their referece triples have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting facts and their reference triples, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_from_file(opts: ArgumentParser) -> int:
    print('Local file extraction is not supported yet. Please use local/public endpoint.')
    return 1


def extract_from_endpoint(opts: ArgumentParser) -> int:
    # list of parallel processes
    extractor_procs = []

    if(opts.extract_external):
        p = Process(target=extract_external_uris(opts))
        extractor_procs.append(p)

    if(opts.statement_nodes):
        p = Process(target=extract_statement_nodes_uris(opts))
        extractor_procs.append(p)

    if(opts.literals):
        p = Process(target=extract_refrence_literals(opts))
        extractor_procs.append(p)

    if(opts.factreftriples):
        p = Process(target=extract_fact_ref_triples(opts))
        extractor_procs.append(p)

    for proc in extractor_procs:
        proc.start()

    for proc in extractor_procs:
        proc.join()


def RQSS_Extractor(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])

    print('Creating output directory: {0}'.format(opts.output_dir))
    Path(opts.output_dir).mkdir(parents=True, exist_ok=True)

    if(opts.input != None):
        return extract_from_file(opts)
    if(opts.endpoint != None):
        return extract_from_endpoint(opts)

    return 0


if __name__ == '__main__':
    RQSS_Extractor(sys.argv[1:])
