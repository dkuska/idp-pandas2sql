from collections.abc import Sequence

import libcst as cst
from model.nodes import AggregationNode, DataFrameNode, JoinNode, Node, SQLNode
from utils.pd_df_operations import (
    DF_OPERATIONS,
    PD_AGGREGATIONS,
    PD_ALIASES,
    PD_JOINS,
    PD_SQL,
)


class NodeSelector(cst.CSTVisitor):
    """
    Traverses Tree, detects if pandas was imported and saves relevant nodes.
    These nodes will then be passed to the IR
    """

    def __init__(self) -> None:
        self.pandas_imported: bool = False
        self.pandas_alias: str = ""
        self.pandas_imported_functions: list[str] = []

        self.nodes: list[Node] = []

        self.dataframes: list[str] = []

        super().__init__()

    def generic_visit(self, node: cst.CSTNode):
        class_name = str(node.__class__.__name__)
        class_name = class_name.replace("CST", "")  # Just in case there are weird class-names...

        method_name = f"visit_{class_name}"

        # TODO: Figure out better way for this, since libcst has methods defined for all types of nodes...
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(node)
        else:
            print(f"Function is not defined for: {method_name}")

    def visit_Arg(self, node: cst.Arg):
        arg_value = self.generic_visit(node.value)

        if node.keyword:
            arg_keyword = self.generic_visit(node.keyword)
            return arg_keyword, arg_value
        return arg_value

    def visit_Assign(self, node: cst.Assign):
        node_type = {
            "PANDAS_NODE": False,
            "DATAFRAME_NODE": False,
            "SQL_NODE": False,
            "JOIN_NODE": False,
            "AGGREGATION_NODE": False,
        }

        targets = []
        for target in node.targets:
            targets.append(self.generic_visit(target))

        values = self.generic_visit(node.value)
        if self.pandas_imported:
            if isinstance(values, list):
                # TODO: Figure this out, multiple return values
                pass
            elif isinstance(values, dict):
                node_type = self.recursively_visit_value(values)

        if node_type["AGGREGATION_NODE"]:
            this_node = AggregationNode(origin=node, targets=targets, values=values)
        elif node_type["JOIN_NODE"]:
            this_node = JoinNode(origin=node, targets=targets, values=values)
        elif node_type["SQL_NODE"]:
            this_node = SQLNode(origin=node, targets=targets, values=values)
        elif node_type["DATAFRAME_NODE"]:
            this_node = DataFrameNode(origin=node, targets=targets, values=values)
        else:
            this_node = Node(origin=node)

        self.nodes.append(this_node)

    def visit_Attribute(self, node: cst.Attribute) -> tuple:
        value = self.generic_visit(node.value)
        attr = self.generic_visit(node.attr)

        return {"value": value, "attr": attr}
        # return value, attr

    def visit_AssignTarget(self, node: cst.AssignTarget):
        ret_targets = []
        ret_targets.append(self.generic_visit(node.target))
        return ret_targets

    def visit_Call(self, node: cst.Call):
        func = self.generic_visit(node.func)
        args = []
        for arg in node.args:
            args.append(self.generic_visit(arg))

        return {"func": func, "args": args}

    def visit_Element(self, node: cst.Element):
        return self.generic_visit(node.value)

    def visit_Import(self, node: cst.Import):
        imports = []
        for importAlias in node.names:
            imports.append(self.generic_visit(importAlias))

        for imp in imports:
            lib_name, alias_name = imp

            # Pandas Check
            if lib_name in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = alias_name if alias_name is not None else lib_name

        self.nodes.append(Node(origin=node))

    def visit_ImportAlias(self, node: cst.ImportAlias):
        asname = ""
        if node.asname:
            asname = self.generic_visit(node.asname)
        return self.generic_visit(node.name), asname

    def visit_ImportFrom(self, node: cst.ImportFrom):

        module = self.generic_visit(node.module)

        imports = []
        if isinstance(node.names, Sequence):
            for name in node.names:
                imports.append(self.generic_visit(name))
        else:
            imports.append(self.generic_visit(node))

        # Pandas Check
        if module in PD_ALIASES or module in self.pandas_alias:
            self.pandas_imported = True
            self.pandas_imported_functions.append(imports)

        self.nodes.append(Node(origin=node))

    def visit_ImportStar(self, node: cst.ImportStar) -> str:
        return "*"

    def visit_Name(self, node: cst.Name) -> str:
        return node.value

    def visit_SimpleString(self, node: cst.SimpleString) -> str:
        return node.value

    def visit_Tuple(self, node: cst.Tuple) -> Sequence:
        ret_values = []
        for element in node.elements:
            ret_values.append(self.generic_visit(element))
        return ret_values

    def recursively_visit_value(self, value: dict):
        node_type = {
            "PANDAS_NODE": False,
            "DATAFRAME_NODE": False,
            "SQL_NODE": False,
            "JOIN_NODE": False,
            "AGGREGATION_NODE": False,
        }

        for key, val in value.items():
            if isinstance(val, dict):
                rec_result = self.recursively_visit_value(val)
                for key, value in rec_result.items():
                    if value == True:
                        node_type[key] = True

            else:
                # Pandas Node check
                if key == "value" and val in self.pandas_alias:
                    node_type["PANDAS_NODE"] = True
                # DataFrame Node check
                if key == "attr" and val in DF_OPERATIONS:
                    node_type["DATAFRAME_NODE"] = True
                # SQL Node check
                if key == "attr" and val in PD_SQL:
                    node_type["SQL_NODE"] = True
                #
                if key == "attr" and val in PD_JOINS:
                    node_type["JOIN_NODE"] = True
                if key == "attr" and val in PD_AGGREGATIONS:
                    node_type["AGGREGATION_NODE"] = True

        return node_type
