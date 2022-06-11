from typing import List, NamedTuple


class MultipleRefResult(NamedTuple):
    total_statement: int
    multiple_referenced: int

    def __repr__(self):
        return "Number of statements: {0}; statements with multiple references:{1}; ratio: {2}".format(self.total_statement, self.multiple_referenced, round(self.ratio, 2))

    @property
    def ratio(self):
        return (self.multiple_referenced/self.total_statement)


class StatementRefNum(NamedTuple):
    statement: str
    num_of_refs: int


class MultipleReferenceChecker:
    result: MultipleRefResult = None
    statements: List[StatementRefNum]

    def __init__(self, statements: List[StatementRefNum]) -> None:
        self.statements = statements

    def count_seperate_multiple_referenced_statements(self) -> List[StatementRefNum]:
        ret_val: List[StatementRefNum] = []
        for record in self.statements:
            if int(record.num_of_refs) > 1:
                ret_val.append(record)
        self.result = MultipleRefResult(len(self.statements), len(ret_val))
        return ret_val

    @property
    def score(self):
        if self.result is not None:
            return self.result.ratio
        return None

    def __repr__(self):
        if self.result == None:
            return 'Results are not computed'
        return """num of statements,num of multiple refed,score
{0},{1},{2}""".format(self.result.total_statement, self.result.multiple_referenced, self.score)

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print(self.result)
