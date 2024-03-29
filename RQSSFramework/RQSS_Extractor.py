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
    parser.add_argument("-eu", "--external-uris",
                        help="Extract all external sources uris (Wikibase referencing model) and save them on output dir. Collects data for computing Dimensions: Availability, Licensing, Security", action='store_true')
    parser.add_argument("-sn", "--statement-nodes",
                        help="Extract all statement nodes uris (Wikibase referencing model) and save them on output dir. Collects data for computing Metric: Syntactic Validity of Reference Triples", action='store_true')
    parser.add_argument("-l", "--literals",
                        help="Extract all literal values in reference triples and save them on output dir. Collects data for computing Metric: Syntactic Validity of References’ Literals", action='store_true')
    parser.add_argument("-fr", "--fact-ref-triples",
                        help="Extract all facts and their reference triples and save them on output dir. Collects data for computing Metric: Semantic Validity of Reference Triples", action='store_true')
    parser.add_argument("-rp", "--ref-properties",
                        help="Extract all reference properties and save them on output dir. Collects data for computing Metric: Consistency of References’ Properties", action='store_true')
    parser.add_argument("-rpvt", "--ref-prop-value-type",
                        help="Extract all reference properties and their object value types and save them on output dir. Collects data for computing Metric: Range Consistency of Reference Triples", action='store_true')
    parser.add_argument("-ri", "--ref-incomings",
                        help="Extract all reference nodes and the numebr of their incoming edges (prov:wasDerivedFrom) and save them on output dir. Collects data for computing Metric: Ratio of Reference Sharing", action='store_true')
    parser.add_argument("-sr", "--statement-refs",
                        help="Extract all sattement nodes and the numebr of their references and save them on output dir. Collects data for computing Metric: Multiple References for Facts", action='store_true')
    parser.add_argument("-irf", "--item-refed-facts",
                        help="Extract all items and their referenced facts and save them on output dir. Collects data for computing Metric: Human-added References Ratio", action='store_true')
    parser.add_argument("-wes", "--wikidata-eschema-data",
                        help="Extract most up-to-date Wikidata EntitySchemas data from Wikidata directory and save them on output dir. Collects Wikidata E-ids data for computing COMPLETENESS metrics", action='store_true')
    parser.add_argument("-cf", "--classes-facts",
                        help="Extract all classes and their facts. Collects data for computing Metric: Class/Property Schema Completeness of References", action='store_true')
    parser.add_argument("-sfr", "--statements-facts-refs",
                        help="Extract all statement id, fact of the statement and the reference properties and save them on output dir. Collects data for computing Metrics: Schema-based Property Completeness and Property Completeness of References", action='store_true')
    parser.add_argument("-aof", "--amount-of-data",
                        help="Extract number of statement nodes, reference nodes, and distribution of triple and literals amongst reference nodes. Collects data for computing Amount-of-Data metrics", action='store_true')
    parser.add_argument("-pu", "--ref-prop-usage",
                        help="Extract number of reference properties, reference triples and reference properties usage distribution and save them on output dir. Collects data for computing Mtric: Diversity of Reference Properties", action='store_true')
    parser.add_argument("-es", "--external-sources",
                        help="Extract all external sources (including Wikidata items) and save them on output dir. Collects data for computing Mtric: Handy External Sources", action='store_true')
    parser.add_argument("-ss", "--statement-source",
                        help="Extract all statement ids and their sources (only IRIs, not literals) and save them on output dir. Collects data for computing Mtrics: Verifiable Type of references, Multilingual Sources and Multilingual Referenced Facts", action='store_true')
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
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
    with open(output_file, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in item_refed_facts:
            csv_writer.writerow([cell.replace('http://www.wikidata.org/entity/',
                                              '').replace('http://www.wikidata.org/prop/', '') for cell in row])

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


def extract_classes_facts(opts: ArgumentParser) -> int:
    print('Started extracting classes and their facts')
    start_time = datetime.now()

    item_refed_facts = perform_query(
        opts.endpoint, RQSS_QUERIES["get_classes_and_facts"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'classes_facts.data')
    with open(output_file, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in item_refed_facts:
            row = [
                row[0].replace('http://www.wikidata.org/entity/', ''),
                row[1].replace('http://www.wikidata.org/prop/', '')] if len(row) == 2 else [
                'no_class_found',
                row[0].replace('http://www.wikidata.org/prop/', '')]
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Classes and their facts have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting classes and their facts, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_statement_fact_refed_props_wikimedia(opts: ArgumentParser) -> int:
    print('Started extracting statement id, fact of the statement and the reference properties')
    start_time = datetime.now()

    item_refed_facts = perform_query(
        opts.endpoint, RQSS_QUERIES["get_statement_fact_refed_props_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'statement_fact_refed_props.data')
    with open(output_file, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in item_refed_facts:
            row = [
                row[0].replace(
                    'http://www.wikidata.org/entity/statement/', ''),
                row[1].replace('http://www.wikidata.org/prop/', ''),
                row[2].replace('http://www.wikidata.org/prop/reference/', '')] if len(row) == 3 else [
                row[0].replace(
                    'http://www.wikidata.org/entity/statement/', ''),
                row[1].replace('http://www.wikidata.org/prop/', '')]
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Statement id, fact of the statement and the reference properties have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting statement id, fact of the statement and the reference properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_amount_of_data_wikimedia(opts: ArgumentParser) -> int:
    print('Started extracting number of statement nodes, reference nodes, and distribution of triple and literals amongst reference nodes')
    start_time = datetime.now()

    output_file_num = os.path.join(
        opts.output_dir + os.sep + 'num_of_statement_and_ref_nodes.data')
    output_file_triple_dist = os.path.join(
        opts.output_dir + os.sep + 'triple_per_ref_node_distribution.data')
    output_file_literal_dist = os.path.join(
        opts.output_dir + os.sep + 'literal_per_ref_node_distribution.data')

    print('Get number of statement nodes')
    num_statement_nodes = perform_query(
        opts.endpoint, RQSS_QUERIES["get_num_of_statement_nodes_wikimedia"])
    print('Get number of reference nodes')
    num_ref_nodes = perform_query(
        opts.endpoint, RQSS_QUERIES["get_num_of_ref_nodes_wikimedia"])

    with open(output_file_num, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(
            ['num of statement nodes', 'num of reference nodes'])
        csv_writer.writerow([num_statement_nodes[0][0], num_ref_nodes[0][0]])

    print('Get triple per reference node distribution')
    triple_dist = perform_query(
        opts.endpoint, RQSS_QUERIES["get_triple_per_ref_node_distribution_wikimedia"])
    with open(output_file_triple_dist, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in triple_dist:
            row = [
                row[0].replace('http://www.wikidata.org/reference/', ''),
                row[1]]
            csv_writer.writerow(row)

    print('Get literal values per reference node distribution')
    literal_dist = perform_query(
        opts.endpoint, RQSS_QUERIES["get_literal_per_ref_node_distribution_wikimedia"])
    with open(output_file_literal_dist, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in literal_dist:
            row = [
                row[0].replace('http://www.wikidata.org/reference/', ''),
                row[1]]
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Number of statement nodes, reference nodes, and distribution of triple and literals amongst reference nodes have been written in the files: {0}, {1}, {2}'.format(
        output_file_num, output_file_triple_dist, output_file_literal_dist))
    print('DONE. Extracting number of statement nodes, reference nodes, and distribution of triple and literals amongst reference nodes, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_refـpropـusage_wikimedia(opts: ArgumentParser) -> int:
    print('Started extracting number of reference properties, reference triples and reference properties usage distribution')
    start_time = datetime.now()

    output_file_num = os.path.join(
        opts.output_dir + os.sep + 'num_of_ref_props_and_ref_triples.data')
    output_file_usage_dist = os.path.join(
        opts.output_dir + os.sep + 'reference_property_usage_distribution.data')

    print('Get number of reference properties')
    num_ref_prop = perform_query(
        opts.endpoint, RQSS_QUERIES["get_num_of_reference_properties_wikimedia"])
    print('Get number of reference triples')
    num_ref_triple = perform_query(
        opts.endpoint, RQSS_QUERIES["get_num_of_reference_triples_wikimedia"])

    with open(output_file_num, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        csv_writer.writerow(
            ['num of ref properties', 'num of ref triples'])
        csv_writer.writerow([num_ref_prop[0][0], num_ref_triple[0][0]])

    print('Get reference properties usage distribution')
    usage_dist = perform_query(
        opts.endpoint, RQSS_QUERIES["get_reference_properties_usage_distribution_wikimedia"])
    with open(output_file_usage_dist, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in usage_dist:
            row = [
                row[0].replace('http://www.wikidata.org/prop/reference/', ''),
                row[1]]
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('number of reference properties, reference triples and reference properties usage distribution have been written in the files: {0}, {1}'.format(
        output_file_num, output_file_usage_dist))
    print('DONE. Extracting number of reference properties, reference triples and reference properties usage distribution, Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_external_sources_wikimedia(opts: ArgumentParser) -> int:
    print('Started extracting External Sources')
    start_time = datetime.now()

    external_uris = perform_query(
        opts.endpoint, RQSS_QUERIES["get_all_external_sources_distinct"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'external_sources.data')
    with open(output_file, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for uri in external_uris:
            csv_writer.writerow(
                [cell.replace('http://www.wikidata.org/entity/', '') for cell in uri])

    end_time = datetime.now()
    print('External Sources have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting External Sources, Duration: {0}'.format(
        end_time - start_time))
    return 0



def extract_statements_sources_wikimedia(opts: ArgumentParser) -> int:
    print('Started extracting statement ids and their sources (only IRIs, not literals)')
    start_time = datetime.now()

    statement_source = perform_query(
        opts.endpoint, RQSS_QUERIES["get_statement_sources_wikimedia"])
    output_file = os.path.join(
        opts.output_dir + os.sep + 'statement_source.data')
    with open(output_file, 'w', newline='') as file_handler:
        csv_writer = csv.writer(
            file_handler, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in statement_source:
            row = [
                row[0].replace('http://www.wikidata.org/entity/statement/', ''),
                row[1].replace('http://www.wikidata.org/entity/', '')]
            csv_writer.writerow(row)

    end_time = datetime.now()
    print('Statement ids and their sources (only IRIs, not literals) have been written in the file: {0}'.format(
        output_file))
    print('DONE. Extracting statement ids and their sources (only IRIs, not literals), Duration: {0}'.format(
        end_time - start_time))
    return 0


def extract_from_file(opts: ArgumentParser) -> int:
    print('Local file extraction is not supported yet. Please use local/public endpoint.')
    return 1


def extract_from_endpoint(opts: ArgumentParser) -> int:
    # list of parallel processes
    extractor_procs = []

    if(opts.external_uris):
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

    if(opts.classes_facts):
        p = Process(target=extract_classes_facts(opts))
        extractor_procs.append(p)

    if(opts.statements_facts_refs):
        p = Process(target=extract_statement_fact_refed_props_wikimedia(opts))
        extractor_procs.append(p)

    if(opts.amount_of_data):
        p = Process(target=extract_amount_of_data_wikimedia(opts))
        extractor_procs.append(p)

    if(opts.ref_prop_usage):
        p = Process(target=extract_refـpropـusage_wikimedia(opts))
        extractor_procs.append(p)

    if(opts.external_sources):
        p = Process(target=extract_external_sources_wikimedia(opts))
        extractor_procs.append(p)

    if(opts.statement_source):
        p = Process(target=extract_statements_sources_wikimedia(opts))
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

    if(opts.input is not None):
        return extract_from_file(opts)
    if(opts.endpoint is not None):
        return extract_from_endpoint(opts)

    return 0


if __name__ == '__main__':
    RQSS_Extractor(sys.argv[1:])
