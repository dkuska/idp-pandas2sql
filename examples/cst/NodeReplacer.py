import libcst as cst


class NodeReplacer():
    def __init__(self) -> None:
        pass
    
    def replace(self, src_tree: cst.Module, old_new_nodes) -> cst.Module:
        new_tree_body = []
        for src_node in src_tree.body:
            node_replaced = False
            node_replacement = None
            
            if src_node.body[0] in old_new_nodes:
                node_replaced = True
                node_replacement = old_new_nodes[src_node.body[0]]
                
                if node_replacement is None:
                    node_replaced = False
                    
            if node_replaced:
                new_tree_body.append(node_replacement)
            else:
                new_tree_body.append(src_node)
    
        return cst.Module(body=new_tree_body, header=src_tree.header, footer=src_tree.footer)
