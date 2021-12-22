SHEX_SCHEMAS={
"test_shex":
'''

''',
"wikibase_reference_reification":
'''
PREFIX wd: <http://www.wikidata.org/entity/>
PREFIX p: <http://www.wikidata.org/prop/>
PREFIX pr: <http://www.wikidata.org/prop/reference/>
PREFIX prv: <http://www.wikidata.org/prop/reference/value/>
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wds: <http://www.wikidata.org/entity/statement/>
PREFIX wdref: <http://www.wikidata.org/reference/>
PREFIX wdv: <http://www.wikidata.org/value/>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

<statement_node> {
  prov:wasDerivedFrom @<reference_node>* ;
}
<reference_node> {
  <ref-property> xsd:decimal OR xsd:integer OR xsd:dateTime OR xsd:string OR IRI* ;
  <ref-property> @<value>* ;
}
<value> {
  wikibase:quantityAmount xsd:decimal OR xsd:integer?;
  wikibase:timeValue xsd:dateTime?;
  #...
}

'''
}