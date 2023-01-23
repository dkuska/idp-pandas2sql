import libcst as cst

from .ir.nodes import DataFrameNode
from .NodeSelector import NodeSelector


class NodeReplacer(cst.CSTTransformer):
    def __init__(self, nodeSelector: NodeSelector) -> None:
        self.nodeSelector = nodeSelector

    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign):
        if not original_node in self.nodeSelector.interesting_nodes:
            return updated_node
        ir_node = self.nodeSelector.interesting_nodes[original_node]

        if not isinstance(ir_node, DataFrameNode):
            # not so interesting after all
            print(original_node)
            print(updated_node)
            return updated_node

        sql_access_methods = self.nodeSelector.get_sql_access_methods()
        if ir_node.library not in sql_access_methods:
            raise Exception(f"No sql access method for {ir_node.library}")
        sql_access_method = sql_access_methods[ir_node.library]

        cst_translation = ir_node.to_cst_translation(sql_access_method)

        updated_node = updated_node.with_changes(value=cst_translation.code)
        pre_code = cst_translation.precode
        post_code = cst_translation.postcode

        return cst.FlattenSentinel(pre_code + [updated_node] + post_code)

    def leave_SimpleStatementLine(self, original_node: cst.SimpleStatementLine, updated_node: cst.SimpleStatementLine):
        if len(updated_node.body) == 1:
            return updated_node
        return cst.FlattenSentinel(cst.SimpleStatementLine([statement]) for statement in updated_node.body)
