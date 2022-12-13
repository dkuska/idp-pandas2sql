from collections.abc import Sequence
from pprint import pprint

import libcst as cst
from model.assignment import Assignment
from model.imports import Import, ImportFrom
from utils.cst_utils import (
    get_Attribute_information,
    get_ImportAlias_information,
    get_Name_value,
    parse_targets,
    parse_values,
)
from utils.pd_df_operations import (
    DF_OPERATIONS,
    PD_AGGREGATIONS,
    PD_ALIASES,
    PD_JOINS,
    PD_SQL,
)


class Visitor(cst.CSTVisitor):
    def __init__(self) -> None:

        self.imports: list[Import] = []  # Object used to keep track of imports in file
        self.imports_from: list[ImportFrom] = []
        self.pandas_imported = False
        self.pandas_alias = None

        self.assignments: list[Assignment] = []  # Object used to keep track of assignments

        self.dfs: list[Assignment] = []  # Object used to keep track of DataFrames
        self.sql_dfs: list[Assignment] = []
        self.join_dfs: list[Assignment] = []
        self.aggregation_dfs: list[Assignment] = []

        super().__init__()

    def visit_Import(self, node: cst.Import) -> None:
        imports = []
        for importAlias in node.names:
            imports.append(get_ImportAlias_information(importAlias))

        for imp in imports:
            lib_name, alias_name = imp
            self.imports.append(Import(lib_name=lib_name, alias=alias_name))

    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        module = node.module
        if isinstance(module, cst.Name):
            module = get_Name_value(module)
        elif isinstance(module, cst.Attribute):
            module = get_Attribute_information(module)
        else:
            pass  # TODO

        imports = []
        if isinstance(node.names, Sequence):
            for name in node.names:
                imports.append(get_ImportAlias_information(name))
        elif isinstance(node.names, cst.ImportStar):
            imports.append("*")
        else:
            pass  # TODO

        self.imports_from.append(ImportFrom(lib_name=module, imports=imports))

    def visit_Assign(self, node: cst.Assign):
        targets = parse_targets(node.targets)
        values = parse_values(node.value)

        # Persist results
        if len(targets) == len(values):
            for target, value in zip(targets, values):
                self.assignments.append(Assignment(var_name=target, value=value))
        elif len(targets) > len(values):
            pass  # TODO: Values returns multiple args

    def analyze_assignments(self):
        """
        Analyze the assignments inside self.assignments.
        Checks if DataFrame Objects and SQL/JOIN/Aggregation operations are present somewhere.
        Very 'stupid' first drauft of an implementation.
        Ideally this should split up into more functions.
        First Pandas, then SQL, then JOIN/Aggregation
        """
        # First analyze all assignments
        for assignment in self.assignments:
            value = assignment.value["value"]  # TODO: Rethink these god damn names....
            # print(type(value))

            ### Simple assignments with singular values like `s='abc'` are caught with this branch
            if isinstance(value, str):
                for df_operation in DF_OPERATIONS:
                    if df_operation in value:
                        self.dfs.append(assignment)
            # Otherwise more sophisticated analysis is necessary.
            # Should include recursive search of the dict, since for nested calls this contains even more dicts....
            elif isinstance(value, dict):
                # pprint(value)
                for relevant_key in ["caller", "attribute"]:
                    value_entry = value[relevant_key]

                    for df_operation in DF_OPERATIONS:
                        if df_operation in value_entry:
                            assignment.pandas = True
                            self.dfs.append(assignment)

                    for sql_operation in PD_SQL:
                        if sql_operation in value_entry:
                            assignment.sql = True
                            self.sql_dfs.append(assignment)

                    for join_operation in PD_JOINS:
                        if join_operation in value_entry:
                            assignment.join = True
                            self.join_dfs.append(assignment)

                    for agg_operation in PD_AGGREGATIONS:
                        if agg_operation in value_entry:
                            assignment.aggregation = True
                            self.aggregation_dfs.append(assignment)

        # Then analyze all DFs for SQL and AGGREGATIOn
        for df in self.dfs:
            pass

    def analyze_imports(self):
        """
        Analyze imports and imports_from for pandas.
        If pandas operations are not included, the rest of the processing could be skipped.
        """
        for imp in self.imports:
            ### PANDAS CHECK
            if imp.lib_name in PD_ALIASES or imp.alias in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = imp.alias
                if imp.alias == "":
                    self.pandas_alias = imp.lib_names

        for imp in self.imports_from:
            if imp.lib_name in PD_ALIASES:
                self.pandas_imported = True

    def print_summary(self):
        """
        Util for debugging purposes.
        """
        print("### Imports ###")
        print(f"# imports {len(self.imports) + len(self.imports_from)}")
        for imp in self.imports:
            print(imp)
        for imp_from in self.imports_from:
            print(imp_from)

        print(f"pandas imported: {self.pandas_imported}")
        print(f"pandas_alias: {self.pandas_alias}")
        print()

        print("### Assignments ###")
        print(f"# assignments {len(self.assignments)}")
        for assignment in self.assignments:
            print(assignment.var_name)
            print("=")
            pprint(assignment.value)
        print()

        print("### DataFrames ###")
        print(f"# dfs {len(self.dfs)}")
        for df in self.dfs:
            print(df.var_name)
            print("=")
            pprint(df.value)
        print()

        print("### SQL ###")
        print(f"# sql_dfs {len(self.sql_dfs)}")
        for sql_df in self.sql_dfs:
            print(sql_df.var_name)
            print("=")
            pprint(sql_df.value)
        print()

        print("### JOIN ###")
        print(f"# join_dfs {len(self.join_dfs)}")
        for join_df in self.join_dfs:
            print(join_df.var_name)
            print("=")
            pprint(join_df.value)
        print()

        print("### Aggregations ###")
        print(f"# aggregation_dfs {len(self.aggregation_dfs)}")
        for agg_df in self.aggregation_dfs:
            print(agg_df.var_name)
            print("=")
            pprint(agg_df.value)
        print()
