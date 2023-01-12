from collections.abc import Sequence
from collections import OrderedDict
from typing import Union

import libcst as cst
from libcst import CSTNode
from model.node import DataFrameNode, IRNode, JoinNode, SetKeyNode, SQLNode

# TODO: Actually use these
# PANDAS_FUNCTIONS_RETURNING_DATAFRAME = ["read_sql"]
# DATAFRAME_ATTRIBUTES_RETURNING_DATAFRAME = ["join", "aggregate"]

Node = Union[CSTNode, IRNode]


class PandasNodeSelector(cst.CSTVisitor):
    """
    Traverses Tree and saves relevant nodes.
    These nodes will then be passed to the IR.
    
    This is a direct copy of the functions of cst_NodeSelector, that are not related to the imports.
    
    Pretty much the only addition is self.interesting_nodes
    This is a dict, that maps the original CSTNode to the IRNodes.
    This is done, because the IRNodes do not keep a reference to the original CSTNode
    
    Additionally a visit_Expr was added, so that we can detect inplace operations on DataFrames such as
    `df.set_index(key, inplace=True)`
    
    TODO: Would be nice, if this would ONLY implement the `is_interesting(node)` functionality and the creation of the IR would take place in the Optimizer
    
    
    """

    def __init__(self, pandas_star_imported: bool,
                 pandas_aliases: list[str],
                 imported_pandas_aliases: list[cst.ImportAlias]):
        self.pandas_star_imported: bool = pandas_star_imported 
        self.pandas_aliases = pandas_aliases
        self.imported_pandas_aliases = imported_pandas_aliases

        self.variables: OrderedDict[str, Node] = OrderedDict()
        self.interesting_nodes: OrderedDict[CSTNode, Node] = OrderedDict()

        super().__init__()

    def generic_visit(self, cst_node: CSTNode) -> Node:
        class_name = str(cst_node.__class__.__name__).replace("CST", "")
        method_name = f"visit_{class_name}"

        if not hasattr(self, method_name):
            raise NotImplementedError(
                f"Function is not defined for: {method_name}"
            )  # but actually they are all implemented in the base class as empty methods, right?

        method = getattr(self, method_name)
        ir_node = method(cst_node)
        if ir_node == None:
            return cst_node
        return ir_node

    def visit_Assign(self, node: cst.Assign):
        if isinstance(node.value, tuple):
            pass  # TODO: if targets and value are tuples do more complicated stuff

        value_node = self.generic_visit(node.value)
        for target_node in node.targets:
            target_name = target_node.target.value
            self.variables[target_name] = value_node
            
        if self.is_interesting(node):
            self.interesting_nodes[node] = value_node

    def visit_Expr(self, node: cst.Expr):
        value_node = self.generic_visit(node.value)
        
        if self.is_interesting(node):
            self.interesting_nodes[node] = value_node

    def is_interesting(self, node: cst.CSTNode) -> bool:
        return True  # TODO: Actually implement this....

    def is_imported_from_pandas(self, func_name: str) -> bool:
        all_pandas_aliases = [
            alias.evaluated_alias if alias.evaluated_alias else alias.evaluated_name
            for alias in self.imported_pandas_aliases
        ]

        return func_name in all_pandas_aliases

    def original_function_name(self, name: str) -> str: # TODO: Actually use this...
        for alias in self.imported_pandas_aliases:
            if alias.evaluated_alias == name:
                return alias.evaluated_name
        return name

    def create_ir_node_for(self, func_name: str, args: list, kwargs: dict) -> IRNode:
        if func_name == "read_sql":
            return SQLNode(*args, **kwargs)
        if func_name == "join":
            return JoinNode(*args, **kwargs)
        if func_name == "set_index":
            return SetKeyNode(*args, **kwargs)

        raise NotImplementedError(f"Rewrite rule for {func_name} is not implemented")

    def visit_Call(self, node: cst.Call):
        args = list(self.generic_visit(arg) for arg in node.args if not arg.keyword)
        kwargs = dict(self.generic_visit(arg) for arg in node.args if arg.keyword)

        if isinstance(node.func, cst.Name):
            func_name = node.func.value
            if self.is_imported_from_pandas(func_name):
                return self.create_ir_node_for(func_name, args, kwargs)

        if isinstance(node.func, cst.Attribute):
            attribute = self.generic_visit(node.func.value)
            if isinstance(attribute, cst.Name):
                if attribute.value in self.pandas_aliases:
                    func_name = node.func.attr.value
                    return self.create_ir_node_for(func_name, args, kwargs)
            if isinstance(attribute, DataFrameNode):
                func_name = node.func.attr.value
                return self.create_ir_node_for(func_name, [attribute] + args, kwargs)

    def visit_Name(self, node: cst.Name):
        if node.value in self.variables:
            return self.variables[node.value]
        return node

    def visit_Arg(self, node: cst.Arg):
        arg_value = self.generic_visit(node.value)

        if node.keyword:
            arg_keyword = self.generic_visit(node.keyword)
            return arg_keyword.value, arg_value
        return arg_value

    def visit_Element(self, node: cst.Element):
        return self.generic_visit(node.value)

    def visit_Tuple(self, node: cst.Tuple) -> Sequence:
        ret_values = []
        for element in node.elements:
            ret_values.append(self.generic_visit(element))
        return tuple(ret_values)
