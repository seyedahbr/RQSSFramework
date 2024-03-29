import csv
import os
import sys
from argparse import ArgumentParser
from datetime import datetime
from multiprocessing.context import Process
from pathlib import Path
from typing import List, Optional, Union

import numpy as np
import pandas as pd

from Availability.DereferencePossibility import DerefOfURI
from Consistency.RefPropertiesConsistencyChecking import PropConsistencyResult
from Licensing.LicenseExistanceChecking import LicExistOfDom
from Reputation.DNSBLBlacklistedChecking import BlacklistedOfDom
from Security.TLSExistanceChecking import TLSExist


def genargs(prog: Optional[str] = None) -> ArgumentParser:
    parser = ArgumentParser(prog)
    parser.add_argument(
        "--result-dir", help="Input data directory that includes the results of the framework metrics in CSV files")
    parser.add_argument(
        "-o", "--output-dir", help="Output destination directory to store charts", default=os.getcwd()+os.sep+'rqss_presenter_output')

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
            mean = float(means.loc[means['variable'] ==
                                   col.get_text(), 'value'].iloc[0])
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


def plot_interlinking(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'interlinking.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'interlinking.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace(0, np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data['num_equivalent'], showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel(
        'Distribution of the number of reference properties equivalence')
    box_plot.set_ylabel("Number of equivalents\nin reference properties")
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Interlinking of Reference Properties chart(s) have been plotted in the file: {0}'.format(
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
    csv_data['not exists rate'] = 1 - csv_data['regexes']/csv_data['total']
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

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['consistency rate'] = 1 - csv_data['fails']/csv_data['total']
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data['consistency rate'], showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel(
        'Distribution of the consistency rate of the reference properties')
    box_plot.set_ylabel("Consistency Ratio")
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
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
    output_file = os.path.join(
        opts.output_dir + os.sep + 'dnsbl_reputation.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data[str(BlacklistedOfDom._fields[1])] = (
        csv_data[str(BlacklistedOfDom._fields[1])] == False).astype(int)  # consider False as good result
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
                     'Human-Added Reference Ratio', 'value', output_file, 'variable')

    print('Metric: Human-added references ratio chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_fact_referencing_freshness_currency(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'fact_freshness.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'fact_freshness.png')

    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['currency rate'] = csv_data['freshness'] / \
        csv_data['total']
    box_whisker_plot(pd.melt(csv_data[['currency rate']]),
                     'Fact Referencing Freshness', 'value', output_file, 'variable')

    print('Metric: Freshness of fact referencing chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_external_uris_freshness_currency(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'external_uris_freshness.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'external_uris_freshness.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace('<None>', np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data, showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel('Freshness of External URIs')
    box_plot.set_ylabel('Freshness')
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Freshness of external sources chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_external_uris_volatility(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'external_uris_volatility.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'external_uris_volatility.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace('<None>', np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data, showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel('Volatility of External URIs')
    box_plot.set_ylabel('Volatility')
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Volatility of external sources chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_external_uris_timeliness(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'external_uris_timeliness.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'external_uris_timeliness.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace('<None>', np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data, showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel('Timeliness of External URIs')
    box_plot.set_ylabel('Timeliness')
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Timeliness of external sources chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_class_properties_schema_completeness(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'class_property_schema_completeness.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'class_property_schema_completeness.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data['property completeness of class'] = csv_data['num_properties_with_defined_ref_schema'] / \
        csv_data['num_total_properties']
    csv_data.replace(0, np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data['property completeness of class'], showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel('Class and Property Completeness')
    box_plot.set_ylabel('Completeness')
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Class and Property Schema Completeness of References chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_schema_based_property_completeness(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'schema_based_property_completeness.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'schema_based_property_completeness.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    plt.figure(figsize=(5, 6))
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace(0, np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data['total_refed_instances_schema_based'], showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel(
        'Distribution of total referenced instances per requiered\n reference property (based on schema)')
    box_plot.set_ylabel('Num of referenced instances')
    sns.despine(trim=True)

    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Property Completeness of References chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_property_completeness(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'property_completeness.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'property_completeness.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace(0, np.nan, inplace=True)
    box_plot = sns.boxplot(palette=["#3498db", "#2ecc71"],
                           data=csv_data['total_refed'], showmeans=True, showfliers=False,
                           meanprops={"marker": "^",
                                      "markerfacecolor": "black",
                                      "markeredgecolor": "black",
                                      "markersize": "5"}, medianprops={'color': 'red'}, flierprops={"marker": "o", "markersize": "5"})
    box_plot.set_xlabel(
        'Distribution of total referenced instances per reference property')
    box_plot.set_ylabel('Num of referenced instances')
    sns.despine(trim=True)
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metric: Schema-based Property Completeness of References chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_human_readable_metadata(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'human_readable_metadata.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'human_readable_metadata.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace(0, np.nan, inplace=True)
    df_labels = csv_data[['num_label']].copy().rename(
        columns={'num_label': 'num'})
    df_labels['metric'] = 'Labels'
    df_labels['dataset'] = 'dataset'
    df_comments = csv_data[['num_comment']].copy().rename(
        columns={'num_comment': 'num'})
    df_comments['metric'] = 'Comments'
    df_comments['dataset'] = 'dataset'
    data_dist = pd.concat([df_labels, df_comments])
    ax = sns.boxplot(
        data=data_dist,
        x='dataset',
        y='num',
        hue='metric',
        showmeans=True,
        showfliers=True,
        meanprops={
            "marker": "^",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "markersize": "5"
        },
        medianprops={
            'color': 'red'
        },
        flierprops={
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "marker": "o",
            "markersize": "3"
        }
    )
    # ax.set_xticklabels(ax.get_xticklabels(),rotation=90)
    ax.set_ylabel('Number of labels/commnents')
    ax.set_xlabel('')
    plt.legend(frameon=True, title='Distribution')
    sns.despine(trim=True)
    plt.autoscale()
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metrics: Human-readable labeling and Commentting of Reference Properties chart(s) have been plotted in the file: {0}'.format(
        output_file))
    return 0


def plot_multilingual_metadata(opts: ArgumentParser) -> int:
    input_data_file = os.path.join(
        opts.result_dir + os.sep + 'multilingual_metadata.csv')
    output_file = os.path.join(
        opts.output_dir + os.sep + 'multilingual_metadata.png')

    import matplotlib.pyplot as plt
    import seaborn as sns
    csv_data = pd.read_csv(input_data_file, index_col=None, header=0)
    csv_data.replace(0, np.nan, inplace=True)
    df_labels = csv_data[['num_non_en_label']].copy().rename(
        columns={'num_non_en_label': 'num'})
    df_labels['metric'] = 'Labels'
    df_labels['dataset'] = 'dataset'
    df_comments = csv_data[['num_non_en_comment']].copy().rename(
        columns={'num_non_en_comment': 'num'})
    df_comments['metric'] = 'Comments'
    df_comments['dataset'] = 'dataset'
    data_dist = pd.concat([df_labels, df_comments])
    ax = sns.boxplot(
        data=data_dist,
        x='dataset',
        y='num',
        hue='metric',
        showmeans=True,
        showfliers=True,
        meanprops={
            "marker": "^",
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "markersize": "5"
        },
        medianprops={
            'color': 'red'
        },
        flierprops={
            "markerfacecolor": "black",
            "markeredgecolor": "black",
            "marker": "o",
            "markersize": "3"
        }
    )
    # ax.set_xticklabels(ax.get_xticklabels(),rotation=90)
    ax.set_ylabel('Number of non-English labels/commnents')
    ax.set_xlabel('')
    plt.legend(frameon=True, title='Distribution')
    sns.despine(trim=True)
    plt.autoscale()
    plt.savefig(output_file, format='png')
    plt.close()
    print('Metrics: Mutilingual labeling and Commentting of Reference Properties chart(s) have been plotted in the file: {0}'.format(
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
    if Path(opts.result_dir + os.sep + 'interlinking.csv').is_file():
        p = Process(target=plot_interlinking(opts))
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
    if Path(opts.result_dir + os.sep + 'fact_freshness.csv').is_file():
        p = Process(target=plot_fact_referencing_freshness_currency(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'external_uris_freshness.csv').is_file():
        p = Process(target=plot_external_uris_freshness_currency(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'external_uris_volatility.csv').is_file():
        p = Process(target=plot_external_uris_volatility(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'external_uris_timeliness.csv').is_file():
        p = Process(target=plot_external_uris_timeliness(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'class_property_schema_completeness.csv').is_file():
        p = Process(target=plot_class_properties_schema_completeness(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'schema_based_property_completeness.csv').is_file():
        p = Process(target=plot_schema_based_property_completeness(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'property_completeness.csv').is_file():
        p = Process(target=plot_property_completeness(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'human_readable_metadata.csv').is_file():
        p = Process(target=plot_human_readable_metadata(opts))
        framework_procs.append(p)
    if Path(opts.result_dir + os.sep + 'multilingual_metadata.csv').is_file():
        p = Process(target=plot_multilingual_metadata(opts))
        framework_procs.append(p)

    for proc in framework_procs:
        proc.start()

    for proc in framework_procs:
        proc.join()


if __name__ == '__main__':
    RQSS_Plot(sys.argv[1:])
