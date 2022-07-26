RQSS_QUERIES={
"test_query":
'''
SELECT ?to_ret WHERE
{
  ?statement prov:wasDerivedFrom ?ref.
  ?ref pr:P854 ?to_ret.
  #FILTER(isIRI(str(?to_ret))).
}

Limit 3
''',
"get_property_comments_wikidata":
'''
SELECT (COUNT (?itemDescs) AS ?to_ret)
WHERE {{ 
  wd:{0} schema:description ?itemDescs.
}}
''',
"get_property_labels_wikidata":
'''
SELECT (COUNT (?itemLabel) AS ?to_ret)
WHERE {{ 
  wd:{0} rdfs:label ?itemLabel.
}}
''',
"get_literal_per_ref_node_distribution_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdref: <http://www.wikidata.org/reference/>
SELECT  DISTINCT ?refNode (COUNT(?object) AS ?numOfTriples) WHERE{
  ?refNode a wikibase:Reference .
  ?refNode ?predicate ?object .
  FILTER (isLiteral(?object))
  MINUS {?object a wikibase:TimeValue}
  MINUS {?object a wikibase:QuantityValue}
  FILTER (?object != <http://wikiba.se/ontology#Reference>)
}GROUP BY ?refNode
'''
,
"get_triple_per_ref_node_distribution_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdref: <http://www.wikidata.org/reference/>
SELECT  DISTINCT ?refNode (COUNT(?object) AS ?numOfTriples) WHERE{
  ?refNode a wikibase:Reference .
  ?refNode ?predicate ?object .
  MINUS {?object a wikibase:TimeValue}
  MINUS {?object a wikibase:QuantityValue}
  FILTER (?object != <http://wikiba.se/ontology#Reference>)
}GROUP BY ?refNode
'''
,
"get_num_of_ref_nodes_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
SELECT (COUNT(DISTINCT ?ref) AS ?numORefNodes) WHERE{
	?ref a wikibase:Reference.
}
''',
"get_num_of_statement_nodes_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
SELECT (COUNT(DISTINCT ?statement) AS ?numOfStatementNodes) WHERE{ 
	?statement a wikibase:Statement.
}
''',
"get_all_statementNodes_refNodes_refValues_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdref: <http://www.wikidata.org/reference/>
SELECT ?statementNode ?refNode ?refValue WHERE{
  ?statementNode a wikibase:Statement.
  ?statementNode prov:wasDerivedFrom ?refNode.
  ?refNode ?predicate ?refValue .
  MINUS {?refValue a wikibase:TimeValue}
  MINUS {?refValue a wikibase:QuantityValue}
  FILTER (?refValue != <http://wikiba.se/ontology#Reference>)
}
''',
"get_statement_fact_refed_props_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT (?statementNode AS ?ret1)
       (?property AS ?ret2)
       (?refProperty AS ?ret3) WHERE{
  ?item ?property ?statementNode.
  ?statementNode a wikibase:Statement.
  OPTIONAL{
    ?statementNode prov:wasDerivedFrom ?refNode.
    ?refNode ?refProperty ?refObject.
    MINUS {?refObject a wikibase:TimeValue}
    MINUS {?refObject a wikibase:QuantityValue}
    FILTER (?refObject != <http://wikiba.se/ontology#Reference>)
  }
}
''',
"get_classes_and_facts":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT (?class AS ?ret1)
                (?property AS ?ret2) WHERE{
  ?item ?property ?statementNode.
  ?statementNode a wikibase:Statement.
  OPTIONAL{
    ?item wdt:P31 ?class.
  }
}
''',
"get_item_refed_facts_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT (?item AS ?ret1)
                (?refedProperty AS ?ret2) WHERE{
  ?item a wikibase:Item;
          ?refedProperty [prov:wasDerivedFrom ?refNode].
}
''',
"get_sattement_nodes_ref_num_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdref: <http://www.wikidata.org/reference/>

SELECT ?statementNode (COUNT(?refnode) AS ?numOfRef) WHERE{
        ?statementNode a wikibase:Statement.
        ?statementNode prov:wasDerivedFrom ?refnode.
}GROUP BY ?statementNode
''',
"get_ref_nodes_incomings_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdref: <http://www.wikidata.org/reference/>

SELECT ?refnode (COUNT(?item) AS ?numOfStatements) WHERE{
        ?item a wikibase:Statement.
        ?item prov:wasDerivedFrom ?refnode.
}GROUP BY ?refnode
''',
"get_ref_properties_object_value_types_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
SELECT (REPLACE(STR(?refProperty),".*P","P") AS ?ret1)
       (REPLACE(STR(?refObject),".*Q","Q") AS ?ret2) WHERE{
  ?ref a wikibase:Reference.
  ?ref ?refProperty ?refObject.
  FILTER(STRSTARTS(STR(?refProperty),'http://www.wikidata.org/prop/reference/'))
  FILTER(STRSTARTS(STR(?refObject),'http://www.wikidata.org/entity/'))
}
''',
"get_instances_subclass_of_values_wikimedia":
'''
SELECT DISTINCT (REPLACE(STR(?item),".*Q","Q") AS ?to_ret) WHERE{{
  {{wd:{0} wdt:P279+ ?item.}}
  UNION{{
    wd:{0} wdt:P31/wdt:279* ?item.
  }}
}}
'''
,
"get_property_range_wikimedia":
'''
SELECT (REPLACE(STR(?constr),".*Q","Q") AS ?to_ret) WHERE{{wd:{0} p:P2302 [ps:P2302 wd:Q21510865;
                                      pq:P2308 ?constr]}}
''',
"get_ref_properties_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
SELECT DISTINCT (REPLACE(STR(?refProperty),".*P","P") AS ?to_ret) WHERE{
        ?item a wikibase:Reference.
        ?item ?refProperty ?object.
        MINUS {?object a wikibase:TimeValue}
        MINUS {?object a wikibase:QuantityValue}
        FILTER (?object != <http://wikiba.se/ontology#Reference>)
        FILTER (?object != <http://www.w3.org/1999/02/22-rdf-syntax-ns#type>)
}
''',
"get_property_constraints_specificity":
'''
SELECT ?to_ret WHERE{{
  BIND (EXISTS{{wd:{0} p:P2302 [pq:P5314 wd:Q54828450]}} AS ?to_ret)
}}
''',
"get_fact_ref_triples_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT (REPLACE(STR(?item),".*Q","Q") AS ?ret1)
                (REPLACE(STR(?property),".*P","P") AS ?ret2)
                (REPLACE(STR(?refProperty),".*P","P") AS ?ret3)
                (REPLACE(STR(?refObject),".*Q","Q") AS ?ret4) WHERE{
  ?item ?property ?statementNode.
  ?statementNode a wikibase:Statement.
  ?statementNode prov:wasDerivedFrom ?refNode.
  ?refNode ?refProperty ?refObject.
  MINUS {?refObject a wikibase:TimeValue}
  MINUS {?refObject a wikibase:QuantityValue}
  FILTER (?refObject != <http://wikiba.se/ontology#Reference>)
}
''',
"get_reference_literals_wikimedia":
'''
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT (REPLACE(STR(?refProp),".*P","P") AS ?to_ret1) ?to_ret2 WHERE {
  ?statement prov:wasDerivedFrom ?ref .
  ?ref ?refProp ?to_ret2 .
  FILTER (isLiteral(?to_ret2))
}
'''
,
"get_property_constraints_regex":
'''
SELECT ?to_ret WHERE{{wd:{0} p:P2302 [pq:P1793 ?to_ret]}}
''',
"get_all_statement_nodes_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
SELECT ?to_ret WHERE{
	?to_ret a wikibase:Statement.
}
''',

"get_all_external_sources_filter_wikimedia" : 
'''
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT ?to_ret WHERE {
   ?statement prov:wasDerivedFrom ?ref .
   ?ref ?refProperty ?to_ret .
  FILTER (isIRI(?to_ret) &&
          !CONTAINS(lcase(str(?to_ret)), "wikidata.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikipedia.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikimedia.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikivoyage.org")&&
          !CONTAINS(lcase(str(?to_ret)), "mediawiki.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikiversity.org")&&
          !CONTAINS(lcase(str(?to_ret)), "wikinews.org")  &&
          !CONTAINS(lcase(str(?to_ret)), "wikisource.org")&&
          !CONTAINS(lcase(str(?to_ret)), "wikibooks.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikiquote.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wiktionary.org")&&
          !CONTAINS(lcase(str(?to_ret)), "wikiba.se"))
}
''',
"get_all_external_sources_filter_wikimedia_distinct" : 
'''
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?to_ret WHERE {
   ?statement prov:wasDerivedFrom ?ref .
   ?ref ?refProperty ?to_ret .
  FILTER (isIRI(?to_ret) &&
          !CONTAINS(lcase(str(?to_ret)), "wikidata.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikipedia.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikimedia.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikivoyage.org")&&
          !CONTAINS(lcase(str(?to_ret)), "mediawiki.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikiversity.org")&&
          !CONTAINS(lcase(str(?to_ret)), "wikinews.org")  &&
          !CONTAINS(lcase(str(?to_ret)), "wikisource.org")&&
          !CONTAINS(lcase(str(?to_ret)), "wikibooks.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wikiquote.org") &&
          !CONTAINS(lcase(str(?to_ret)), "wiktionary.org")&&
          !CONTAINS(lcase(str(?to_ret)), "wikiba.se"))
}
'''
}