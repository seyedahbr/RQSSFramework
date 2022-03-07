from dataclasses import dataclass
from typing import Dict, List, Optional, Union

import requests
from lxml import html
from pyshex.utils.schema_loader import SchemaLoader
from ShExJSG import ShExJ


@dataclass
class RefedFactRef:
    refed_fact: str
    ref_predicates: List[str]


@dataclass
class EidRefSummary:
    e_id: str
    related_classes: List[str]
    related_properties: List[str]
    refed_facts_refs: List[RefedFactRef]


class EntitySchemaExtractor:
    _schema_dir = 'https://www.wikidata.org/wiki/Wikidata:Database_reports/EntitySchema_directory'
    _xpath_query = '/html/body/div[3]/div[3]/div[5]/div[1]/table[contains(@class,"wikitable")]'
    _eid_page = 'https://www.wikidata.org/wiki/Special:EntitySchemaText/{}'

    def get_related_classes_of_entity_ids(self) -> List[EidRefSummary]:
        print('Getting related classes for each EntitySchema')
        print('\tGetting EntitySchemas directory page data from: ', self._schema_dir)
        page = requests.get(self._schema_dir)
        tree = html.fromstring(page.content)
        tables = tree.xpath(self._xpath_query)
        tables_info: List[EidRefSummary] = []
        print('\tParsing data')
        for table in tables:
            rows = table.xpath('./tbody/tr')
            for row in rows:
                cols = row.xpath('./td')
                if len(cols) != 5:
                    continue
                e_id = cols[0].xpath('./text()')[0]
                e_id = e_id[e_id.find("(")+1:e_id.find(")")]
                q_ids = cols[3].xpath('./text()')
                for index, item in enumerate(q_ids):
                    q_ids[index] = item[item.find("(")+1:item.find(")")]
                classes = ';'.join([i for i in q_ids if i[0] == 'Q'])
                properties = ';'.join([i for i in q_ids if i[0] == 'P'])
                tables_info.append(EidRefSummary(e_id,classes,properties,[]))
        print('DONE. Getting related classes for {} EntitySchemas.'.format(
            len(tables_info)))
        return tables_info

    def get_entity_schemas_references_summary_from_wikidata(self) -> List[EidRefSummary]:
        initial_dict = self.get_related_classes_of_entity_ids()
        print('Start getting EntitySchemas text')
        schemata: List[ShExJ.Schema] = []
        for record in initial_dict:
            e_id = record.e_id
            if e_id != 'E293':
                continue
            print('\tGetting EntitySchema {} texts from Wikidat'.format(e_id))
            schema_text = str(requests.get(
                self._eid_page.format(e_id)).content, "utf-8")
            shext = schema_text.strip()
            loader = SchemaLoader()
            print('\tParsing EntitySchema {} via PyShEx'.format(e_id))
            eschema = loader.loads(shext)
            if eschema is None:
                print("\t\tERROR: Unable to parse entity schema: ", e_id)
                continue
            schemata.append(eschema)
            
        print('Getting referenced facts and their reference predicates in each EntitySchema')
        for schema in schemata:
            refed_facts_refs: List[RefedFactRef] = []
            for shape in schema.shapes:
                print(type(shape))
                refed_facts_refs += self.get_refed_facts_ref_predicates_recursive(shape)
            
    def get_refed_facts_ref_predicates_recursive(self, shape:ShExJ.Shape) -> List[RefedFactRef]:          
        
        if type(shape.expression) == ShExJ.TripleConstraint:
            print('***')
            return RefedFactRef(shape.expression.predicate, shape.expression.valueExpr)
            # print(shape.expression.predicate)
        return self.get_refed_facts_ref_predicates_recursive(shape.expression.expressions)
                # print('\t', type(exp))
        # print(type(shape))
        # for exp in shape.expressions:
                #    print(type(exp))
