import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Union

from SPARQLWrapper import JSON, SPARQLWrapper

from Queries import RQSS_QUERIES


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    
    return parser


def RQSS_Framework_Runner(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])


if __name__ == '__main__':
    RQSS_Framework_Runner(sys.argv[1:])
