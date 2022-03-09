from dataclasses import dataclass
from typing import List

import requests
from lxml import html
from pyshex.utils.schema_loader import SchemaLoader
from ShExJSG import ShExJ


@dataclass
class RefedFactRef:
    refed_fact: str
    ref_predicates: List[str]

    def __repr__(self) -> str:
        return '''\n
\treferenced fact: {0}
\tref-specific properties: {1}
        '''.format(self.refed_fact, self.ref_predicates)


@dataclass
class EidRefSummary:
    e_id: str
    related_classes: List[str]
    related_properties: List[str]
    refed_facts_refs: List[RefedFactRef]

    def __repr__(self) -> str:
        return '''
eid:{0}
related classes: {1}
related properties: {2}
referenced facts and their ref-specific properties: {3}
        '''.format(self.e_id, self.related_classes, self.related_properties, self.refed_facts_refs)


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
                tables_info.append(EidRefSummary(
                    e_id, classes, properties, []))
        print('DONE. Getting related classes for {} EntitySchemas.'.format(
            len(tables_info)))
        return tables_info

    def get_entity_schemas_references_summary_from_wikidata(self) -> List[EidRefSummary]:
        initial_dict = self.get_related_classes_of_entity_ids()
        print('Start getting EntitySchemas text')
        schemata: List[ShExJ.Schema] = []
        for record in initial_dict:
            e_id = record.e_id

            print('\tGetting EntitySchema {} texts from Wikidata'.format(e_id))
            schema_text = str(requests.get(
                self._eid_page.format(e_id)).content, "utf-8")
            shext = schema_text.strip()
            loader = SchemaLoader()
            print('\tParsing EntitySchema {} via PyShEx'.format(e_id))
            try:
                eschema = loader.loads(shext)
            except:
                print("\t\tERROR: Unable to parse entity schema: ", e_id)
                continue
            if eschema is None:
                print("\t\tERROR: Unable to parse entity schema: ", e_id)
                continue
            schemata.append((e_id, shext, eschema))
        print(
            'Getting referenced facts and their reference predicates in each EntitySchema')
        for e_id, shext, schema in schemata:

            refed_facts_refs: List[RefedFactRef] = []
            print('\tSchema {}'.format(e_id))
            shape_ctr = 0

            # Start working on schema
            # if schema is empty (it can be!) don't do anything
            if schema == None or schema.shapes == None:
                continue
            # if there is no predicate pointing to a statement node in the schema, ignore it
            if 'PREFIX p: <http://www.wikidata.org/prop/>' not in shext:
                continue
            for shape in schema.shapes:
                # if the shape is empty don't do anything
                if shape.expression == None:
                    continue
                # if the type of expression in the shape is triple const, fetch the predicate/values directly
                if type(shape.expression) == ShExJ.TripleConstraint:
                    # if the predicate is a refered-fact i.e. pointing to a statement Node AND is referenced
                    was, refs = self.is_referenced_fact(
                        shape.expression.predicate, shape.expression, schema, schemata)
                    if was:
                        refed_facts_refs += [RefedFactRef(shape.expression.predicate.split(
                            'http://www.wikidata.org/prop/')[1], refs)]

                # if the type of experision is EachOf or OneOf, for each experision start the recursive fetching func
                else:
                    for exp in shape.expression.expressions:
                        refed_facts_refs += self.get_refed_facts_ref_predicates_recursive(
                            exp, schema, schemata)

                shape_ctr += 1
                print('\t\tprocessed shape number: ', shape_ctr)

            for index, item in enumerate(initial_dict):
                if item.e_id == e_id:
                    initial_dict[index].refed_facts_refs = refed_facts_refs

        return initial_dict

    def get_refed_facts_ref_predicates_recursive(self, expression, schema, schemata) -> List[RefedFactRef]:
        if type(expression) == ShExJ.TripleConstraint:
            was, refs = self.is_referenced_fact(
                expression.predicate, expression, schema, schemata)
            if was:
                return [RefedFactRef(expression.predicate.split('http://www.wikidata.org/prop/')[1], refs)]
        else:
            for exp in expression.expressions:
                return self.get_refed_facts_ref_predicates_recursive(exp, schema, schemata)
        return []

    def is_referenced_fact(self, predicate, expression, schema, schemata):
        # check if the predicate has a valid value
        if predicate == None:
            return False, []
        # check if the predicate is pointing to a statement node
        if 'http://www.wikidata.org/prop/P' not in predicate:
            return False, []
        # check if the value of the predicate is not None
        if expression.valueExpr == None:
            return False, []
        # check if the value of the predicate is a Shape
        if type(expression.valueExpr) in [ShExJ.Shape, ShExJ.ShapeOr, ShExJ.ShapeAnd]:
            if type(expression.valueExpr) == ShExJ.TripleConstraint:
                if expression.valueExpr.predicate == 'http://www.w3.org/ns/prov#wasDerivedFrom':
                    return self.fact_has_reference_predicate(expression.valueExpr, schema, schemata)
                else:
                    for exp in expression.valueExpr.expressions:
                        # no need for more deep exploration as a prov:wasDerivedFrom must be the predicate of a statement node
                        # and we are here as a sequence of p:
                        if type(exp) == ShExJ.TripleConstraint:
                            if exp.predicate == 'http://www.w3.org/ns/prov#wasDerivedFrom':
                                return self.fact_has_reference_predicate(expression.valueExpr, schema, schemata)

        if type(expression.valueExpr) is ShExJ.IRIREF:
            # if the value refers to a shape in another E-id
            if str(expression.valueExpr).startswith('https://www.wikidata.org/wiki/Special:EntitySchemaText/E'):
                eid_page, shape_id = str(expression.valueExpr).split('#')
                eid = eid_page.split(
                    'https://www.wikidata.org/wiki/Special:EntitySchemaText/')[1]
                for e_id, shext, s in schemata:
                    if e_id == eid:
                        for shape in s:
                            if s.id == shape_id:
                                if s.expression == None:
                                    break
                                elif type(s.expression) == ShExJ.TripleConstraint:
                                    if s.predicate == 'http://www.w3.org/ns/prov#wasDerivedFrom':
                                        return self.fact_has_reference_predicate(s.valueExpr, schema, schemata)
                                elif type(s.expression) in [ShExJ.EachOf, ShExJ.OneOf]:
                                    for exp in s.expression.expressions:
                                        if exp.predicate == 'http://www.w3.org/ns/prov#wasDerivedFrom':
                                            return self.fact_has_reference_predicate(exp.valueExpr, schema, schemata)
                            break
                    break
            # if the value refers to a shape in the current E-id
            else:
                for shape in schema.shapes:
                    if shape.id == expression.valueExpr:

                        if shape.expression == None:
                            break
                        elif type(shape.expression) == ShExJ.TripleConstraint:
                            if shape.predicate == 'http://www.w3.org/ns/prov#wasDerivedFrom':
                                return self.fact_has_reference_predicate(shape.valueExpr, schema, schemata)
                        elif type(shape.expression) in [ShExJ.EachOf, ShExJ.OneOf]:
                            for exp in shape.expression.expressions:
                                if exp.predicate == 'http://www.w3.org/ns/prov#wasDerivedFrom':
                                    return self.fact_has_reference_predicate(exp.valueExpr, schema, schemata)
                        break

        return False, []

    def fact_has_reference_predicate(self, expression, schema, schemata):
        grabber = []
        if expression == None:
            return False, []
        # check if the value of the predicate is a Shape
        if type(expression) in [ShExJ.Shape, ShExJ.ShapeOr, ShExJ.ShapeAnd]:
            if type(expression) == ShExJ.TripleConstraint:
                if str(expression.predicate).startswith('http://www.wikidata.org/prop/reference/P'):
                    grabber.append(str(expression.predicate).split(
                        'http://www.wikidata.org/prop/reference/')[1])
                else:
                    for exp in expression.expressions:
                        # no need for more deep exploration as a prov:wasDerivedFrom must be the predicate of a statement node
                        # and we are here as a sequence of p:
                        if type(exp) == ShExJ.TripleConstraint:
                            if str(exp.predicate).startswith('http://www.wikidata.org/prop/reference/P'):
                                grabber.append(str(exp.predicate).split(
                                    'http://www.wikidata.org/prop/reference/')[1])

        if type(expression) is ShExJ.IRIREF:
            # if the value refers to a shape in another E-id
            if str(expression).startswith('https://www.wikidata.org/wiki/Special:EntitySchemaText/E'):
                eid_page, shape_id = str(expression).split('#')
                eid = eid_page.split(
                    'https://www.wikidata.org/wiki/Special:EntitySchemaText/')[1]
                for e_id, shext, s in schemata:
                    if e_id == eid:
                        for shape in s:
                            if s.id == shape_id:
                                if s.expression == None:
                                    break
                                elif type(s.expression) == ShExJ.TripleConstraint:
                                    if str(s.predicate).startswith('http://www.wikidata.org/prop/reference/P'):
                                        grabber.append(str(s.predicate).split(
                                            'http://www.wikidata.org/prop/reference/')[1])
                                elif type(s.expression) in [ShExJ.EachOf, ShExJ.OneOf]:
                                    for exp in s.expression.expressions:
                                        if str(exp.predicate).startswith('http://www.wikidata.org/prop/reference/P'):
                                            grabber.append(str(exp.predicate).split(
                                                'http://www.wikidata.org/prop/reference/')[1])
                            break
                    break
            # if the value refers to a shape in the current E-id
            else:
                for shape in schema.shapes:
                    if shape.id == expression:

                        if shape.expression == None:
                            break
                        elif type(shape.expression) == ShExJ.TripleConstraint:
                            if str(shape.predicate).startswith('http://www.wikidata.org/prop/reference/P'):
                                grabber.append(str(shape.predicate).split(
                                    'http://www.wikidata.org/prop/reference/')[1])
                        elif type(shape.expression) in [ShExJ.EachOf, ShExJ.OneOf]:
                            for exp in shape.expression.expressions:
                                if str(exp.predicate).startswith('http://www.wikidata.org/prop/reference/P'):
                                    grabber.append(str(exp.predicate).split(
                                        'http://www.wikidata.org/prop/reference/')[1])
                        break
        if len(grabber) > 0:
            return True, grabber
        else:
            return False, grabber
