from typing import Dict, List, NamedTuple


class ClassPropSchemaResult(NamedTuple):
    class_id: str
    total_refed_properties: int = 0
    num_properties_schema_exists: int = 0

    def __repr__(self):
        return "Class {0}, referenced properties: {1}; schema exists for: {2}".format(self.class_id, self.total_refed_properties, self.num_properties_schema_exists)


class ClassesPropertiesSchemaCompletenessChecker:
    results: List[ClassPropSchemaResult] = None
    _classes_refed_props: Dict

    def __init__(self, classes_refed_props: Dict):
        self._classes_refed_props = classes_refed_props

    def check_ref_schema_existance_for_properties_Wikidata(self, wikidata_entityschemas_info: Dict) -> List[ClassPropSchemaResult]:
        self.results = []
        for class_id in self._classes_refed_props:
            if class_id not in wikidata_entityschemas_info:
                self.results.append(ClassPropSchemaResult(
                    class_id, len(self._classes_refed_props[str(class_id)]), 0))
                continue
            self.results.append(ClassPropSchemaResult(
                class_id,
                len(self._classes_refed_props[str(class_id)]),
                len([i for i in self._classes_refed_props[str(class_id)] if i in wikidata_entityschemas_info[str(class_id)]])))
        return self.results

    @property
    def property_schema_completeness_score(self):
        if self.results != None:
            total = sum([i.total_refed_properties for i in self.results])
            return sum([i.num_properties_schema_exists for i in self.results])/total if total > 0 else 1
        return None
    
    @property
    def class_schema_completeness_score(self):
        if self.results != None:
            return len([i for i in self.results if i.num_properties_schema_exists > 0])/len(self.results) if len(self.results) > 0 else 1
        return None

    def __repr__(self):
        if self.results == None:
            return 'Results are not computed'
        return """num of classes,total of refed properties,total properties with schema defined,class schema completeness score,property schema completeness score
{0},{1},{2},{3},{4}""".format(len(self.results),
sum([i.total_refed_properties for i in self.results]),
sum([i.num_properties_schema_exists for i in self.results]),
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
