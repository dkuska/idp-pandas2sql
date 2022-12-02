import typing

import libcst as cst


class Visitor(cst.CSTVisitor):
    def __init__(self) -> None:
        self.pandas_imported = False
        self.pandas_alias = None

        self.imports = {}  # Object used to keep track of imports in file
        self.imports_from = {}
        self.import_counter = 0

        self.assignments = {}  # Object used to keep track of assignments
        self.assign_counter = 0

        self.dfs = {}  # Object used to keep track of DataFrames

        super().__init__()

    def visit_Import(self, node: cst.Import):
        print("Import:")
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                import_name = name.name.value
                print(f"name: {import_name}")

                alias_name = None
                if name.asname:
                    alias_name = name.asname.name.value
                    print(f"asname:{alias_name}")
                    self.imports[import_name] = alias_name
                else:
                    self.imports[import_name] = import_name

                ### PANDAS CHECK
                if import_name == "pandas":
                    self.pandas_imported = True
                    self.pandas_alias = import_name
                    if alias_name != None:
                        self.pandas_alias = alias_name
            self.import_counter += 1
        print()

    def visit_ImportFrom(self, node: cst.ImportFrom):
        print("ImportFrom:")

        module = node.module
        if isinstance(module, cst.Name):
            module_name = module.value
            if module_name not in self.imports_from:
                self.imports_from[module_name] = []

            if module_name == "pandas":
                self.pandas_imported = True

            print(f"module_name: {module_name}")
            if isinstance(node.names, typing.Sequence):
                for name in node.names:
                    if isinstance(name, cst.ImportAlias):
                        print(f"name: {name.name.value}")
                        self.imports_from[module_name].append(name.name.value)
            elif isinstance(node.names, cst.ImportStar):
                print(f"name: STAR(*)")
                self.imports_from[module_name].append("*")
            pass
        elif isinstance(module, cst.Attribute):
            # TODO: Do something in this case
            pass
        else:
            # module is None
            pass

        self.import_counter += 1
        print()

    def visit_Assign(self, node: cst.Assign):
        targets = []
        values = []

        ## Parse targets
        for target in node.targets:
            if isinstance(target, cst.AssignTarget):
                target_target = target.target
                if isinstance(target_target, cst.Name):
                    targets.append(target_target.value)
                elif isinstance(target_target, cst.Tuple):
                    for element in target_target.elements:
                        if isinstance(element.value, cst.Name):
                            targets.append(element.value.value)

        ## Parse values
        node_value = node.value
        if isinstance(node_value, cst.Call):
            values.append(analyze_Call(node_value))
        elif isinstance(node_value, cst.SimpleString):
            values.append(node_value.value)
        if isinstance(node_value, cst.Tuple):
            for element in node_value.elements:
                ## TODO: Parse element.value if this is somethin complicated....

                if isinstance(element.value, cst.SimpleString):
                    values.append(element.value.value)

        # DEBUG
        print("Assign:")
        print(f'{", ".join(targets)} = {", ".join(values)}')
        print()

        # TODO: Persist targets and values somehow..
        self.assign_counter += len(targets)

    def report(self):
        print("Report:")
        print(f"pandas imported: {self.pandas_imported}")
        print(f"pandas_alias: {self.pandas_alias}")
        print(f"# imports {self.import_counter}")
        for key, value in self.imports.items():
            print(f"imported {key} as {value}")
        for key, value in self.imports_from.items():
            print(f'from {key} import {", ".join(value)}')

        print(f"# assigns {self.assign_counter}")


def analyze_Call(call: cst.Call):
    func = call.func
    lib, attribute = "", ""
    if isinstance(func, cst.Attribute):  # TODO: Figure out what other flows can be returned by call
        func_value = func.value
        # Func Value is simple name
        if isinstance(func_value, cst.Name):
            lib = func_value.value
        elif isinstance(func_value, cst.Call):
            lib = analyze_Call(func_value)  # Recursive call

        func_attr = func.attr
        if isinstance(func_attr, cst.Name):
            attribute = func_attr.value

    args = call.args
    parts_n = []
    for arg in args:
        keyword, argument = "", ""
        arg_value = arg.value
        if arg.keyword:
            arg_keyword = arg.keyword
            if isinstance(arg_keyword, cst.Name) or isinstance(arg_keyword, cst.SimpleString):
                keyword = arg.keyword.value
            elif isinstance(arg_keyword, cst.Call):
                keyword = analyze_Call(arg_keyword)

        if isinstance(arg_value, cst.Arg) or isinstance(arg_value, cst.SimpleString):
            argument = arg_value.value
        elif isinstance(arg_value, cst.Call):
            argument = analyze_Call(arg_value)

        if keyword == "":
            parts_n.append(argument)
        else:
            parts_n.append("=".join([keyword, argument]))

    ## TODO: Persist this somehow...
    return_value = lib + "." + attribute + "(" + ",".join(parts_n) + ")"

    return return_value
