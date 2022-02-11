import csv
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import List, NamedTuple, Optional, Union

from Accuracy.LiteralSyntaxChecking import WikibaseRefLiteralSyntaxChecker
from Accuracy.TripleSemanticChecking import (FactReference,
                                             RefTripleSemanticChecker)
from Accuracy.TripleSyntaxChecking import WikibaseRefTripleSyntaxChecker
from Availability.DereferencePossibility import DerefrenceExplorer
from Conciseness.ReferenceSharingChecking import *
from Consistency.RefPropertiesConsistencyChecking import \
    RefPropertiesConsistencyChecker
from Consistency.TriplesRangeConsistencyChecking import \
    TriplesRangeConsistencyChecker
from Licensing.LicenseExistanceChecking import LicenseChecker
from Objectivity.MultipleReferenceChecking import *
from Queries import RQSS_QUERIES
from Reputation.DNSBLBlacklistedChecking import DNSBLBlacklistedChecker
from Security.TLSExistanceChecking import TLSChecker


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument(
        "data_dir", help="Input data directory that includes initial collections like facts, properties, literals, external sources, etc.")
    parser.add_argument(
        "--endpoint", help="The local/public endpoint of the dataset for shex-based metrics", required=False)
    parser.add_argument(
        "-o", "--output_dir", help="Output destination directory to store computed metrics details", default=os.getcwd()+os.sep+'rqss_framework_output')
    parser.add_argument("-dp", "--dereferencing",
                        help="Compute the metric: Dereference Possibility of the External URIs", action='store_true')
    parser.add_argument("-l", "--licensing",
                        help="Compute the metric: External Sources’ Datasets Licensing", action='store_true')
    parser.add_argument("-sec", "--security",
                        help="Compute the metric: Link Security of the External URIs", action='store_true')
    parser.add_argument("-rts", "--reftriplesyntax",
                        help="Compute the metric: Syntactic Validity of Reference Triples", action='store_true')
    parser.add_argument("-rls", "--refliteralsyntax",
                        help="Compute the metric: Syntactic validity of references’ literals", action='store_true')
    parser.add_argument("-rtm", "--reftriplesemantic",
                        help="Compute the metric: Semantic validity of reference triples", action='store_true')
    parser.add_argument("-rpc", "--refpropertyconsistency",
                        help="Compute the metric: Consistency of references’ properties", action='store_true')
    parser.add_argument("-rc", "--rangeconsistency",
                        help="Compute the metric: Range consistency of reference triples", action='store_true')
    parser.add_argument("-rs", "--refsharing",
                        help="Compute the metric: Ratio of reference sharing", action='store_true')
    parser.add_argument("-rdns", "--reputation",
                        help="Compute the metric: External sources’ domain reputation", action='store_true')
    parser.add_argument("-mr", "--mulipleref",
                        help="Compute the metric: Multiple references for facts", action='store_true')
    return parser


def write_results_to_CSV(results: List[NamedTuple], output_file: str) -> None:
    with open(output_file, 'w', newline='') as f:
        w = csv.writer(f)
        # write header from NamedTuple fields
        w.writerow([field for field in results[0]._fields])
        for result in results:
            row = [result._asdict()[field] for field in result._fields]
            w.writerow(row)
    return


