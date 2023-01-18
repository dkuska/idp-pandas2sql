from collections import OrderedDict

import libcst as cst


class NodeReplacer:
    """
    The function of this is to replace Nodes in the old CST with the new nodes obtained through our optimizations.
    """

    def __init__(self) -> None:
        pass

    def replace(self, src_tree: cst.Module, old_new_nodes: OrderedDict) -> cst.Module:
        new_tree_body = []
        # Iterate over old CST
        for src_node in src_tree.body:
            node_replaced = False
            node_replacement = None

            # TODO: This is a quick fix, investigate if src_node.body can contain multiple statements...
            if src_node.body[0] in old_new_nodes:
                node_replaced = True
                node_replacement = old_new_nodes[src_node.body[0]]

                if node_replacement is None:  # Also a quick fix...
                    node_replaced = False

            if node_replaced:
                new_tree_body.extend(node_replacement)
            else:
                new_tree_body.append(src_node)

        return cst.Module(
            body=new_tree_body,
            header=src_tree.header,
            footer=src_tree.footer,
            encoding=src_tree.encoding,
            default_indent=src_tree.default_indent,
            default_newline=src_tree.default_newline,
            has_trailing_newline=src_tree.has_trailing_newline,
        )
