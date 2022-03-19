import csv
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import List, Optional, Union

from SPARQLWrapper import JSON, SPARQLWrapper

from EntitySchemaExtractor import EntitySchemaExtractor
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
        "-o", "--output-dir", help="Output destination directory to store extarcted components from the RDF input file", default=os.getcwd()+os.sep+'rqss_extractor_output')
    parser.add_argument("-eExt", "--extract-external",
                        help="Extract all external sources uris (Wikibase referencing model) and save them on output dir. Collects data for computing Dimensions: Availability, Licensing, Security", action='store_true')
    parser.add_argument("-sn", "--statement-nodes",
                        help="Extract all statement nodes uris (Wikibase referencing model) and save them on output dir. Collects data for computing Metric: Syntactic validity of reference triples", action='store_true')
    parser.add_argument("-l", "--literals",
                        help="Extract all literal values in reference triples and save them on output dir. Collects data for computing Metric: Syntactic validity of references’ literals", action='store_true')
    parser.add_argument("-fr", "--fact-ref-triples",
                        help="Extract all facts and their reference triples and save them on output dir. Collects data for computing Metric: Semantic validity of reference triples", action='store_true')
    parser.add_argument("-rp", "--ref-properties",
                        help="Extract all reference properties and save them on output dir. Collects data for computing Metric: Consistency of references’ properties", action='store_true')
    parser.add_argument("-rpvt", "--ref-prop-value-type",
                        help="Extract all reference properties and their object value types and save them on output dir. Collects data for computing Metric: Range consistency of reference triples", action='store_true')
    parser.add_argument("-ri", "--ref-incomings",
                        help="Extract all reference nodes and the numebr of their incoming edges (prov:wasDerivedFrom) and save them on output dir. Collects data for computing Metric: Ratio of reference sharing", action='store_true')
    parser.add_argument("-sr", "--statement-refs",
                        help="Extract all sattement nodes and the numebr of their references and save them on output dir. Collects data for computing Metric: Multiple references for facts", action='store_true')
    parser.add_argument("-irf", "--item-refed-facts",
                        help="Extract all items and their referenced facts and save them on output dir. Collects data for computing Metric: Human-added references ratio", action='store_true')
    parser.add_argument("-wes", "--wikidata-eschema-data",
                        help="Extract most up-to-date Wikidata EntitySchemas data from Wikidata directory and save them on output dir. Collects data for computing COMPLETENESS metrics", action='store_true')
    parser.add_argument("-cfr", "--classes-facts-refs",
                        help="Extract all classes of referenced items, and their referenced facts and the reference properties and save them on output dir. Collects data for computing Schema completeness of references metrics", action='store_true')
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
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
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
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in fact_ref_triples:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Facts and their referece triples have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting facts and their reference triples, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_reference_properties(opts: ArgumentParser) -> int:
    print('Started extracting properties that are used in references')
    start_time = datetime.now()

    ref_props = perform_query(
        opts.endpoint, RQSS_QUERIES["get_ref_properties_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_properties.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in ref_props:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Reference properties have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting reference properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_reference_properties_value_types(opts: ArgumentParser) -> int:
    print('Started extracting reference properties and their object values types')
    start_time = datetime.now()

    ref_props = perform_query(
        opts.endpoint, RQSS_QUERIES["get_ref_properties_object_value_types_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_properties_object_value.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in ref_props:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Reference properties and object value types have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting reference properties and object value types, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_reference_node_incomings(opts: ArgumentParser) -> int:
    print('Started extracting reference nodes and the numebr of their incoming edges (prov:wasDerivedFrom)')
    start_time = datetime.now()

    ref_props = perform_query(
        opts.endpoint, RQSS_QUERIES["get_ref_nodes_incomings_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_nodes_incomings.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in ref_props:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Reference nodes and the numebr of their incoming edges (prov:wasDerivedFrom) have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting reference nodes and the numebr of their incoming edges (prov:wasDerivedFrom), Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_statement_node_references(opts: ArgumentParser) -> int:
    print('Started extracting statement nodes and the numebr of their references')
    start_time = datetime.now()

    ref_props = perform_query(
        opts.endpoint, RQSS_QUERIES["get_sattement_nodes_ref_num_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'statement_node_ref_num.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in ref_props:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Statement nodes and the numebr of their references have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting statement nodes and the numebr of their references, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_item_referenced_facts(opts: ArgumentParser) -> int:
    print('Started extracting items and their referenced facts')
    start_time = datetime.now()

    item_refed_facts = perform_query(
        opts.endpoint, RQSS_QUERIES["get_item_refed_facts_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'item_refed_facts.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in item_refed_facts:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Items and their referenced facts have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting items and their referenced facts, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_wikidata_entityschemas_data(opts: ArgumentParser) -> int:
    output_file_classes = os.path.join(
        opts.output_dir + os.sep + 'eschemas_summarization_related_classes.data')
    output_file_refed_fact_refs = os.path.join(
        opts.output_dir + os.sep + 'eschemas_summarization_related_refed_fact_refs.data')

    extractor = EntitySchemaExtractor()
    eschema_data = extractor.get_entity_schemas_references_summary_from_wikidata()

    with open(output_file_classes, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['eid', 'related class', 'related property'])
        for eid in eschema_data:
            for rel_class in eid.related_classes:
                csv_writer.writerow([eid.e_id, rel_class, ''])
        for eid in eschema_data:
            for rel_prop in eid.related_properties:
                csv_writer.writerow([eid.e_id, '', rel_prop])

    with open(output_file_refed_fact_refs, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(['eid', 'refed fact', 'ref predicate'])
        for eid in eschema_data:
            for refed_facts_ref in eid.refed_facts_refs:
                for ref_predicate in refed_facts_ref.ref_predicates:
                    csv_writer.writerow(
                        [eid.e_id, refed_facts_ref.refed_fact, ref_predicate])


def extract_classes_facts_refs(opts: ArgumentParser) -> int:
    print('Started extracting classes of referenced items, and their referenced facts and the reference properties')
    start_time = datetime.now()

    item_refed_facts = perform_query(
        opts.endpoint, RQSS_QUERIES["get_classes_and_facts_and_refed_props"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'classes_facts_refs.data')
    with open(output_file, 'w') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in item_refed_facts:
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Classes of referenced items, and their referenced facts and the reference properties have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting classes of referenced items, and their referenced facts and the reference properties, Duration: {0}'.format(
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

    if(opts.fact_ref_triples):
        p = Process(target=extract_fact_ref_triples(opts))
        extractor_procs.append(p)

    if(opts.ref_properties):
        p = Process(target=extract_reference_properties(opts))
        extractor_procs.append(p)

    if(opts.ref_prop_value_type):
        p = Process(target=extract_reference_properties_value_types(opts))
        extractor_procs.append(p)

    if(opts.ref_incomings):
        p = Process(target=extract_reference_node_incomings(opts))
        extractor_procs.append(p)

    if(opts.statement_refs):
        p = Process(target=extract_statement_node_references(opts))
        extractor_procs.append(p)

    if(opts.item_refed_facts):
        p = Process(target=extract_item_referenced_facts(opts))
        extractor_procs.append(p)

    if(opts.wikidata_eschema_data):
        p = Process(target=extract_wikidata_entityschemas_data(opts))
        extractor_procs.append(p)

    if(opts.classes_facts_refs):
        p = Process(target=extract_classes_facts_refs(opts))
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
