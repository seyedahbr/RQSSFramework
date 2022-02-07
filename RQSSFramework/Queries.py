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
"get_ref_nodes_incomings_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdref: <http://www.wikidata.org/reference/>

SELECT ?refnode (?numOfStatements AS ?num) WHERE{
SELECT  DISTINCT ?refnode (COUNT(?item) AS ?numOfStatements) WHERE{
        ?item a wikibase:Statement.
        ?item prov:wasDerivedFrom ?refnode.
}GROUP BY ?refnode
}
''',
"get_ref_properties_object_value_types_wikimedia":
'''
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>
SELECT DISTINCT (REPLACE(STR(?refProperty),".*P","P") AS ?ret1)
                (REPLACE(STR(?refVlueType),".*Q","Q") AS ?ret2) WHERE{
  ?refNode a wikibase:Reference.
  ?refNode ?refProperty ?refObject.
  MINUS {?refObject a wikibase:TimeValue}
  MINUS {?refObject a wikibase:QuantityValue}
  FILTER (?refObject != <http://wikiba.se/ontology#Reference>).
  ?refobject wdt:P31 ?refVlueType.
  ?refobject wdt:P279 ?refVlueType.
  ?refobject wdt:P31/wdt:P279* ?refVlueType.
}
''',
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