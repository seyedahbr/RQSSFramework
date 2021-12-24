SHEX_SCHEMAS={
"wikibase_reference_reification":
'''
PREFIX prov: <http://www.w3.org/ns/prov#>
PREFIX wikibase: <http://wikiba.se/ontology#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

START=@<statement_node>

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