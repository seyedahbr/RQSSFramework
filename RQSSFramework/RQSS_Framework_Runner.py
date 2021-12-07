import csv
import os
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional, Union

from SPARQLWrapper import JSON, SPARQLWrapper

from RQSSFramework.Availability.DereferencePossibility import DerefrenceExplorer
from RQSSFramework.Licensing.LicenseExistanceChecking import LicenseChecker
from RQSSFramework.Queries import RQSS_QUERIES
from RQSSFramework.Security.TLSExistanceChecking import TLSChecker


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument(
        "data_dir", help="Input data directory that includes initial collections like facts, properties, literals, external sources, etc.")
    parser.add_argument(
        "-o", "--output_dir", help="Output destination directory to store computed metrics details", default=os.getcwd()+os.sep+'rqss_framework_output')
    parser.add_argument("-dp", "--dereferencing",
                        help="Compute the metric: Dereference Possibility of the External URIs", action='store_true')
    parser.add_argument("-l", "--licensing",
                        help="Compute the metric: External Sources’ Datasets Licensing", action='store_true')
    parser.add_argument("-sec", "--security",
                        help="Compute the metric: Link Security of the External URIs", action='store_true')
    
    return parser

def write_results_to_CSV(results: List[NamedTuple], output_file: str) -> None:
    if len(results) == 0: return
    with open(output_file, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow([field for field in results[0]._fields])    # write header from NamedTuple fields
        for result in results:
            row = []
            for field in result._fields:
                row.append(result._asdict()[field])
            w.writerow(row)

    
def compute_dereferencing(opts: ArgumentParser) -> int:
    print('Started computing Metric: Dereference Possibility of the External URIs')
    input_data_file = os.path.join(opts.data_dir + os.sep + 'external_uris.data')
    output_file = os.path.join(opts.output_dir + os.sep + 'dereferencing.csv')

    # reading the extracted External URIs
    print('Reading data ...')
    uris = []
    with open(input_data_file) as file:
        for line in file:
            uris.append(line.rstrip())

    # running the framework metric function
    print('Running metric ...')
    start_time=datetime.now()
    results = DerefrenceExplorer(uris).check_dereferencies()
    end_time=datetime.now()

    # saving the results for presentation layer
    # with open(output_file, 'w') as f:
    #     w = csv.writer(f)
    #     w.writerow([field.replace("_", "").title() for field in DerefOfURI._fields])    # write header from NamedTuple fields
    #     for result in results:
    #         row = []
    #         for field in DerefOfURI._fields:
    #             row.append(results[field.replace("_", "").title()])
    #         w.writerow(row)



    time.sleep(2)
    print('Metric: Dereference Possibility of the External URIs results have been written in the file: {0}'.format(output_file))
    print('DONE. Metric: Dereference Possibility of the External URIs, Duration: {0}'.format(end_time - start_time))
    return 0

def compute_licensing(opts: ArgumentParser) -> int:
    print('Started computing Metric: External Sources’ Datasets Licensing')
    start_time=datetime.now()
    output_file=''
    time.sleep(2)
    end_time=datetime.now()
    print('Metric: External Sources’ Datasets Licensing results have been written in the file: {0}'.format(output_file))
    print('DONE. Metric: External Sources’ Datasets Licensing, Duration: {0}'.format(end_time - start_time))
    return 0

def compute_security(opts: ArgumentParser) -> int:
    print('Started computing Metric: Link Security of the External URIs')
    start_time=datetime.now()
    output_file=''
    time.sleep(2)
    end_time=datetime.now()
    print('Metric: Link Security of the External URIs results have been written in the file: {0}'.format(output_file))
    print('DONE. Metric: Link Security of the External URIs, Duration: {0}'.format(end_time - start_time))
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
    opts.data_dir = opts.data_dir.resolve(strict=True)

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
    
    for proc in framework_procs:
        proc.start()
    
    for proc in framework_procs:
        proc.join()
    
if __name__ == '__main__':
    RQSS_Framework_Runner(sys.argv[1:])
