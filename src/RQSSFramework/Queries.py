RQSS_QUERIES={
"get_all_external_sources_filter_wikimedia" : 
'''
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT ?refValue WHERE {
   ?statement prov:wasDerivedFrom ?ref .
   ?ref ?refProperty ?refValue .
  FILTER (CONTAINS(lcase(?refValue), "http") &&
          !CONTAINS(lcase(?refValue), "wikidata.org") &&
          !CONTAINS(lcase(?refValue), "wikipedia.org") &&
          !CONTAINS(lcase(?refValue), "wikimedia.org") &&
          !CONTAINS(lcase(?refValue), "wikivoyage.org")&&
          !CONTAINS(lcase(?refValue), "mediawiki.org") &&
          !CONTAINS(lcase(?refValue), "wikiversity.org")&&
          !CONTAINS(lcase(?refValue), "wikinews.org")  &&
          !CONTAINS(lcase(?refValue), "wikisource.org")&&
          !CONTAINS(lcase(?refValue), "wikibooks.org") &&
          !CONTAINS(lcase(?refValue), "wikiquote.org") &&
          !CONTAINS(lcase(?refValue), "wiktionary.org"))
}
''',
"get_all_external_sources_filter_wikimedia_distinct" : 
'''
PREFIX prov: <http://www.w3.org/ns/prov#>
SELECT DISTINCT ?refValue WHERE {
   ?statement prov:wasDerivedFrom ?ref .
   ?ref ?refProperty ?refValue .
  FILTER (CONTAINS(lcase(?refValue), "http") &&
          !CONTAINS(lcase(?refValue), "wikidata.org") &&
          !CONTAINS(lcase(?refValue), "wikipedia.org") &&
          !CONTAINS(lcase(?refValue), "wikimedia.org") &&
          !CONTAINS(lcase(?refValue), "wikivoyage.org")&&
          !CONTAINS(lcase(?refValue), "mediawiki.org") &&
          !CONTAINS(lcase(?refValue), "wikiversity.org")&&
          !CONTAINS(lcase(?refValue), "wikinews.org")  &&
          !CONTAINS(lcase(?refValue), "wikisource.org")&&
          !CONTAINS(lcase(?refValue), "wikibooks.org") &&
          !CONTAINS(lcase(?refValue), "wikiquote.org") &&
          !CONTAINS(lcase(?refValue), "wiktionary.org"))
}
'''
}