import csv
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import List, NamedTuple, Optional, Union

import pandas as pd

from Accuracy.LiteralSyntaxChecking import WikibaseRefLiteralSyntaxChecker
from Accuracy.TripleSemanticChecking import (FactReference,
                                             RefTripleSemanticChecker)
from Accuracy.TripleSyntaxChecking import WikibaseRefTripleSyntaxChecker
from Amount_of_Data.AmountOfDataComputing import *
from Availability.DereferencePossibility import DerefrenceExplorer
from Believability.HumanReferenceInItemChecking import *
from Completeness.ClassesPropertiesSchemaCompletenessChecking import *
from Completeness.PropertyCompletenessChecking import *
from Completeness.SchemaBasedRefPropertiesCompletenessChecking import *
from Conciseness.ReferenceSharingChecking import *
from Consistency.RefPropertiesConsistencyChecking import \
    RefPropertiesConsistencyChecker
from Consistency.TriplesRangeConsistencyChecking import \
    TriplesRangeConsistencyChecker
from Currency.ExternalURIsFreshnessChecking import *
from Currency.ReferenceFreshnessChecking import *
from EntitySchemaExtractor import EidRefSummary, RefedFactRef
from Interlinking.RefPropertiesInterlinkingChecking import *
from Interpretability.BlankNodeChecking import *
from Licensing.LicenseExistanceChecking import LicenseChecker
from Objectivity.MultipleReferenceChecking import *
from Queries import RQSS_QUERIES
from Representational_Conciseness.ExternalSourcesURILengthChecking import *
from Representational_Consistency.RefPropertiesDiversityComputing import *
from Reputation.DNSBLBlacklistedChecking import DNSBLBlacklistedChecker
from Security.TLSExistanceChecking import TLSChecker
from Timeliness.ExternalURIsTimelinessChecking import *
from Understandability.HandyExternalSourcesChecking import *
from Understandability.HumanReadableMetadataChecking import *
from utils.lists import known_datasets
from Verifiability.TypeofSourcesChecking import *
from Versatility.MultilingualMetadataChecking import *
from Versatility.MultilingualSourcesAndFactsChecking import *
from Volatility.ExternalURIsVolatilityChecking import *


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument(
        "data_dir", help="Input data directory that includes initial collections like facts, properties, literals, external sources, etc.")
    parser.add_argument(
        "--endpoint", help="The local/public endpoint of the dataset for shex-based metrics", required=False)
    parser.add_argument(
        "--upper-date", help="The upper date (Format DD-MM-YYYY) limit for reivision history checker metrics. The deafult is now()", required=False, type=lambda d: datetime.datetime.strptime(d, "%d-%m-%Y"), default=datetime.datetime.now())
    parser.add_argument(
        "-o", "--output-dir", help="Output destination directory to store computed metrics details", default=os.getcwd()+os.sep+'rqss_framework_output')
    parser.add_argument("-dp", "--dereferencing",
                        help="Compute the metric: Dereference Possibility of the External URIs", action='store_true')
    parser.add_argument("-l", "--licensing",
                        help="Compute the metric: External Sources’ Datasets Licensing", action='store_true')
    parser.add_argument("-sec", "--security",
                        help="Compute the metric: Link Security of the External URIs", action='store_true')
    parser.add_argument("-i", "--interlinking",
                        help="Compute the metric: Interlinking of Reference Properties", action='store_true')
    parser.add_argument("-rts", "--ref-triple-syntax",
                        help="Compute the metric: Syntactic Validity of Reference Triples", action='store_true')
    parser.add_argument("-rls", "--ref-literal-syntax",
                        help="Compute the metric: Syntactic Validity of Reference Literals", action='store_true')
    parser.add_argument("-rtm", "--ref-triple-semantic",
                        help="Compute the metric: Semantic Validity of Reference Triples", action='store_true')
    parser.add_argument("-rpc", "--ref-property-consistency",
                        help="Compute the metric: Consistency of Reference Properties", action='store_true')
    parser.add_argument("-rc", "--range-consistency",
                        help="Compute the metric: Range Consistency of Reference Triples", action='store_true')
    parser.add_argument("-rs", "--ref-sharing",
                        help="Compute the metric: Ratio of Reference Sharing", action='store_true')
    parser.add_argument("-rdns", "--reputation",
                        help="Compute the metric: External Sources’ Domain Reputation", action='store_true')
    parser.add_argument("-mr", "--multiple-ref",
                        help="Compute the metric: Multiple References for Facts", action='store_true')
    parser.add_argument("-ha", "--human-added",
                        help="Compute the metric: Human-added References Ratio", action='store_true')
    parser.add_argument("-ts", "--type-of-sources",
                        help="Compute the metrics: Verifiable Type of References", action='store_true')
    parser.add_argument("-rf", "--ref-freshness",
                        help="Compute the metric: Freshness of Fact Referencing", action='store_true')
    parser.add_argument("-ef", "--ext-uris-freshness",
                        help="Compute the metric: Freshness of External Sources", action='store_true')
    freshness_group = parser.add_argument_group(
        title='options for computing freshness of external sources')
    freshness_group.add_argument(
        "--extract-google-cache", help="Set to extract google cache info for freshness of external sources", action='store_true')
    parser.add_argument("-ev", "--ext-uris-volatility",
                        help="Compute the metric: Volatility of External Sources", action='store_true')
    parser.add_argument("-et", "--ext-uris-timeliness",
                        help="Compute the metric: Timeliness of External Sources. The metric will use the results of the metrics Freshness of external sources and Volatility of external sources. Make sure the results of the two metric is in the --output-dir argument", action='store_true')
    parser.add_argument("-cpsc", "--class-property-schema-completeness",
                        help="Compute the metric: Schema Completeness of References", action='store_true')
    parser.add_argument("-sbpc", "--schema-based-property-completeness",
                        help="Compute the metric: Schema-based Property Completeness of References", action='store_true')
    parser.add_argument("-pc", "--property-completeness",
                        help="Compute the metric: Property Completeness of References", action='store_true')
    parser.add_argument("-aof", "--amount-of-data",
                        help="Compute the Dimension: Amount-of-Data", action='store_true')
    parser.add_argument("-el", "--ext-uri-length",
                        help="Compute the metric: External Sources URL Length", action='store_true')
    parser.add_argument("-rpd", "--ref-property-diversity",
                        help="Compute the metric: Diversity of Reference Properties", action='store_true')
    parser.add_argument("-hm", "--human-readable-metadata",
                        help="Compute the metrics: Human-readable Labeling and Human-readable Commenting of Reference Properties", action='store_true')
    parser.add_argument("-he", "--handy-external-sources",
                        help="Compute the metrics: Handy External Sources", action='store_true')
    parser.add_argument("-bn", "--blank-node",
                        help="Compute the metrics: Usage of Blank Nodes", action='store_true')
    parser.add_argument("-mm", "--multilingual-metadata",
                        help="Compute the metrics: Multilingual Labeling and Multilingual Commenting of Reference Properties", action='store_true')
    parser.add_argument("-mfs", "--multilingual-sources-facts",
                        help="Compute the metrics: Multilingual Sources and Multilingual Referenced Facts", action='store_true')
    return parser