def compute_dereferencing(opts: ArgumentParser) -> int:
    print('Started computing Metric: Dereference Possibility of the External URIs')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file = os.path.join(opts.output_dir + os.sep + 'dereferencing.csv')

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
    start_time = datetime.now()
    results = DerefrenceExplorer(uris).check_dereferencies()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: Dereference Possibility of the External URIs results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Dereference Possibility of the External URIs, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_licensing(opts: ArgumentParser) -> int:
    print('Started computing Metric: External Sources’ Datasets Licensing')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file = os.path.join(opts.output_dir + os.sep + 'licensing.csv')

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
    start_time = datetime.now()
    results = LicenseChecker(uris).check_license_existance()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: External Sources’ Datasets Licensing results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: External Sources’ Datasets Licensing, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_security(opts: ArgumentParser) -> int:
    print('Started computing Metric: Link Security of the External URIs')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file = os.path.join(opts.output_dir + os.sep + 'security.csv')

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
    start_time = datetime.now()
    results = TLSChecker(uris).check_support_tls()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: Link Security of the External URIs results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Link Security of the External URIs, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_triple_syntax(opts: ArgumentParser) -> int:
    print('Started computing Metric: Syntactic Validity of Reference Triples')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'statement_nodes_uris.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_triple_syntax.csv')

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
    start_time = datetime.now()
    results = []
    if(opts.endpoint):
        results = WikibaseRefTripleSyntaxChecker(
            statements, opts.endpoint, None).check_shex_over_endpoint()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV([results], output_file)

    print('Metric: Syntactic Validity of Reference Triples results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Syntactic Validity of Reference Triples, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_literal_syntax(opts: ArgumentParser) -> int:
    print('Started computing Metric: Syntactic validity of references’ literals')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'reference_literals.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_literal_syntax.csv')

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
    start_time = datetime.now()
    results = WikibaseRefLiteralSyntaxChecker(
        prop_values).check_literals_regex()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: Syntactic validity of references’ literals results have been written in the file: {0}'.format(
        output_file))
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
    start_time = datetime.now()
    results = RefTripleSemanticChecker(
        gs_fact_refs, fact_refs).check_semantic_to_gold_standard()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: Syntactic validity of references’ literals results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Syntactic validity of references’ literals, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_ref_properties_consistency(opts: ArgumentParser) -> int:
    print('Started computing Metric: Consistency of references’ properties')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_properties_consistency.csv')

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
    start_time = datetime.now()
    results = RefPropertiesConsistencyChecker(
        props).check_reference_specificity_from_Wikdiata()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: Consistency of references’ properties results have been written in the file: {0}'.format(
        output_file))
    print('DONE. Metric: Consistency of references’ properties, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_range_consistency(opts: ArgumentParser) -> int:
    print('Started computing Metric: Range consistency of reference triples')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'ref_properties_object_value.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'range_consistency.csv')

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
    start_time = datetime.now()
    results = TriplesRangeConsistencyChecker(
        prop_values).check_all_value_ranges()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: Range consistency of reference triples results have been written in the file: {0}'.format(
        output_file))
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
    start_time = datetime.now()
    checker = ReferenceSharingChecker(ref_nodes)
    shared_refs = checker.count_seperate_shared_references()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(shared_refs, output_file_dist)
    write_results_to_CSV([checker.result], output_file_result)

    print('Metric: Ratio of reference sharing results have been written in the files: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Ratio of reference sharing, Duration: {0}'.format(
        end_time - start_time))
    return 0


def compute_dnsbl_reputation(opts: ArgumentParser) -> int:
    print('Started computing Metric: External sources’ domain reputation')
    input_data_file = os.path.join(
        opts.data_dir + os.sep + 'external_uris.data')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'dnsbl_reputation.csv')

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
    start_time = datetime.now()
    results = DNSBLBlacklistedChecker(uris).check_domain_blacklisted()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(results, output_file)

    print('Metric: External sources’ domain reputation results have been written in the file: {0}'.format(
        output_file))
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
    start_time = datetime.now()
    checker = MultipleReferenceChecker(statements)
    shared_refs = checker.count_seperate_multiple_referenced_statements()
    end_time = datetime.now()

    # saving the results for presentation layer
    write_results_to_CSV(shared_refs, output_file_dist)
    write_results_to_CSV([checker.result], output_file_result)

    print('Metric: Multiple references for facts results have been written in the files: {0} and {1}'.format(
        output_file_dist, output_file_result))
    print('DONE. Metric: Multiple references for facts, Duration: {0}'.format(
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
    if opts.reftriplesyntax:
        p = Process(target=compute_ref_triple_syntax(opts))
        framework_procs.append(p)
    if opts.refliteralsyntax:
        p = Process(target=compute_ref_literal_syntax(opts))
        framework_procs.append(p)
    if opts.reftriplesemantic:
        p = Process(target=compute_ref_triple_semantic(opts))
        framework_procs.append(p)
    if opts.refpropertyconsistency:
        p = Process(target=compute_ref_properties_consistency(opts))
        framework_procs.append(p)
    if opts.rangeconsistency:
        p = Process(target=compute_range_consistency(opts))
        framework_procs.append(p)
    if opts.refsharing:
        p = Process(target=compute_ref_sharing_ratio(opts))
        framework_procs.append(p)
    if opts.reputation:
        p = Process(target=compute_dnsbl_reputation(opts))
        framework_procs.append(p)
    if opts.mulipleref:
        p = Process(target=compute_multiple_referenced(opts))
        framework_procs.append(p)

    for proc in framework_procs:
        proc.start()

    for proc in framework_procs:
        proc.join()


if __name__ == '__main__':
    RQSS_Framework_Runner(sys.argv[1:])
