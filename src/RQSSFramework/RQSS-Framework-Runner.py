import os
import sys
import time
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import List, Optional, Union

from SPARQLWrapper import JSON, SPARQLWrapper

from Queries import RQSS_QUERIES


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

def compute_dereferencing() -> int:
    print('Started computing Metric: Dereference Possibility of the External URIs')
    start_time=datetime.now()
    output_file=''
    time.sleep(2)
    end_time=datetime.now()
    print('Metric: Dereference Possibility of the External URIs results have been written in the file: {0}'.format(output_file))
    print('DONE. Metric: Dereference Possibility of the External URIs, Duration: {0}'.format(end_time - start_time))
    return 0

def compute_licensing() -> int:
    print('Started computing Metric: External Sources’ Datasets Licensing')
    start_time=datetime.now()
    output_file=''
    time.sleep(2)
    end_time=datetime.now()
    print('Metric: External Sources’ Datasets Licensing results have been written in the file: {0}'.format(output_file))
    print('DONE. Metric: External Sources’ Datasets Licensing, Duration: {0}'.format(end_time - start_time))
    return 0

def compute_security() -> int:
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
        p = Process(target=compute_dereferencing)
        framework_procs.append(p)
    if opts.licensing:
        p = Process(target=compute_licensing)
        framework_procs.append(p)
    if opts.security:
        p = Process(target=compute_security)
        framework_procs.append(p)
    
    for proc in framework_procs:
        proc.start()
    
    for proc in framework_procs:
        proc.join()
    
if __name__ == '__main__':
    RQSS_Framework_Runner(sys.argv[1:])
