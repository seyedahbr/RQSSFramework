import sys
import os
import pandas as pd
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import Iterator, List, NamedTuple, Optional, Union

from RQSSFramework.Availability.DereferencePossibility import DerefOfURI
from RQSSFramework.Licensing.LicenseExistanceChecking import LicExistOfDom
from RQSSFramework.Security.TLSExistanceChecking import TLSExist


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument(
        "result_dir", help="Input data directory that includes the results of the framework metrics in CSV files")
    parser.add_argument(
        "-o", "--output_dir", help="Output destination directory to store charts", default=os.getcwd()+os.sep+'rqss_presenter_output')

    return parser


def box_whisker_plot(data, x_row: str, y_col: str, output: str) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns
    box_plot = sns.boxplot(data=data, y=y_col, showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"},
                           medianprops={'color': 'red'},
                           flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel(x_row)
    box_plot.set_ylabel(y_col)
    plt.savefig(output , format='png')
    plt.close()


def plot_dereferencing(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'dereferencing.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'dereferencing.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    # convert True and False to 1 and 0
    csv_data[str(DerefOfURI._fields[1])] = (csv_data[str(DerefOfURI._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Derefrence Possibility', str(DerefOfURI._fields[1]), output_file)
    
    print('Metric: Dereference Possibility of the External URIs chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0

def plot_licensing(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'licensing.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'licensing.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(LicExistOfDom._fields[1])] = (csv_data[str(LicExistOfDom._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Licensing', str(LicExistOfDom._fields[1]), output_file)
    
    print('Metric: External Sources’ Datasets Licensing chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0

def plot_security(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'security.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'security.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(TLSExist._fields[1])] = (csv_data[str(TLSExist._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Security', str(TLSExist._fields[1]), output_file)
    
    print('Metric: Link Security of the External URIs chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def RQSS_Plot(argv: Optional[Union[str, List[str]]] = None, prog: Optional[str] = None) -> int:
    if isinstance(argv, str):
        argv = argv.split()
    opts = genargs(prog).parse_args(argv if argv is not None else sys.argv[1:])

    # checking existance of the input data directory
    opts.result_dir = Path(opts.result_dir)
    if not opts.result_dir.is_dir():
        print('The data directory "{0}" not existed.'.format(opts.result_dir))
        return 1
    opts.result_dir = str(opts.result_dir.resolve(strict=True))

    # creating the output destination directory
    print('Creating output directory: {0}'.format(opts.output_dir))
    Path(opts.output_dir).mkdir(parents=True, exist_ok=True)

    # list of parallel processes
    framework_procs = []

    if Path(opts.result_dir + os.sep + 'dereferencing.csv').is_file():
        p = Process(target=plot_dereferencing(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'licensing.csv').is_file():
        p = Process(target=plot_licensing(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'security.csv').is_file():
        p = Process(target=plot_security(opts))
        framework_procs.append(p)

    for proc in framework_procs:
        proc.start()

    for proc in framework_procs:
        proc.join()


if __name__ == '__main__':
    RQSS_Plot(sys.argv[1:])
