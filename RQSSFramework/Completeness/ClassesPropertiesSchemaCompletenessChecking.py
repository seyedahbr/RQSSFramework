from typing import Dict, List, NamedTuple, Set

from RQSSFramework.EntitySchemaExtractor import EidRefSummary


class ClassPropSchemaResult(NamedTuple):
    class_id: str
    num_total_properties: int = 0
    num_properties_with_defined_ref_schema: int = 0

    def __repr__(self):
        return "Class {0}, fact properties: {1}; schema exists for: {2}".format(self.class_id, self.total_properties, self.num_properties_with_defined_ref_schema)


class ClassesPropertiesSchemaCompletenessChecker:
    results: List[ClassPropSchemaResult] = None
    _classes_refed_props: Dict
    _eschema_refed_classes: Set[str]
    _eschema_refed_properties: Set[str]

    def __init__(self, classes_refed_props: Dict, wikidata_entityschemas_ref_summary: List[EidRefSummary]):
        self._classes_refed_props = classes_refed_props
        self._eschema_refed_classes, self._eschema_refed_properties = self._get_eschema_distinct_ref_specified_classes_properties(
            wikidata_entityschemas_ref_summary)

    def check_ref_schema_existance_for_properties_Wikidata(self) -> List[ClassPropSchemaResult]:
        self.results = []
        for key, value in self._classes_refed_props.items():
            self.results.append(ClassPropSchemaResult(
                key,
                len(value),
                len(set(value) & self._eschema_refed_properties)))
        return self.results

    def _get_eschema_distinct_ref_specified_classes_properties(self, wikidata_entityschemas_ref_summary: List[EidRefSummary]):
        ret_val_classes = []
        ret_val_properties = []

        for schema in wikidata_entityschemas_ref_summary:
            for fact_ref in schema.refed_facts_refs:
                if not fact_ref.ref_predicates:
                    continue
                else:
                    [ret_val_classes.append(i) for i in schema.related_classes]
                    [ret_val_properties.append(i)
                     for i in schema.related_properties]
                    ret_val_properties.append(fact_ref.refed_fact)

        return set(ret_val_classes), set(ret_val_properties)

    def _get_input_distinct_properties(self) -> Set[str]:
        ret_val = set.union(
            *[set(value) for key, value in self._classes_refed_props.items()])
        return ret_val

    @property
    def property_schema_completeness_score(self):
        if self.results is not None:
            distinct_props = self._get_input_distinct_properties()
            return len(distinct_props & self._eschema_refed_properties)/len(distinct_props) if len(distinct_props) > 0 else 1
        return None

    @property
    def class_schema_completeness_score(self):
        if self.results is not None:
            return len(self._classes_refed_props.keys() & self._eschema_refed_classes)/len(self._classes_refed_props.keys()) if len(self._classes_refed_props.keys()) > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num distinct classes,num distinct fact properties,num classes with defined ref-schema,num properties with defined ref-schema,class schema completeness of refs score,property schema completeness of refs score
{0},{1},{2},{3},{4},{5}""".format(len(self._classes_refed_props.keys()),
                                  len(self._get_input_distinct_properties()),
                                  len(self._classes_refed_props.keys()
                                      & self._eschema_refed_classes),
                                  len(self._get_input_distinct_properties()
                                      & self._eschema_refed_properties),
                                  self.class_schema_completeness_score,
                                  self.property_schema_completeness_score)

    def print_results(self):
        """
        print self.resultsif it is already computed
        """
        if self.results == None:
            print('results are not computed')
            return
        for r in self.results:
            print(r)
