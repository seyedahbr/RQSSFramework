from TripleSyntaxChecking import SyntxResult

class WikibaseRefLiteralSyntaxChecker:
    result:SyntxResult = None

    def print_results(self):
        """
        print self.result if it is already computed
        """
        if self.result == None:
            print('Results are not computed')
            return
        print(self.result)