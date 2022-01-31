# RQSS-Framework
RQSS is a Data Quality Assessment Methodology that aims to measure the fitness of the Wikidata references (and other RDF graphs) to the users and applications by defining explicit metrics for data quality dimensions.

## Input/Output
RQSS gets an RDF graph as the **input**. RQSS gets an RDF graph as the input. The input graph could be either a raw RDF file (.nt, .ttl, ...) or a local/public SPARQL endpoint. [Currently] The most comprehensive input graph for the system are subsets of Wikidata. These subsets can be topical or not. They can be as small as a statement or as large as the entire Wikidata. The only condition for the input subset is to include at least one reference.

The main **output** of RQSS is the calculated values of the metrics as numbers between [0,1]. A small number of metrics produce numbers outside the range of zero and one. For more information about the definition of metrics and the formulas, please reed [To be annonced](). The Presentation Layer provide more graphical information to the user than the distribution of criteria.

## Layers
Reference Quality Scoring System (RQSS) has three main layers:

### Extractor Layer
Extractor layer prepares the required collections for the Framework Layer which are needed to calculate the metrics. These collections are the collection of items, properties, statements, references, literals, external sources, etc. Collections can be extracted from the raw RDF files or local/public SPARQL endpoints. The extractor obtains the collections mostly by performing SPARQL queries.

### Framework Layer
The framework layer is the main part of RQSS. It contains independent classes, each of which computes a metric. The framework classes use collected data from the extractor layer as input and create CSV files to demonstrate the computed results. Rather than saving just [0,1] scores, the framework classes save more computation data so we can compute a distribution over results. The framework layer is categorized in different dimensions, according to metric definitions.

### Presenttion Layer
The presenter layer is the last step of RQSS. The presenter layer accepts the framework layer results as input and plots different charts to demonstrate the results to human users efficiently.

