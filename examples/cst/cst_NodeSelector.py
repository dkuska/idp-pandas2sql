from collections.abc import Sequence
from typing import Optional, Union

import libcst as cst
from input.inputModule import InputModule
from input.pandas import PandasInput
from libcst import CSTNode
from model.new_models import IRNode

input_modules = [
    PandasInput(),
]

module_by_name = {module.module_name: module for module in input_modules}

Node = Union[CSTNode, IRNode]


class NodeSelector(cst.CSTVisitor):
    """
    Traverses Tree, detects if pandas was imported and saves relevant nodes.
    These nodes will then be passed to the IR
    """

    def __init__(self) -> None:

        self.variables: dict[str, Node] = {}
        """Maps the library names in namespace to the responsible InputModule"""
        self.libraries: dict[str, InputModule] = {}
        """Maps the method names in namespace to the responsible InputModule and the original method name."""
        self.library_methods: dict[str, tuple[InputModule, str]] = {}

        super().__init__()

    def generic_visit(self, cst_node: CSTNode) -> Node:
        class_name = str(cst_node.__class__.__name__).replace("CST", "")
        method_name = f"parse_{class_name}"

        if not hasattr(self, method_name):
            # raise NotImplementedError(
            #     f'No way to parse CST Node of type "{class_name}"'
            # )  # but actually they are all implemented in the base class as empty methods, right?
            print(f'Warning: No way to parse CST Node of type "{class_name}"')
            return cst_node

        method = getattr(self, method_name)
        ir_node = method(cst_node)
        if ir_node == None:
            return cst_node
        return ir_node

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

        value_node = self.generic_visit(node.value)
        for target_node in node.targets:
            target_name = target_node.target.value
            self.variables[target_name] = value_node

        return False

    def parse_Call(self, node: cst.Call) -> Optional[Node]:
        args = list(self.parse_NonKwArg(arg) for arg in node.args if not arg.keyword)
        kwargs = dict(self.parse_KwArg(arg) for arg in node.args if arg.keyword)

        result = None

        if isinstance(node.func, cst.Name):  # calls to directly imported library function. e.g. read_sql
            func_alias = node.func.value
            if func_alias not in self.library_methods:
                return
            module, func_name = self.library_methods[func_alias]
            result = self.call_module_method(module, func_name, args, kwargs)

        elif isinstance(node.func, cst.Attribute):
            attribute = self.generic_visit(node.func.value)

            if isinstance(attribute, cst.Name):  # calls to function accessed via module. e.g. pd.read_sql
                if attribute.value not in self.libraries:
                    return
                module = self.libraries[attribute.value]
                func_name = node.func.attr.value
                result = self.call_module_method(module, func_name, args, kwargs)
            elif isinstance(attribute, IRNode):  # calls to IR nodes. e.g. df.join
                func_name = node.func.attr.value
                node = attribute
                module = module_by_name[node.library]
                result = self.call_module_ir_method(module, node, func_name, args, kwargs)
            else:
                print("Warning: Something strange got called: ", attribute)

        if result:
            return result

    def call_module_method(self, module: InputModule, func_name: str, args: list, kwargs: dict) -> Node:
        result = module.visit_call(func_name, args, kwargs)
        if result:
            if not result.library:
                result.library = module.module_name
            return result
        raise NotImplementedError(f"Rewrite rule for '{func_name}' of '{module.module_name}' is not implemented.")

    def call_module_ir_method(
        self, module: InputModule, ir_node: IRNode, func_name: str, args: list, kwargs: dict
    ) -> Node:
        result = module.visit_call_on_ir_node(ir_node, func_name, args, kwargs)
        if result:
            if not result.library:
                result.library = module.module_name
            return result
        raise NotImplementedError(
            f"Rewrite rule for '{func_name}' on IR object for '{module.module_name}' is not implemented."
        )

    def parse_Name(self, node: cst.Name) -> Optional[Node]:
        if node.value in self.variables:
            return self.variables[node.value]
        return node

    def parse_NonKwArg(self, node: cst.Arg) -> Node:
        arg_value = self.generic_visit(node.value)
        return arg_value

    def parse_KwArg(self, node: cst.Arg) -> tuple[str, Node]:
        arg_value = self.generic_visit(node.value)
        return node.keyword.value, arg_value

    def parse_Element(self, node: cst.Element) -> Optional[Node]:
        return self.generic_visit(node.value)

    def parse_Tuple(self, node: cst.Tuple) -> Sequence:
        ret_values = []
        for element in node.elements:
            ret_values.append(self.generic_visit(element))
        return tuple(ret_values)
