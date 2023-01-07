from PandasOptimizer import PandasOptimizer
import libcst as cst

class NodeReplacer():
    def __init__(self) -> None:
        pass
    
    def replace(src_tree: cst.Module, old_new_nodes) -> cst.Module:
        new_tree = src_tree.deep_clone()
        new_tree_body = []
        for src_node in src_tree.body:
            node_replaced = False
            node_replacement = None
            for old_node, new_node in old_new_nodes:
                if src_node == old_node:
                    node_replaced = True
                    node_replacement = new_node
                    
            if node_replaced:
                new_tree_body.append(node_replacement)
            else:
                new_tree_body.append(src_node)
        
        new_tree.body = new_tree_body
        
        return new_tree