def write_results_to_CSV(results: List[NamedTuple], output_file: str) -> None:
    with open(output_file, 'w', newline='') as f:
        if isinstance(results, str):
            f.write(results)
            return

        w = csv.writer(
            f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        # write header from NamedTuple fields
        w.writerow([field for field in results[0]._fields])
        for result in results:
            row = ['<None>' if result._asdict()[field] == None else result._asdict()[
                field] for field in result._fields]
            w.writerow(row)
    return


def compute_dereferencing(opts: ArgumentParser) -> int:
    print('Started computing Metric: Dereference Possibility of the External URIs')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'dereferencing.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'dereferencing_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    deref_checker = DerefrenceExplorer(uris)
    results = deref_checker.check_dereferencies()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(deref_checker), output_file_result)

    print('Metric: Dereference Possibility of the External URIs results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Dereference Possibility of the External URIs, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_licensing(opts: ArgumentParser) -> int:
    print('Started computing Metric: External Sources’ Datasets Licensing')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(opts.output_dir + os.sep + 'licensing.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'licensing_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    lic_checker = LicenseChecker(uris)
    results = lic_checker.check_license_existance()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(lic_checker), output_file_result)

    print('Metric: External Sources’ Datasets Licensing results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: External Sources’ Datasets Licensing, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_security(opts: ArgumentParser) -> int:
    print('Started computing Metric: Link Security of the External URIs')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(opts.output_dir + os.sep + 'security.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'security_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    sec_checker = TLSChecker(uris)
    results = sec_checker.check_support_tls()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(sec_checker), output_file_result)

    print('Metric: Link Security of the External URIs results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Link Security of the External URIs, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_interlinking(opts: ArgumentParser) -> int:
    print('Started computing Metric: Interlinking of Reference Properties')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'interlinking.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'interlinking_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    props = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                props.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"ref_properties.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    inter_checker = RefPropertiesInterlinkingChecker(props)
    results = inter_checker.check_reference_interlinking_from_Wikdiata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(inter_checker), output_file_result)

    print('Metric: Interlinking of Reference Properties results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Interlinking of Reference Properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_triple_syntax(opts: ArgumentParser) -> int:
    print('Started computing Metric: Syntactic Validity of Reference Triples')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_nodes_uris.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_triple_syntax_result.csv')

    # reading the statement nodes data
    print('Reading data ...')
    statements = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                statements.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"statement_nodes_uris.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    shex_checker = None
    if(opts.endpoint):
        shex_checker = WikibaseRefTripleSyntaxChecker(
            statements, opts.endpoint, None)
        results = shex_checker.check_shex_over_endpoint()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(str(shex_checker), output_file)

    print('Metric: Syntactic Validity of Reference Triples results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Syntactic Validity of Reference Triples, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_literal_syntax(opts: ArgumentParser) -> int:
    print('Started computing Metric: Syntactic validity of references’ literals')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'reference_literals.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'ref_literal_syntax.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'ref_literal_syntax_ratio.csv')

    # reading the properties/literals
    print('Reading data ...')
    prop_values = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in prop_values.keys():
                    prop_values[str(row[0])] = []
                prop_values[str(row[0])].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"reference_literals.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    lit_checker = WikibaseRefLiteralSyntaxChecker(prop_values)
    results = lit_checker.check_literals_regex()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(lit_checker), output_file_result)

    print('Metric: Syntactic validity of references’ literals results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Syntactic validity of references’ literals, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_triple_semantic(opts: ArgumentParser) -> int:
    print('Started computing Metric: Semantic validity of reference triples')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'fact_ref_triples.data')
    input_gold_standard_file = os.path.join(
        opts.data_dir + os.sep + 'semantic_validity_gs.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'semantic_validity.csv')

    # reading the fact/reference triples
    print('Reading data ...')
    fact_refs = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                fact_refs.append(FactReference(row[0], row[1], row[2], row[3]))
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"fact_ref_triples.data"'))
        exit(1)

    # reading the gold standard set
    print('Reading gold standard set ...')
    gs_fact_refs = []
    try:
        with open(input_gold_standard_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                gs_fact_refs.append(FactReference(
                    row[0], row[1], row[2], row[3]))
    except FileNotFoundError:
        print("Error: Gold Standard Set file not found. Provide gold standard data file with name: {0} in data_dir".format(
            '"semantic_validity_gs.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    results = RefTripleSemanticChecker(
        gs_fact_refs, fact_refs).check_semantic_to_gold_standard()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file)

    print('Metric: Syntactic validity of references’ literals results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Syntactic validity of references’ literals, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_properties_consistency(opts: ArgumentParser) -> int:
    print('Started computing Metric: Consistency of reference properties')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'ref_properties_consistency.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'ref_properties_consistency_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    props = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                props.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"ref_properties.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    cons_checker = RefPropertiesConsistencyChecker(props)
    results = cons_checker.check_reference_specificity_from_Wikdiata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(cons_checker), output_file_result)

    print('Metric: Consistency of reference properties results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Consistency of reference properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_range_consistency(opts: ArgumentParser) -> int:
    print('Started computing Metric: Range consistency of reference triples')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties_object_value.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'range_consistency.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'range_consistency_ratio.csv')

    # reading the properties/literals
    print('Reading data ...')
    prop_values = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in prop_values.keys():
                    prop_values[str(row[0])] = []
                prop_values[str(row[0])].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"ref_properties_object_value.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    range_checker = TriplesRangeConsistencyChecker(prop_values)
    results = range_checker.check_all_value_ranges()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(range_checker), output_file_result)

    print('Metric: Range consistency of reference triples results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Range consistency of reference triples, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_sharing_ratio(opts: ArgumentParser) -> int:
    print('Started computing Metric: Ratio of reference sharing')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_nodes_incomings.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'ref_sharing.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'ref_sharing_ratio.csv')

    # reading the statement nodes data
    print('Reading data ...')
    ref_nodes = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                ref_nodes.append(RefNodeIncomings(row[0], row[1]))
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"ref_nodes_incomings.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    checker = ReferenceSharingChecker(ref_nodes)
    shared_refs = checker.count_seperate_shared_references()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(shared_refs) > 0:
        write_results_to_CSV(shared_refs, output_file_dist)
        write_results_to_CSV(str(checker), output_file_result)

    print('Metric: Ratio of reference sharing results have been written in the files: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Ratio of reference sharing, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_dnsbl_reputation(opts: ArgumentParser) -> int:
    print('Started computing Metric: External sources’ domain reputation')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'dnsbl_reputation.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'dnsbl_reputation_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    dnsbl_checker = DNSBLBlacklistedChecker(uris)
    results = dnsbl_checker.check_domain_blacklisted()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(dnsbl_checker), output_file_result)

    print('Metric: External sources’ domain reputation results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: External sources’ domain reputation, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_multiple_referenced(opts: ArgumentParser) -> int:
    print('Started computing Metric: Multiple references for facts')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_node_ref_num.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'multiple_refs.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'multiple_refs_ratio.csv')

    # reading the statement nodes data
    print('Reading data ...')
    statements = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                statements.append(StatementRefNum(row[0], row[1]))
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"statement_node_ref_num.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    checker = MultipleReferenceChecker(statements)
    multiples = checker.count_seperate_multiple_referenced_statements()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(multiples) > 0:
        write_results_to_CSV(multiples, output_file_dist)
        write_results_to_CSV(str(checker), output_file_result)

    print('Metric: Multiple references for facts results have been written in the files: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Multiple references for facts, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_human_added_references_per_item(opts: ArgumentParser) -> int:
    print('Started computing Metric: Human-added references ratio')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'item_refed_facts.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'human_added.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'human_added_ratio.csv')

    # reading the properties/literals
    print('Reading data ...')
    item_refed_facts = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in item_refed_facts.keys():
                    item_refed_facts[str(row[0])] = []
                item_refed_facts[str(row[0])].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"item_refed_facts.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    human_added_checker = HumanReferenceInItemChecker(
        item_refed_facts, opts.upper_date)
    dist = human_added_checker.check_referenced_facts_human_added()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(dist) > 0:
        write_results_to_CSV(dist, output_file_dist)
        write_results_to_CSV(str(human_added_checker), output_file_result)

    print('Metric: Human-added references ratio results have been written in the files: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Human-added references ratio, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_verifiable_type_of_sources(opts: ArgumentParser) -> int:
    print('Started computing Metrics: Verifiable Type of References')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_source.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'type_of_sources.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'type_of_sources_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    srcs = []
    statements_ref_vals: Dict = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in statements_ref_vals.keys():
                    statements_ref_vals[row[0]] = []
                statements_ref_vals[row[0]].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"statement_source.data"'))
        exit(1)

    distinct_sources = set.union(
        *[set(value) for key, value in statements_ref_vals.items()])
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    type_checker = TypeOfSourcesChecker(distinct_sources, known_datasets)
    results = type_checker.check_type_of_sources_wikidata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(type_checker), output_file_result)

    print('Metrics: Verifiable Type of References results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metrics: Verifiable Type of References, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_referenced_facts_reference_freshness_per_item(opts: ArgumentParser) -> int:
    print('Started computing Metric: Freshness of fact referencing')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'item_refed_facts.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'fact_freshness.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'fact_freshness_ratio.csv')

    # reading the properties/literals
    print('Reading data ...')
    item_refed_facts = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in item_refed_facts.keys():
                    item_refed_facts[str(row[0])] = []
                item_refed_facts[str(row[0])].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"item_refed_facts.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    freshness_checker = ReferenceFreshnessInItemChecker(
        item_refed_facts, opts.upper_date)
    dist = freshness_checker.check_referenced_facts_freshness()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(dist) > 0:
        write_results_to_CSV(freshness_checker.results, output_file_dist)
        write_results_to_CSV(str(freshness_checker), output_file_result)

    print('Metric: Freshness of fact referencing results have been written in the files: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Freshness of fact referencing, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_external_uris_freshness(opts: ArgumentParser) -> int:
    print('Started computing Metric: Freshness of external sources')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'external_uris_freshness.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'external_uris_freshness_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    freshness_checker = ExternalURIsFreshnessChecker(
        uris, extract_google_cache=opts.extract_google_cache)
    results = freshness_checker.check_external_uris_freshness()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(freshness_checker.results, output_file_dist)
        write_results_to_CSV(str(freshness_checker), output_file_result)

    print('Metric: Freshness of external sources results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Freshness of external sources, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_external_uris_volatility(opts: ArgumentParser) -> int:
    print('Started computing Metric: Volatility of external sources')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'external_uris_volatility.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'external_uris_volatility_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    volatility_checker = ExternalURIsVolatilityChecker(uris)
    results = volatility_checker.check_external_uris_volatility()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(volatility_checker.results, output_file_dist)
        write_results_to_CSV(str(volatility_checker), output_file_result)

    print('Metric: Volatility of external sources results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Volatility of external sources, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_external_uris_timeliness(opts: ArgumentParser) -> int:
    print('Started computing Metric: Timeliness of external sources')
    input_data_file_freshness = os.path.join(
        opts.output_dir + os.sep + 'external_uris_freshness.csv')
    input_data_file_volatility = os.path.join(
        opts.output_dir + os.sep + 'external_uris_volatility.csv')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'external_uris_timeliness.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'external_uris_timeliness_ratio.csv')

    # reading the freshness input data
    print('Reading data ...')
    freshnesses = []
    volatilities = []
    try:
        with open(input_data_file_freshness, encoding="utf8") as file:
            reader = csv.reader(file)
            next(reader, None)  # skip the headers
            for row in reader:
                freshnesses.append(FreshnessOfURI(URIRef(str(row[0])), freshness_last_modif=float(
                    row[1]) if row[1] != '<None>' else None))
    except FileNotFoundError:
        print("Error: Input data file of freshness scores not found. Provide data file with name: {0} in --output-dir".format(
            '"external_uris_freshness.csv"'))
        exit(1)
    # reading the volatility input data
    try:
        with open(input_data_file_volatility, encoding="utf8") as file:
            reader = csv.reader(file)
            next(reader, None)  # skip the headers
            for row in reader:
                volatilities.append(VolatilityOfURI(
                    URIRef(str(row[0])), float(row[1]) if row[1] != '<None>' else None))
    except FileNotFoundError:
        print("Error: Input data file of volatility scores not found. Provide data file with name: {0} in --output-dir".format(
            '"external_uris_volatility.csv"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    timeliness_checker = ExternalURIsTimelinessChecker(
        freshnesses, volatilities)
    results = timeliness_checker.check_external_uris_timeliness()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(timeliness_checker.results, output_file_dist)
        write_results_to_CSV(str(timeliness_checker), output_file_result)

    print('Metric: Timeliness of external sources results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Timeliness of external sources, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_class_property_schema_completeness(opts: ArgumentParser) -> int:
    print('Started computing Metric: Schema completeness of references')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'classes_facts.data')
    input_eid_summarization_related_classes = os.path.join(
        opts.data_dir + os.sep + 'eschemas_summarization_related_classes.data')
    input_eid_summarization_refed_fact_refs = os.path.join(
        opts.data_dir + os.sep + 'eschemas_summarization_related_refed_fact_refs.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'class_property_schema_completeness.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'class_property_schema_completeness_ratio.csv')

    # reading eid data
    print('Reading Entity Schemas data ...')
    try:
        with open(input_eid_summarization_related_classes, encoding="utf8") as file:
            related_class_csv = pd.read_csv(file)
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"eschemas_summarization_related_classes.data"'))
        exit(1)
    try:
        with open(input_eid_summarization_refed_fact_refs, encoding="utf8") as file:
            refed_fact_refs_csv = pd.read_csv(file)
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"eschemas_summarization_related_refed_fact_refs.data"'))
        exit(1)

    eid_summaries: List[EidRefSummary] = []
    for eid in related_class_csv['eid'].unique().tolist():
        refed_facts_refs: List[RefedFactRef] = []
        for fact in refed_fact_refs_csv.loc[(refed_fact_refs_csv['eid'] == eid), 'refed fact'].unique().tolist():
            refed_facts_refs.append(RefedFactRef(fact, refed_fact_refs_csv.loc[(refed_fact_refs_csv['eid'] == eid) & (
                refed_fact_refs_csv['refed fact'] == fact), 'ref predicate'].dropna().tolist()))
        eid_summaries.append(EidRefSummary(eid, related_class_csv.loc[related_class_csv['eid'] == eid, 'related class'].dropna(
        ).tolist(), related_class_csv.loc[related_class_csv['eid'] == eid, 'related property'].dropna().tolist(), refed_facts_refs))

    print('Number of E-ids: ', len(eid_summaries))
    print('Number of E-ids with referenced facts: ',
          sum([1 for i in eid_summaries if len(i.refed_facts_refs) > 0]))

    # reading the input instance-level data
    print('Reading instance-level data ...')
    refed_fact_refs: Dict = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in refed_fact_refs.keys():
                    refed_fact_refs[row[0]] = []
                if row[1] in refed_fact_refs[row[0]]:
                    continue
                else:
                    refed_fact_refs[row[0]].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"classes_facts.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    schema_comp_checker = ClassesPropertiesSchemaCompletenessChecker(
        refed_fact_refs, eid_summaries)
    results = schema_comp_checker.check_ref_schema_existance_for_properties_Wikidata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(schema_comp_checker.results, output_file_dist)
        write_results_to_CSV(str(schema_comp_checker), output_file_result)

    print('Metric: Schema completeness of references results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Schema completeness of references, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_schema_based_property_completeness(opts: ArgumentParser) -> int:
    print('Started computing Metric: Schema-based property completeness of references')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_fact_refed_props.data')
    input_eid_summarization_related_classes = os.path.join(
        opts.data_dir + os.sep + 'eschemas_summarization_related_classes.data')
    input_eid_summarization_refed_fact_refs = os.path.join(
        opts.data_dir + os.sep + 'eschemas_summarization_related_refed_fact_refs.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'schema_based_property_completeness.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'schema_based_property_completeness_ratio.csv')

    # reading eid data
    print('Reading Entity Schemas data ...')
    try:
        with open(input_eid_summarization_related_classes, encoding="utf8") as file:
            related_class_csv = pd.read_csv(file)
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"eschemas_summarization_related_classes.data"'))
        exit(1)
    try:
        with open(input_eid_summarization_refed_fact_refs, encoding="utf8") as file:
            refed_fact_refs_csv = pd.read_csv(file)
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"eschemas_summarization_related_refed_fact_refs.data"'))
        exit(1)

    eid_summaries: List[EidRefSummary] = []
    for eid in related_class_csv['eid'].unique().tolist():
        refed_facts_refs: List[RefedFactRef] = []
        for fact in refed_fact_refs_csv.loc[(refed_fact_refs_csv['eid'] == eid), 'refed fact'].unique().tolist():
            refed_facts_refs.append(RefedFactRef(fact, refed_fact_refs_csv.loc[(refed_fact_refs_csv['eid'] == eid) & (
                refed_fact_refs_csv['refed fact'] == fact), 'ref predicate'].dropna().tolist()))
        eid_summaries.append(EidRefSummary(eid, related_class_csv.loc[related_class_csv['eid'] == eid, 'related class'].dropna(
        ).tolist(), related_class_csv.loc[related_class_csv['eid'] == eid, 'related property'].dropna().tolist(), refed_facts_refs))

    print('Number of E-ids: ', len(eid_summaries))
    print('Number of E-ids with referenced facts: ',
          sum([1 for i in eid_summaries if len(i.refed_facts_refs) > 0]))

    # reading the input instance-level data
    print('Reading instance-level data ...')
    refed_fact_refs: List[FactRef] = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    refed_fact_refs.append(FactRef(row[0], row[1], row[2]))
                except IndexError:
                    refed_fact_refs.append(FactRef(row[0], row[1]))
    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"statement_fact_refed_props.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    schema_comp_checker = SchemaBasedRefPropertiesCompletenessChecker(
        refed_fact_refs)
    results = schema_comp_checker.check_schema_based_property_completeness_Wikidata(
        eid_summaries)
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if results:
        write_results_to_CSV(schema_comp_checker.results, output_file_dist)
    write_results_to_CSV(str(schema_comp_checker), output_file_result)

    print('Metric: Schema-based property completeness of references results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Schema-based property completeness of references, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_property_completeness(opts: ArgumentParser) -> int:
    print('Started computing Metric: Property Completeness of References')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_fact_refed_props.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'property_completeness.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'property_completeness_ratio.csv')

    # reading the input instance-level data
    print('Reading instance-level data ...')
    refed_fact_refs: List[FactRef] = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                try:
                    refed_fact_refs.append(FactRef(row[0], row[1], row[2]))
                except IndexError:
                    refed_fact_refs.append(FactRef(row[0], row[1]))
    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"statement_fact_refed_props.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    schema_comp_checker = PropertyCompletenessChecker(
        refed_fact_refs)
    results = schema_comp_checker.check_property_completeness_Wikidata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if results:
        write_results_to_CSV(schema_comp_checker.results, output_file_dist)
    write_results_to_CSV(str(schema_comp_checker), output_file_result)

    print('Metric: Property Completeness of References results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Property Completeness of References, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_amount_of_data(opts: ArgumentParser) -> int:
    print('Started computing Dimension: Amount-of-Data')
    input_data_file_nums = os.path.join(
        opts.data_dir + os.sep + 'num_of_statement_and_ref_nodes.data')
    input_data_file_triple_dist = os.path.join(
        opts.data_dir + os.sep + 'triple_per_ref_node_distribution.data')
    input_data_file_literal_dist = os.path.join(
        opts.data_dir + os.sep + 'literal_per_ref_node_distribution.data')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'amount_of_data_ratios.csv')

    print('Reading number of statement/reference nodes file ...')
    try:
        with open(input_data_file_nums, encoding="utf8") as file:
            df = pd.read_csv(
                file, usecols=['num of statement nodes', 'num of reference nodes'])
            num_statement_node = int(df['num of statement nodes'].iloc[0])
            num_ref_node = int(df['num of reference nodes'].iloc[0])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"num_of_statement_and_ref_nodes.data"'))
        exit(1)

    print('Reading triple per ref node distribution file ...')
    triple_dist = []
    try:
        with open(input_data_file_triple_dist, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                triple_dist.append(RefNodeOutgoing(row[0], int(row[1])))

    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"triple_per_ref_node_distribution.data"'))
        exit(1)

    print('Reading literal per ref node distribution file ...')
    literal_dist = []
    try:
        with open(input_data_file_literal_dist, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                literal_dist.append(RefNodeOutgoing(row[0], int(row[1])))

    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"literal_per_ref_node_distribution.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    amount_of_data_computer = AmountOfDataComputer(
        triple_dist,
        literal_dist,
        num_statement_node,
        num_ref_node
    )
    write_results_to_CSV(str(amount_of_data_computer), output_file_result)
    end_time = datetime.datetime.now()

    # saving the results for presentation layer

    print(
        'Dimension: Amount-of-Data results have been written in the file: {0}'.format(output_file_result))
    print('DONE. Dimension: Amount-of-Data, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_external_uris_length(opts: ArgumentParser) -> int:
    print('Started computing Metric: External Sources URL Length')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'url_length.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'url_length_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                uris.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_uris.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    length_computer = ExternalURLLengthChecking(uris)
    results = length_computer.count_length_scores()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(length_computer), output_file_result)

    print('Metric: External Sources URL Length results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: External Sources URL Length, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_property_diversity(opts: ArgumentParser) -> int:
    print('Started computing Metric: Diversity of Reference Properties')
    input_data_file_nums = os.path.join(
        opts.data_dir + os.sep + 'num_of_ref_props_and_ref_triples.data')
    input_data_file_dist = os.path.join(
        opts.data_dir + os.sep + 'reference_property_usage_distribution.data')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'ref_properties_diversity_ratios.csv')

    print('Reading number of properties/triples file ...')
    try:
        with open(input_data_file_nums, encoding="utf8") as file:
            df = pd.read_csv(
                file, usecols=['num of ref properties', 'num of ref triples'])
            num_ref_prop = int(df['num of ref properties'].iloc[0])
            num_ref_triple = int(df['num of ref triples'].iloc[0])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"num_of_ref_props_and_ref_triples.data"'))
        exit(1)

    print('Reading ref property usage distribution file ...')
    usage_dist = []
    try:
        with open(input_data_file_dist, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                usage_dist.append(RefPropInstances(row[0], int(row[1])))

    except FileNotFoundError:
        print("Error: Input data file not found. Provide input data file with name: {0} in data_dir".format(
            '"reference_property_usage_distribution.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    diversity_computer = RefPropertyDiversityComputer(
        usage_dist,
        num_ref_prop,
        num_ref_triple
    )
    write_results_to_CSV(str(diversity_computer), output_file_result)
    end_time = datetime.datetime.now()

    # saving the results for presentation layer

    print(
        'Metric: Diversity of Reference Properties results have been written in the file: {0}'.format(output_file_result))
    print('DONE. Metric: Diversity of Reference Properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_human_readable_metadata(opts: ArgumentParser) -> int:
    print('Started computing Metrics: Human-readable Labeling and Human-readable Commenting of Reference Properties')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'human_readable_metadata.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'human_readable_metadata_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    props = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                props.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"ref_properties.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    metadata_checker = HumanReadableMetadataChecker(props)
    results = metadata_checker.check_labels_comments_existance_from_Wikdiata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(metadata_checker), output_file_result)

    print('Metrics: Human-readable Labeling and Human-readable Commenting of Reference Properties results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metrics: Human-readable Labeling and Human-readable Commenting of Reference Properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_handy_external_sources(opts: ArgumentParser) -> int:
    print('Started computing Metrics: Handy External Sources')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_sources.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'handy_external_sources.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'handy_external_sources_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    srcs = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                srcs.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"external_sources.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    handy_checker = HandyExternalSourcesChecker(srcs)
    results = handy_checker.check_handy_external_sources_wikidata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(handy_checker), output_file_result)

    print('Metrics: Handy External Sources results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metrics: Handy External Sources, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_blank_node_usage(opts: ArgumentParser) -> int:
    print('Started computing Metric: Usage of Blank Nodes')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'blank_node_result.csv')

    # running the framework metric function
    if not opts.endpoint:
        print('ERROR: Usage of Blank Nodes needs endpoint. Specify an SPARQL endpoint with --endpoint arg.')
        return -1
    print('Running metric ...')
    start_time = datetime.datetime.now()
    bn_checker = None
    bn_checker = BlankNodeChecker(opts.endpoint)
    results = bn_checker.check_blank_nodes_over_endpoint()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if results is not None:
        write_results_to_CSV(str(bn_checker), output_file)

    print('Metric: Usage of Blank Nodes results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Usage of Blank Nodes, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_multilingual_metadata(opts: ArgumentParser) -> int:
    print('Started computing Metrics: Multilingual Labeling and Multilingual Commenting of Reference Properties')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties.data')
    output_file_dist = os.path.join(
        opts.output_dir + os.sep + 'multilingual_metadata.csv')
    output_file_result = os.path.join(
        opts.output_dir + os.sep + 'multilingual_metadata_ratio.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    props = []
    try:
        with open(input_data_file, encoding="utf8") as file:
            for line in file:
                props.append(line.rstrip())
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"ref_properties.data"'))
        exit(1)
    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    ml_checker = MultilingualMetadataChecker(props)
    results = ml_checker.check_multilingual_existance_from_Wikdiata()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(results) > 0:
        write_results_to_CSV(results, output_file_dist)
        write_results_to_CSV(str(ml_checker), output_file_result)

    print('Metrics: Multilingual Labeling and Multilingual Commenting of Reference Properties results have been written in the file: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metrics: Multilingual Labeling and Multilingual Commenting of Reference Properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_multilingual_sources_facts(opts: ArgumentParser) -> int:
    print('Started computing Metrics: Multilingual Sources and Multilingual Referenced Facts')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_source.data')
    output_file_sources_ml_dist = os.path.join(
        opts.output_dir + os.sep + 'sources_multilingualism.csv')
    output_file_facts_ml_dist = os.path.join(
        opts.output_dir + os.sep + 'facts_multilingualism.csv')
    output_file_ml_result = os.path.join(
        opts.output_dir + os.sep + 'sources_facts_multilingualism_ratio.csv')

    # reading the properties/literals
    print('Reading data ...')
    statements_ref_vals: Dict = {}
    try:
        with open(input_data_file, encoding="utf8") as file:
            reader = csv.reader(file)
            for row in reader:
                if row[0] not in statements_ref_vals.keys():
                    statements_ref_vals[row[0]] = []
                statements_ref_vals[row[0]].append(row[1])
    except FileNotFoundError:
        print("Error: Input data file not found. Provide data file with name: {0} in data_dir".format(
            '"statement_source.data"'))
        exit(1)

    # running the framework metric function
    print('Running metric ...')
    start_time = datetime.datetime.now()
    fact_source_ml_checker = MultilingualFactsAndSourcesChecker(
        statements_ref_vals)
    source_dist, facts_dist = fact_source_ml_checker.check_fact_sources_multilingualism()
    end_time = datetime.datetime.now()

    # saving the results for presentation layer
    if len(source_dist) > 0:
        write_results_to_CSV(source_dist, output_file_sources_ml_dist)
    if len(facts_dist) > 0:
        write_results_to_CSV(facts_dist, output_file_facts_ml_dist)
    write_results_to_CSV(str(fact_source_ml_checker), output_file_ml_result)

    print('Metrics: Multilingual Sources and Multilingual Referenced Facts results have been written in the files: {0} and {1} and {2}'.format(
        output_file_sources_ml_dist, output_file_facts_ml_dist, output_file_ml_result))
    print('DONE. Metrics: Multilingual Sources and Multilingual Referenced Facts, Duration: {0}'.format(
        end_time - start_time))
    return 0


def RQSS_Framework_Runner(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])

    # checking existance of the input data directory
    opts.data_dir = Path(opts.data_dir)
    if not opts.data_dir.is_dir():
        print('The data directory "{0}" not existed.'.format(opts.data_dir))
        return 1
    opts.data_dir = str(opts.data_dir.resolve(strict=True))

    # creating the output destination directory
    print('Creating output directory: {0}'.format(opts.output_dir))
    Path(opts.output_dir).mkdir(parents=True, exist_ok=True)

    # list of parallel processes
    framework_procs = []

    if opts.dereferencing:
        p = Process(target=compute_dereferencing(opts))
        framework_procs.append(p)
    if opts.licensing:
        p = Process(target=compute_licensing(opts))
        framework_procs.append(p)
    if opts.security:
        p = Process(target=compute_security(opts))
        framework_procs.append(p)
    if opts.interlinking:
        p = Process(target=compute_interlinking(opts))
        framework_procs.append(p)
    if opts.ref_triple_syntax:
        p = Process(target=compute_ref_triple_syntax(opts))
        framework_procs.append(p)
    if opts.ref_literal_syntax:
        p = Process(target=compute_ref_literal_syntax(opts))
        framework_procs.append(p)
    if opts.ref_triple_semantic:
        p = Process(target=compute_ref_triple_semantic(opts))
        framework_procs.append(p)
    if opts.ref_property_consistency:
        p = Process(target=compute_ref_properties_consistency(opts))
        framework_procs.append(p)
    if opts.range_consistency:
        p = Process(target=compute_range_consistency(opts))
        framework_procs.append(p)
    if opts.ref_sharing:
        p = Process(target=compute_ref_sharing_ratio(opts))
        framework_procs.append(p)
    if opts.reputation:
        p = Process(target=compute_dnsbl_reputation(opts))
        framework_procs.append(p)
    if opts.multiple_ref:
        p = Process(target=compute_multiple_referenced(opts))
        framework_procs.append(p)
    if opts.human_added:
        p = Process(target=compute_human_added_references_per_item(opts))
        framework_procs.append(p)
    if opts.type_of_sources:
        p = Process(target=compute_verifiable_type_of_sources(opts))
        framework_procs.append(p)
    if opts.ref_freshness:
        p = Process(
            target=compute_referenced_facts_reference_freshness_per_item(opts))
        framework_procs.append(p)
    if opts.ext_uris_freshness:
        p = Process(target=compute_external_uris_freshness(opts))
        framework_procs.append(p)
    if opts.ext_uris_volatility:
        p = Process(target=compute_external_uris_volatility(opts))
        framework_procs.append(p)
    if opts.ext_uris_timeliness:
        p = Process(target=compute_external_uris_timeliness(opts))
        framework_procs.append(p)
    if opts.class_property_schema_completeness:
        p = Process(target=compute_class_property_schema_completeness(opts))
        framework_procs.append(p)
    if opts.schema_based_property_completeness:
        p = Process(target=compute_schema_based_property_completeness(opts))
        framework_procs.append(p)
    if opts.property_completeness:
        p = Process(target=compute_property_completeness(opts))
        framework_procs.append(p)
    if opts.amount_of_data:
        p = Process(target=compute_amount_of_data(opts))
        framework_procs.append(p)
    if opts.ext_uri_length:
        p = Process(target=compute_external_uris_length(opts))
        framework_procs.append(p)
    if opts.ref_property_diversity:
        p = Process(target=compute_ref_property_diversity(opts))
        framework_procs.append(p)
    if opts.human_readable_metadata:
        p = Process(target=compute_human_readable_metadata(opts))
        framework_procs.append(p)
    if opts.handy_external_sources:
        p = Process(target=compute_handy_external_sources(opts))
        framework_procs.append(p)
    if opts.blank_node:
        p = Process(target=compute_blank_node_usage(opts))
        framework_procs.append(p)
    if opts.multilingual_metadata:
        p = Process(target=compute_multilingual_metadata(opts))
        framework_procs.append(p)
    if opts.multilingual_sources_facts:
        p = Process(target=compute_multilingual_sources_facts(opts))
        framework_procs.append(p)

    for proc in framework_procs:
        proc.start()

    for proc in framework_procs:
        proc.join()


if __name__ == '__main__':
    RQSS_Framework_Runner(sys.argv[1:])
