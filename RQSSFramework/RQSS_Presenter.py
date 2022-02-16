import sys
import os
import pandas as pd
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import List, Optional, Union

from Availability.DereferencePossibility import DerefOfURI
from Licensing.LicenseExistanceChecking import LicExistOfDom
from Security.TLSExistanceChecking import TLSExist
from Consistency.RefPropertiesConsistencyChecking import PropConsistencyResult
from Reputation.DNSBLBlacklistedChecking import BlacklistedOfDom


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument(
        "result_dir", help="Input data directory that includes the results of the framework metrics in CSV files")
    parser.add_argument(
        "-o", "--output_dir", help="Output destination directory to store charts", default=os.getcwd()+os.sep+'rqss_presenter_output')

    return parser


def box_whisker_plot(data, x_row: str, y_col: str, output: str, x_col: str = None) -> None:
    import matplotlib.pyplot as plt
    import seaborn as sns
    box_plot = sns.boxplot(data=data, y=y_col, x=x_col, showmeans=False, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"},
                           medianprops={'color': 'red'},
                           flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel(x_row)
    box_plot.set_ylabel(y_col)
    if len(box_plot.get_xticklabels()) > 1:
        means = data.groupby('variable', as_index=False)['value'].mean()
        ctr = 0
        for col in box_plot.get_xticklabels():
            mean = float(means.loc[means['variable'] == col.get_text(), 'value'].iloc[0])
            box_plot.text(box_plot.get_xticks()[ctr], mean, 'Avg: {0}'.format(round(mean, 2)),
                          horizontalalignment='center', size='x-small', color='black', weight='semibold')
            ctr += 1
    else:
        box_plot.text(box_plot.get_xticks()[0], data[y_col].mean(), 'Avg:{0}'.format(round(data[y_col].mean(), 2)),
                      horizontalalignment='center', size='x-small', color='black', weight='semibold')
    #box_plot.set(ylim=(0, 1))
    sns.despine(trim=True)
    plt.savefig(output, format='png')
    plt.close()


def plot_dereferencing(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'dereferencing.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'dereferencing.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    # convert True and False to 1 and 0
    csv_data[str(DerefOfURI._fields[1])] = (
        csv_data[str(DerefOfURI._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Derefrence Possibility',
                     str(DerefOfURI._fields[1]), output_file)

    print('Metric: Dereference Possibility of the External URIs chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_licensing(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'licensing.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'licensing.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(LicExistOfDom._fields[1])] = (
        csv_data[str(LicExistOfDom._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Licensing', str(
        LicExistOfDom._fields[1]), output_file)

    print('Metric: External Sources’ Datasets Licensing chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_security(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'security.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'security.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(TLSExist._fields[1])] = (
        csv_data[str(TLSExist._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Security', str(
        TLSExist._fields[1]), output_file)

    print('Metric: Link Security of the External URIs chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_literal_syntax(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'ref_literal_syntax.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_literal_syntax.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['accuracy rate'] = 1 - csv_data['fails']/csv_data['total']
    csv_data['error rate'] = csv_data['errors']/csv_data['total']
    csv_data['not exists rate'] = csv_data['not_exixts']/csv_data['total']
    box_whisker_plot(pd.melt(csv_data[['accuracy rate', 'error rate', 'not exists rate']]),
                     'Syntax Validity of Reference Literals and Regex Errors', 'value', output_file, 'variable')

    print('Metric: Syntactic validity of references’ literals chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_semantic_accuracy(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'semantic_validity.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'seamntic_accuracy.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['accuracy rate'] = csv_data['full_matches'] / \
        csv_data['half_matches']
    box_whisker_plot(pd.melt(csv_data[['accuracy rate']]),
                     'Semantic Valididty of Reference Triples', 'value', output_file, 'variable')

    print('Metric: Semantic validity of reference triples chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_ref_properties_consistency(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'ref_properties_consistency.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_properties_consistency.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(PropConsistencyResult._fields[1])] = (
        csv_data[str(PropConsistencyResult._fields[1])] == True).astype(int)
    box_whisker_plot(csv_data, 'Reference Properties Consistency', str(
        PropConsistencyResult._fields[1]), output_file)

    print('Metric: Consistency of references’ properties chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_range_consistency(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'range_consistency.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'range_consistency.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['consistency rate'] = 1 - csv_data['fails']/csv_data['total']
    csv_data['not exixts rate'] = csv_data['not_exixts']/csv_data['total']
    box_whisker_plot(pd.melt(csv_data[['consistency rate', 'not exixts rate']]),
                     'Range consistency of reference triples and not exist range rate', 'value', output_file, 'variable')

    print('Metric: Range consistency of reference triples chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0

def plot_ref_sharing_conciseness(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'ref_sharing.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'ref_sharing.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    box_whisker_plot(csv_data,
                     'Reference Sharing Ratio', 'num_of_incomes', output_file)

    print('Metric: Ratio of reference sharing chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0

def plot_dnsbl_reputation(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'dnsbl_reputation.csv')
    output_file = os.path.join(opts.output_dir + os.sep + 'dnsbl_reputation.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(BlacklistedOfDom._fields[1])] = (
        csv_data[str(BlacklistedOfDom._fields[1])] == False).astype(int) # consider False as good result
                                                                         # note: False means the domain is not blacklisted 
    box_whisker_plot(csv_data, 'DNS Reputation', str(
        BlacklistedOfDom._fields[1]), output_file)

    print('Metric: External sources’ domain reputation chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0

def plot_multiple_reference_objectivity(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'multiple_refs.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'multiple_refs.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    box_whisker_plot(csv_data,
                     'Multiple Referenced Ratio', 'num_of_refs', output_file)

    print('Metric: Multiple references for facts chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0

def plot_human_added_references_believbility(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'human_added.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'believbility.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['believbility rate'] = csv_data['human_added'] / \
        csv_data['total']
    box_whisker_plot(pd.melt(csv_data[['believbility rate']]),
                     'Semantic Valididty of Reference Triples', 'value', output_file, 'variable')

    print('Metric: Human-added references ratio chart(s) have been plotted in the file: {0}'.format(
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
    if Path(opts.result_dir + os.sep + 'ref_literal_syntax.csv').is_file():
        p = Process(target=plot_literal_syntax(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'semantic_validity.csv').is_file():
        p = Process(target=plot_semantic_accuracy(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'ref_properties_consistency.csv').is_file():
        p = Process(target=plot_ref_properties_consistency(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'range_consistency.csv').is_file():
        p = Process(target=plot_range_consistency(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'ref_sharing.csv').is_file():
        p = Process(target=plot_ref_sharing_conciseness(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'dnsbl_reputation.csv').is_file():
        p = Process(target=plot_dnsbl_reputation(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'multiple_refs.csv').is_file():
        p = Process(target=plot_multiple_reference_objectivity(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'human_added.csv').is_file():
        p = Process(target=plot_human_added_references_believbility(opts))
        framework_procs.append(p)

    for proc in framework_procs:
        proc.start()

    for proc in framework_procs:
        proc.join()


if __name__ == '__main__':
    RQSS_Plot(sys.argv[1:])
