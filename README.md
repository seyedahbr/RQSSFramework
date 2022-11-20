# RQSS-Framework
**Referencing Quality Scoring System - RQSS** is a data quality assessment framework implemented to measure the quality of Wikidata references. RQSS is based on a comprehensive referencing quality assessment framework with 40 data quality metrics on 21 data quality dimensions. In this repository, 34 objective metrics of the framework have been implemented.

## Input/Output
RQSS gets an RDF graph based on the [Wikidata data model](https://www.mediawiki.org/wiki/Wikibase/Indexing/RDF_Dump_Format) as the **input**. In version 1.0.0, the input graph should be accessible on a local/public SPARQL endpoint.

The main **output** of RQSS is the calculated values of the metrics as numbers between 0 and 1. The Presentation Layer provides more graphical information to the user than the distribution of scores over properties, statements, etc.

## Layers
RQSS has three main layers: Extractor, Framework Runner, and Presenter. The pipeline starts with the Extractor, then computing metric scores via the Framework Runner and finishes with deploying the Presenter.

### Extractor Layer
The Extractor layer prepares the required collections for the Framework Runner layer. These collections are `.data` files of items, properties, statements, references, literals, external sources, etc. In version 1.0.0, collections can only be extracted from local or public SPARQL endpoints. The extractor obtains the collections by performing SPARQL queries on the endpoint. Note that using RQSS on public endpoints, you may face time-out or access restriction limits as the queries are time-consuming. To deploy the Extractor, use the `RQSSFramework/RQSS_Extractor.py` script:
```
usage: RQSS_Extractor.py [-h] (--input INPUT | --endpoint ENDPOINT) [-f FORMAT] [-o OUTPUT_DIR] [-eu] [-sn] [-l] [-fr] [-rp] [-rpvt] [-ri] [-sr] [-irf] [-wes] [-cf]
                         [-sfr] [-aof] [-pu] [-es] [-ss]

optional arguments:
  -h, --help            show this help message and exit
  --input INPUT         Input RDF file of the dataset
  --endpoint ENDPOINT   The local/public endpoint of the dataset
  -f FORMAT, --format FORMAT
                        Input file RDF format (nt, ttl)
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output destination directory to store extarcted components from the RDF input file
  -eu, --external-uris  Extract all external sources uris (Wikibase referencing model) and save them on output dir. Collects data for computing Dimensions:
                        Availability, Licensing, Security
  -sn, --statement-nodes
                        Extract all statement nodes uris (Wikibase referencing model) and save them on output dir. Collects data for computing Metric: Syntactic
                        Validity of Reference Triples
  -l, --literals        Extract all literal values in reference triples and save them on output dir. Collects data for computing Metric: Syntactic Validity of
                        References’ Literals
  -fr, --fact-ref-triples
                        Extract all facts and their reference triples and save them on output dir. Collects data for computing Metric: Semantic Validity of Reference
                        Triples
  -rp, --ref-properties
                        Extract all reference properties and save them on output dir. Collects data for computing Metric: Consistency of References’ Properties
  -rpvt, --ref-prop-value-type
                        Extract all reference properties and their object value types and save them on output dir. Collects data for computing Metric: Range
                        Consistency of Reference Triples
  -ri, --ref-incomings  Extract all reference nodes and the numebr of their incoming edges (prov:wasDerivedFrom) and save them on output dir. Collects data for
                        computing Metric: Ratio of Reference Sharing
  -sr, --statement-refs
                        Extract all sattement nodes and the numebr of their references and save them on output dir. Collects data for computing Metric: Multiple
                        References for Facts
  -irf, --item-refed-facts
                        Extract all items and their referenced facts and save them on output dir. Collects data for computing Metric: Human-added References Ratio
  -wes, --wikidata-eschema-data
                        Extract most up-to-date Wikidata EntitySchemas data from Wikidata directory and save them on output dir. Collects Wikidata E-ids data for
                        computing COMPLETENESS metrics
  -cf, --classes-facts  Extract all classes and their facts. Collects data for computing Metric: Class/Property Schema Completeness of References
  -sfr, --statements-facts-refs
                        Extract all statement id, fact of the statement and the reference properties and save them on output dir. Collects data for computing Metrics:
                        Schema-based Property Completeness and Property Completeness of References
  -aof, --amount-of-data
                        Extract number of statement nodes, reference nodes, and distribution of triple and literals amongst reference nodes. Collects data for
                        computing Amount-of-Data metrics
  -pu, --ref-prop-usage
                        Extract number of reference properties, reference triples and reference properties usage distribution and save them on output dir. Collects
                        data for computing Mtric: Diversity of Reference Properties
  -es, --external-sources
                        Extract all external sources (including Wikidata items) and save them on output dir. Collects data for computing Mtric: Handy External Sources
  -ss, --statement-source
                        Extract all statement ids and their sources (only IRIs, not literals) and save them on output dir. Collects data for computing Mtrics:
                        Verifiable Type of references, Multilingual Sources and Multilingual Referenced Facts

``` 
An example of using the Extractor to obtain all external sources URLs in the input graph:
```
 python3.9 ./RQSSFramework/RQSS_Extractor.py --endpoint http://localhost:9999/blazegraph/sparql --output ./rqss_extractor_output --external-uris
Creating output directory: ./rqss_extractor_output
```
The above command will generate `external_uris.data` collection in the `./rqss_extractor_output` directory.

### Framework Runner Layer
The Framework Runner is the main part of the RQSS. It contains independent classes, each of which computes one or a group of related metrics. The framework classes use collected data from the Extractor layer as input and create `.csv` files to demonstrate the computed results. To deploy the Framework Runner use the `RQSSFramework/RQSS_Framework_Runner.py` script:
```
usage: RQSS_Framework_Runner.py [-h] [--endpoint ENDPOINT] [--upper-date UPPER_DATE] [-o OUTPUT_DIR] [-dp] [-l] [-sec] [-i] [-rts] [-rls] [-rtm] [-rpc] [-rc] [-rs]
                                [-rdns] [-mr] [-ha] [-ts] [-rf] [-ef] [--extract-google-cache] [-ev] [-et] [-cpsc] [-sbpc] [-pc] [-aof] [-el] [-rpd] [-hm] [-he] [-bn]
                                [-mm] [-mfs]
                                data_dir

positional arguments:
  data_dir              Input data directory that includes initial collections like facts, properties, literals, external sources, etc.

optional arguments:
  -h, --help            show this help message and exit
  --endpoint ENDPOINT   The local/public endpoint of the dataset for shex-based metrics
  --upper-date UPPER_DATE
                        The upper date (Format DD-MM-YYYY) limit for reivision history checker metrics. The deafult is now()
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output destination directory to store computed metrics details
  -dp, --dereferencing  Compute the metric: Dereference Possibility of the External URIs
  -l, --licensing       Compute the metric: External Sources’ Datasets Licensing
  -sec, --security      Compute the metric: Link Security of the External URIs
  -i, --interlinking    Compute the metric: Interlinking of Reference Properties
  -rts, --ref-triple-syntax
                        Compute the metric: Syntactic Validity of Reference Triples
  -rls, --ref-literal-syntax
                        Compute the metric: Syntactic Validity of Reference Literals
  -rtm, --ref-triple-semantic
                        Compute the metric: Semantic Validity of Reference Triples
  -rpc, --ref-property-consistency
                        Compute the metric: Consistency of Reference Properties
  -rc, --range-consistency
                        Compute the metric: Range Consistency of Reference Triples
  -rs, --ref-sharing    Compute the metric: Ratio of Reference Sharing
  -rdns, --reputation   Compute the metric: External Sources’ Domain Reputation
  -mr, --multiple-ref   Compute the metric: Multiple References for Facts
  -ha, --human-added    Compute the metric: Human-added References Ratio
  -ts, --type-of-sources
                        Compute the metrics: Verifiable Type of References
  -rf, --ref-freshness  Compute the metric: Freshness of Fact Referencing
  -ef, --ext-uris-freshness
                        Compute the metric: Freshness of External Sources
  -ev, --ext-uris-volatility
                        Compute the metric: Volatility of External Sources
  -et, --ext-uris-timeliness
                        Compute the metric: Timeliness of External Sources. The metric will use the results of the metrics Freshness of external sources and
                        Volatility of external sources. Make sure the results of the two metric is in the --output-dir argument
  -cpsc, --class-property-schema-completeness
                        Compute the metric: Schema Completeness of References
  -sbpc, --schema-based-property-completeness
                        Compute the metric: Schema-based Property Completeness of References
  -pc, --property-completeness
                        Compute the metric: Property Completeness of References
  -aof, --amount-of-data
                        Compute the Dimension: Amount-of-Data
  -el, --ext-uri-length
                        Compute the metric: External Sources URL Length
  -rpd, --ref-property-diversity
                        Compute the metric: Diversity of Reference Properties
  -hm, --human-readable-metadata
                        Compute the metrics: Human-readable Labeling and Human-readable Commenting of Reference Properties
  -he, --handy-external-sources
                        Compute the metrics: Handy External Sources
  -bn, --blank-node     Compute the metrics: Usage of Blank Nodes
  -mm, --multilingual-metadata
                        Compute the metrics: Multilingual Labeling and Multilingual Commenting of Reference Properties
  -mfs, --multilingual-sources-facts
                        Compute the metrics: Multilingual Sources and Multilingual Referenced Facts

options for computing freshness of external sources:
  --extract-google-cache
                        Set to extract google cache info for freshness of external sources
```
An example of using the Framework Runner to compute the Availability of External URIs:
```
python3.9 RQSSFramework/RQSS_Framework_Runner.py ./rqss_extractor_output/ --dereferencing --output ./rqss_framework_output
```
the above command computes the metric and saves the scores and details of external URIs availability in two `.csv` files in the `./rqss_framework_output` directory.

### Presenttion Layer
The presenter layer is the last step in RQSS. The Presenter looks into the framework layer results directory and plots different charts to demonstrate the distribution of data over properties, statements, labels, etc. in some metrics. To deploy the Presenter, use `RQSSFramework/RQSS_Presenter.py` script:
```
usage: RQSS_Presenter.py [-h] [--result-dir RESULT_DIR] [-o OUTPUT_DIR]

optional arguments:
  -h, --help            show this help message and exit
  --result-dir RESULT_DIR
                        Input data directory that includes the results of the framework metrics in CSV files
  -o OUTPUT_DIR, --output-dir OUTPUT_DIR
                        Output destination directory to store charts
```


