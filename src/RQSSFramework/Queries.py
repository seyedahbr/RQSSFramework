RQSS_QUERIES={
"test_query":
'''
SELECT ?to_ret WHERE
{
  ?statement prov:wasDerivedFrom ?ref.
  ?ref pr:P854 str(?to_ret).
  FILTER(isIRI(str(?to_ret))).
}

Limit 3
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