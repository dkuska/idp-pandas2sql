from collections.abc import Sequence

import libcst as cst
from model.nodes import AggregationNode, JoinNode, Node, PandasNode, SQLNode
from utils.cst_utils import parse_targets, parse_values
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
        class_name = class_name.replace("CST", "")

        method_name = f"visit_{class_name}"

        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(node)
        else:
            print(f"Function is not defined for: {method_name}")

    def visit_Import(self, node: cst.Import) -> None:
        imports = []
        for importAlias in node.names:
            imports.append(self.generic_visit(importAlias))

        for imp in imports:
            lib_name, alias_name = imp

            # Pandas Check
            if lib_name in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = alias_name

        self.nodes.append(Node(origin=node))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:

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

    def visit_Assign(self, node: cst.Assign):
        node_type = {
            "PANDAS_NODE": False,
            "DATAFRAME_NODE": False,
            "SQL_NODE": False,
            "JOIN_NODE": False,
            "AGGREGATION_NODE": False,
        }

        targets = parse_targets(node.targets)
        values = parse_values(node.value)

        if self.pandas_imported:
            # Persist results
            if len(targets) == len(values):
                for target, value in zip(targets, values):
                    node_type = self.recursively_visit_value(value)
                    for key, val in node_type.items():
                        if val:
                            node_type[key] = True

            elif len(targets) > len(values):
                pass  # TODO: Values returns multiple args
        else:
            self.nodes.append(Node(origin=node))

        if node_type["AGGREGATION_NODE"]:
            this_node = AggregationNode(origin=node)
        elif node_type["JOIN_NODE"]:
            this_node = JoinNode(origin=node)
        elif node_type["SQL_NODE"]:
            this_node = SQLNode(origin=node)
        elif node_type["PANDAS_NODE"]:
            this_node = PandasNode(origin=node)
        else:
            this_node = Node(origin=node)

        self.nodes.append(this_node)

    def visit_ImportAlias(self, node: cst.ImportAlias):
        asname = ""
        if node.asname:
            asname = self.generic_visit(node.asname)
        return self.generic_visit(node.name), asname

    def visit_ImportStar(self, node: cst.ImportStar) -> str:
        return "*"

    def visit_Attribute(self, node: cst.Attribute) -> tuple:
        value = self.generic_visit(node.value)
        attr = self.generic_visit(node.attr)

        return value, attr

    def visit_Tuple(self, node: cst.Tuple) -> Sequence[str]:
        ret_values = []
        for element in node.elements:
            ret_values.append(self.generic_visit(element))
        return ret_values

    def visit_Name(self, node: cst.Name) -> str:
        return node.value

    def visit_SimpleString(self, node: cst.SimpleString) -> str:
        return node.value

    def recursively_visit_value(self, value: dict):
        node_type = {
            "PANDAS_NODE": False,
            "DATAFRAME_NODE": False,
            "SQL_NODE": False,
            "JOIN_NODE": False,
            "AGGREGATION_NODE": False,
        }

        for key, val in value.items():
            print(f"key:   {key}")
            print(f"value: {val}")

            if isinstance(val, dict):
                rec_result = self.recursively_visit_value(val)

                for key, value in rec_result.items():
                    if value == True:
                        node_type[key] = True

            else:
                if key == "caller" and val in self.pandas_alias:
                    node_type["PANDAS_NODE"] = True

                if key == "attribute" and val in DF_OPERATIONS:
                    node_type["DATAFRAME_NODE"] = True

                if key == "attribute" and val in PD_SQL:
                    node_type["SQL_NODE"] = True

                if key == "attribute" and val in PD_JOINS:
                    node_type["JOIN_NODE"] = True

                if key == "attribute" and val in PD_AGGREGATIONS:
                    node_type["AGGREGATION_NODE"] = True

        print(node_type)
        return node_type
