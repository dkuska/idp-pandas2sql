import libcst as cst


#### NodeTransformer
class Transformer(cst.CSTTransformer):
    def __init__(self, analyzer: cst.CSTVisitor) -> None:
        pass

    def visit_Assign(self, node: cst.Assign):
        pass

    def visit_Import(self, node: cst.Import):
        pass

    def visit_ImportFrom(self, node: cst.ImportFrom):
        pass
