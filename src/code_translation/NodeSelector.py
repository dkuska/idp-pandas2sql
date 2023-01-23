from collections.abc import Sequence
from typing import Optional, Union

import libcst as cst

from ..exceptions import (
    LibMethodUnresolved,
    LibMethodWithoutHandler,
    NoResolveMethod,
    UnresolvableCSTNode,
)
from .input import DaskInput, InputModule, PandasInput
from .ir.nodes import IRNode

input_modules = [PandasInput(), DaskInput()]

module_by_name: dict[str, InputModule] = {module.module_name: module for module in input_modules}

Node = Union[cst.CSTNode, IRNode]


class NodeSelector(cst.CSTVisitor):
    """
    Traverses Tree, detects if pandas was imported and saves relevant nodes.
    These nodes will then be passed to the IR
    """

    def __init__(self) -> None:

        self.variables: dict[str, Node] = {}
        self.interesting_nodes: dict[cst.CSTNode, Node] = {}

        """Maps the library names in namespace to the responsible InputModule"""
        self.libraries: dict[str, InputModule] = {}
        """Maps the method names in namespace to the responsible InputModule and the original method name."""
        self.library_methods: dict[str, tuple[InputModule, str]] = {}

        super().__init__()

    def resolve(self, cst_node: cst.CSTNode) -> Node:
        try:
            class_name = str(cst_node.__class__.__name__).replace("CST", "")
            method_name = f"resolve_{class_name}"

            if not hasattr(self, method_name):
                raise NoResolveMethod(class_name)

            resolve_method = getattr(self, method_name)
            return resolve_method(cst_node)
        except (NoResolveMethod, UnresolvableCSTNode, LibMethodWithoutHandler, LibMethodUnresolved) as e:
            print(type(e))
            print(f"Warning: {e}")
            return cst_node

    def get_sql_access_methods(self):
        # For each InputModule.module_name, get name for sql access
        access_methods: dict[str, cst.CSTNode] = {}

        # For each library get the default sql access method
        for library_alias, input_module in self.libraries.items():
            access_methods[input_module.module_name] = cst.Attribute(
                value=cst.Name(value=library_alias), attr=cst.Name(value=input_module.sql_access_method)
            )

        # If this method is directly imported without alias, use that one
        for library_method, (input_module, _) in self.library_methods.items():

            if input_module.module_name in access_methods and library_method == input_module.sql_access_method:
                access_methods[input_module.module_name] = cst.Name(value=library_method)

        return access_methods

    def visit_Import(self, node: cst.Import):
        imported_modules = list(node.names)

        for imported_module in imported_modules:
            if imported_module.evaluated_name not in module_by_name:
                continue
            input_module = module_by_name[imported_module.evaluated_name]
            alias = imported_module.evaluated_alias or imported_module.evaluated_name
            self.libraries[alias] = input_module

        return False

    def visit_ImportFrom(self, node: cst.ImportFrom):
        imported_module_name = node.module.value
        if imported_module_name not in module_by_name:
            return False
        input_module = module_by_name[imported_module_name]

        if isinstance(node.names, cst.ImportStar):
            # Todo: add all pandas symbols
            symbols = input_module.all_symbol_names
            imported_elements = [(symbol, symbol) for symbol in symbols]
        else:
            imported_elements = [
                (alias.evaluated_alias or alias.evaluated_name, alias.evaluated_name) for alias in node.names
            ]

        for imported_element in imported_elements:
            self.library_methods[imported_element[0]] = (input_module, imported_element[1])

        return False

    def visit_Assign(self, node: cst.Assign):
        if isinstance(node.value, tuple):
            pass  # if targets and value are tuples do more complicated stuff

        value_node = self.resolve(node.value)
        for target_node in node.targets:
            target_name = target_node.target.value
            self.variables[target_name] = value_node

        self.interesting_nodes[node] = value_node

        return False

    def resolve_Call(self, node: cst.Call) -> Optional[Node]:
        args = list(self.parse_NonKwArg(arg) for arg in node.args if not arg.keyword)
        kwargs = dict(self.parse_KwArg(arg) for arg in node.args if arg.keyword)
        result = None

        if isinstance(node.func, cst.Name):  # calls to directly imported library function. e.g. read_sql
            func_alias = node.func.value
            if func_alias not in self.library_methods:
                raise UnresolvableCSTNode(f'Name ("{node.func.value}")')
            module, func_name = self.library_methods[func_alias]
            result = module.resolve_call(func_name, False, *args, **kwargs)

        elif isinstance(node.func, cst.Attribute):
            attribute = self.resolve(node.func.value)

            if isinstance(attribute, cst.Name):  # calls to function accessed via module. e.g. pd.read_sql
                if attribute.value not in self.libraries:
                    raise UnresolvableCSTNode(f'Attribute ("{attribute.value}")')
                module = self.libraries[attribute.value]
                func_name = node.func.attr.value
                result = module.resolve_call(func_name, False, *args, **kwargs)
            elif isinstance(attribute, IRNode):  # calls to IR nodes. e.g. df.join
                method_name = node.func.attr.value
                node = attribute
                module = module_by_name[node.library]
                result = module.resolve_call(method_name, True, node, *args, **kwargs)
            else:
                print("Warning: Something strange got called: ", attribute)

        if result:
            return result

    def resolve_Name(self, node: cst.Name) -> Node:
        if node.value not in self.variables:
            raise UnresolvableCSTNode(f'Name ("{node.value}")')
        return self.variables[node.value]

    def resolve_Element(self, node: cst.Element) -> Optional[Node]:
        return self.resolve(node.value)

    def resolve_Tuple(self, node: cst.Tuple) -> Sequence:
        ret_values = []
        for element in node.elements:
            ret_values.append(self.resolve(element))
        return tuple(ret_values)

    def resolve_SimpleString(self, node: cst.SimpleString) -> str:
        return node.value

    def parse_NonKwArg(self, node: cst.Arg) -> Node:
        arg_value = self.resolve(node.value)
        return arg_value

    def parse_KwArg(self, node: cst.Arg) -> tuple[str, Node]:
        arg_value = self.resolve(node.value)
        return node.keyword.value, arg_value
