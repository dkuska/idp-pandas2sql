from ast import *

from ast_nodevisitor import Analyzer


#### NodeTransformer
class Transformer(NodeTransformer):
    def __init__(self, analyzer: Analyzer) -> None:
        pass

    def visit_Assign(self, node: Assign):
        self.generic_visit(node)

    def visit_Import(self, node: Import):
        self.generic_visit(node)
