# RQSS-Framework
**Referencing Quality Scoring System - RQSS** is a data quality assessment framework implemented to measure the quality of Wikidata references. RQSS is based on a comprehensive referencing quality assessment framework with 40 data quality metrics on 21 data quality dimensions. In this repository, the objective metrics of the framework (34 out of 40) have been implemented. The formal definitions of the metrics and a comprehensive analysis of Wikidata referencing scores in 7 topical and random subsets of Wikidata can be found in the repo's paper: [RQSS: Referencing Quality Scoring System for Wikidata](https://www.semantic-web-journal.net/system/files/swj3593.pdf).

## Input/Output
RQSS gets an RDF graph based on the [Wikidata data model](https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format) as the **input**. In version 1.0.2, the input graph should be accessible on a local/public SPARQL endpoint.

RQSS also requires access to the Internet for receiving **metadata** from the SPARQL endpoint, history pages, and EntitySchemas of Wikidata.

RQSS produce two kinds of **output**:

1. The computed quality scores as numbers between 0 and 1, along with the distribution of results in some metrics.
1. Graphical charts (bar, box and whisker, pie, etc.) to provide a high level view of the scores and/or distributions.

## How to Deploy RQSS
RQSS is a modular framework, thus its implemented metrics can be called independently.

First, a local endpoint should be placed on the RDF data. We recommend using Blazegraph. Other triplestores, such as Jena Fuseki or GraphDB can be used as well. Suppose the dataset is available over a triplestore endpoint with the following address: `http://localhost:9999/blazegraph/sparql`

Based on what metric is desired to be computed, the process may be started by calling the Extractor to fetch the initial metadata from the dataset/Wikidata. Then the Framework_Runner is called and finally, the presenter might be deployed.

### Compute all of the metrics
To compute all of the metrics at once, run the following command from the repo directory to extract all required metadata (note that depending on the size of the dataset and the performance of the host, extracting some of the metadata can take a long time and high disk space):

```
$ python RQSSFramework/RQSS_Extractor.py --endpoint http://localhost:9999/blazegraph/sparql -eu -sn -l -fr -rp -rpvt -ri -sr -irf -wes -cf -sfr -aof -pu -es -ss
```

The output of the Extractor now should be in `./rqss_extractor_output/` directory as `.data` files. Then, call the Framework-Runner with all options such as below:

```
$ python RQSSFramework/RQSS_Framework_Runner.py ./rqss_extractor_output/ --endpoint http://localhost:9999/blazegraph/sparql -dp -l -sec -i -rts -rls -rtm -rpc -rc -rs -rdns -mr -ha -ts -rf -ef --extract-google-cache -ev -et -cpsc -sbpc -pc -aof -el -rpd -hm -he -bn -mm -mfs
```

Now, the scores and distributions (if applicable) can be seen in the `./rqss_framework_output` directory as `.csv` files (score files have a `_ratio` at the end of their filenames).

If graphical charts are desired, deploy the presenter as follows:

```
$ python RQSSFramework/RQSS_Presenter.py ./rqss_framework_output
```

Then, the `.png` files can be found in the `rqss_presenter_output` directory.

### Compute individual metrics
RQSS metrics can be computed separately. To compute a metric, first look at the `--help` of the  `RQSSFramework/RQSS_Framework_Runner.py` to obtain the name of the metric. Then see the `--help` of the  `RQSSFramework/RQSS_Extractor.py` to check whether computing the metric need to fetch any metadata first. For example, to compute the Availability of External URIs, the help of the extractor tells us we need to obtain all external source URLs in the input graph. So we call this command:
```
$ python ./RQSSFramework/RQSS_Extractor.py --endpoint http://localhost:9999/blazegraph/sparql --external-uris
```
Then, we call the Framework_Runner as below:
```
$ python RQSSFramework/RQSS_Framework_Runner.py ./rqss_extractor_output/ --dereferencing
```
And then, to have the graphical chart, the Presenter can be called:
```
$ python RQSSFramework/RQSS_Presenter.py ./rqss_framework_output
```

## Repo Structure
The main part of the framework code is located in the RQSSFramework package. In this directory, there is a package corresponding to each dimension of the framework, in which Python files have implemented one or more metrics. In addition to the dimensions and metrics packages, the following scripts and files exist in the RQSSFramework package:

- `entityschemaextractor.py`: To fetch the most up-to-date EntitySchemas and their referencing information from Wikidata website
- `Queries.py`: SPARQL queries used in the Extractor and the Framework_Runner
- `RQSS_Extractor.py`: The Extractor module
- `RQSS_Framework_Runner.py`: The metric computer module
- `RQSS_Presenter.py`: The graphical chart representer module
- `ShExes.py`: The ShEx schemas used in consistency and other dimensions


In addition, the `utils` directory in the RQSSFramework package contains the following scripts: 

- `item_overlap_checker.py`: The script is used to identify the overlapping items amongst randomly chosen subsets
- `lists.py`: Contains the list of datasets, licensing keywords, and any other set of literal values used in the Framework Runner
- `topic_coverage.py`: This script is used to compute the main high-level classes of items in a subset (the topics the subset covers).


## More details
See the `README.md` inside the RQSSFramework.