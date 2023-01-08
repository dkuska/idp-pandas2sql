from cst.PandasNodeSelector import PandasNodeSelector
from model.new_models import IRNode, DataFrameNode, SQLNode, JoinNode, SetKeyNode
from collections import OrderedDict

class PandasOptimizer():
    
    def __init__(self, variables, interesting_nodes) -> None:
        self.variables = variables
        self.interesting_nodes = interesting_nodes
        
        self.optimized_nodes = OrderedDict()
        
        self.create_IR()
        self.optimize()
        self.map_old_to_new_nodes()
        
    def create_IR(self):
        pass
    
    def optimize(self):
        pass
    
    def map_old_to_new_nodes(self):
        for old_node, IRNode in self.interesting_nodes.items():
            # Woohoo, we can do something here...
            new_node = None 
            if isinstance(IRNode, DataFrameNode):
                for target, value in self.variables.items():
                    if IRNode == value:
                        new_node = IRNode.to_cst_statement(target)
                  
            if old_node != new_node and new_node is not None:
                self.optimized_nodes[old_node] = new_node
    
    def get_optimized_nodes(self):
        return self.optimized_nodes