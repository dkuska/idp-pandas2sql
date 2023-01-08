from collections.abc import Sequence
from typing import Union

import libcst as cst
from libcst import CSTNode
from model.new_models import DataFrameNode, IRNode, JoinNode, SetKeyNode, SQLNode

PANDAS_FUNCTIONS_RETURNING_DATAFRAME = ["read_sql"]
DATAFRAME_ATTRIBUTES_RETURNING_DATAFRAME = ["join", "aggregate"]

Node = Union[CSTNode, IRNode]


class NodeSelector(cst.CSTVisitor):
    """
    Traverses Tree, detects if pandas was imported and saves relevant nodes.
    These nodes will then be passed to the IR
    """

    def __init__(self) -> None:
        self.pandas_imported: bool = False
        self.pandas_star_imported: bool = True  # TODO: use this in code
        self.pandas_aliases = ["pandas"]
        self.imported_pandas_aliases: list[cst.ImportAlias] = []

        self.variables: dict[str, Node] = {}

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

    def visit_Import(self, node: cst.Import):
        imported_modules = list(node.names)

        for imported_module in imported_modules:
            if imported_module.evaluated_name != "pandas":
                continue
            if imported_module.evaluated_alias:
                self.pandas_aliases.append(imported_module.evaluated_alias)

    def visit_ImportFrom(self, node: cst.ImportFrom):
        imported_module_name = node.module.value
        if imported_module_name != "pandas":
            return

        # if it is an import star
        if isinstance(node.names, cst.ImportStar):
            self.pandas_star_imported = True
            return

        imported_elements = list(node.names)
        self.imported_pandas_aliases.extend(imported_elements)

    def visit_Assign(self, node: cst.Assign):
        if isinstance(node.value, tuple):
            pass  # if targets and value are tuples do more complicated stuff

        value_node = self.generic_visit(node.value)
        for target_node in node.targets:
            target_name = target_node.target.value
            self.variables[target_name] = value_node

    def is_imported_from_pandas(self, func_name: str) -> bool:
        all_pandas_aliases = [
            alias.evaluated_alias if alias.evaluated_alias else alias.evaluated_name
            for alias in self.imported_pandas_aliases
        ]

        return func_name in all_pandas_aliases

    def original_function_name(self, name: str) -> str:
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
