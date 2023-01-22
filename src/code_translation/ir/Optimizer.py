from collections import OrderedDict

import libcst as cst

from .nodes import DataFrameNode


class Optimizer:
    """
    At the moment this is not much more than a stub...
    Ideally, I'd like the creation of the IR to take place here.
    However we need to evaluate how this can be done without this being another cst.NodeVisitor...
    The information saved in self.variables and self.interesting_nodes are super, super redundant...
    Passing both are required, because the IR-Nodes don't currently have a reference to their target.
    """

    def __init__(self, variables, interesting_nodes, sql_access_methods) -> None:
        self.variables = variables
        self.interesting_nodes = interesting_nodes
        self.optimized_nodes = OrderedDict()
        self.sql_access_methods = sql_access_methods
        self.create_IR()

    def create_IR(self):
        pass

    def optimize(self):
        pass

    def map_old_to_new_nodes(self):
        """
        This is super stupid...
        It is mostly required, because self.variables saves the reference to the target, which is needed for to_cst_statement
        """
        for old_node, ir_node in self.interesting_nodes.items():
            new_nodes = []
            if isinstance(ir_node, DataFrameNode):
                for target, value in self.variables.items():
                    if ir_node == value:
                        if ir_node.library in self.sql_access_methods:
                            sql_access_method = self.sql_access_methods[ir_node.library]
                        else:
                            raise Exception(f"No sql access method for {ir_node.library}")
                        cst_translation = ir_node.to_cst_translation(sql_access_method)
                        # TODO: Needs awareness of assignment name
                        targets = [cst.AssignTarget(target=cst.Name(target))]
                        assign = cst.Assign(targets=targets, value=cst_translation.code)
                        new_nodes.extend([cst.SimpleStatementLine(body=[node]) for node in cst_translation.precode])
                        new_nodes.append(cst.SimpleStatementLine(body=[assign]))
                        new_nodes.extend([cst.SimpleStatementLine(body=[node]) for node in cst_translation.postcode])

            if new_nodes and [old_node] != new_nodes:
                self.optimized_nodes[old_node] = new_nodes

    def get_optimized_nodes(self):
        return self.optimized_nodes
