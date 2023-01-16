from collections import OrderedDict

from model.nodes import DataFrameNode
import libcst as cst

class Optimizer:
    """
    At the moment this is not much more than a stub...
    Ideally, I'd like the creation of the IR to take place here.
    However we need to evaluate how this can be done without this being another cst.NodeVisitor...
    The information saved in self.variables and self.interesting_nodes are super, super redundant...
    Passing both are required, because the IR-Nodes don't currently have a reference to their target.
    """

    def __init__(self, variables, interesting_nodes) -> None:
        self.variables = variables
        self.interesting_nodes = interesting_nodes
        self.optimized_nodes = OrderedDict()
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
        for old_node, IRNode in self.interesting_nodes.items():
            # Woohoo, we can do something here...
            new_node = None
            if isinstance(IRNode, DataFrameNode):
                for target, value in self.variables.items():
                    if IRNode == value:
                        call = IRNode.to_cst_node()
                        targets = [cst.AssignTarget(target=cst.Name(target))]  # TODO: Needs awareness of assignment name
                        assign = cst.Assign(targets=targets, value=call)    
                        new_node = cst.SimpleStatementLine(body=[assign])

            if old_node != new_node and new_node is not None:
                self.optimized_nodes[old_node] = new_node

    def get_optimized_nodes(self):
        return self.optimized_nodes
