import sys
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional, Union


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument("--first", help="First Q-id file", required=True)
    parser.add_argument("--second", help="Second Q-id file", required=True)
    return parser


def check_overlap_line_by_line(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])
    opts.first = Path(opts.first)
    opts.second = Path(opts.second)
    if not opts.first.is_file():
        print('File not existed: {0}'.format(opts.first))
        return 1
    if not opts.second.is_file():
        print('File not existed: {0}'.format(opts.second))
        return 1
    with open(opts.first) as file_1:
        lines_1 = file_1.readlines()
    with open(opts.second) as file_2:
        lines_2 = file_2.readlines()
    intersects = 0
    for i in lines_1:
        for j in lines_2:
            if i == j:
                intersects += 1
                break
    print('Num of Intersections: {0}'.format(intersects))


if __name__ == '__main__':
    check_overlap_line_by_line(sys.argv[1:])
