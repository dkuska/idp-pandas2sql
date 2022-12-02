import typing

import libcst as cst
from pprint import pprint

from utils.pd_df_operations import DF_OPERATIONS, PD_AGGREGATIONS, PD_ALIASES, PD_JOINS
from utils.assignment import Assignment
from utils.imports import Import, ImportFrom

class Visitor(cst.CSTVisitor):
    def __init__(self) -> None:
        self.pandas_imported = False
        self.pandas_alias = None

        self.imports = []  # Object used to keep track of imports in file
        self.imports_from = []

        self.assignments = []  # Object used to keep track of assignments

        self.dfs = []  # Object used to keep track of DataFrames
        self.sql_dfs = []

        super().__init__()


    def visit_Import(self, node: cst.Import) -> None:
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                import_name = name.name.value
                alias_name = ""
                if name.asname:
                    alias_name = name.asname.name.value
                    
                self.imports.append(Import(lib_name = import_name, alias = alias_name))


    def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
        module = node.module
        if isinstance(module, cst.Name):
            module_name = module.value
            imports = []
            if isinstance(node.names, typing.Sequence):
                for name in node.names:
                    if isinstance(name, cst.ImportAlias):
                        imports.append(name.name.value)
            elif isinstance(node.names, cst.ImportStar):
                imports.append('*')

            self.imports_from.append(ImportFrom(lib_name=module_name, imports=imports))
        elif isinstance(module, cst.Attribute):
            pass
        else:
            pass


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
            call_analysis = self.recursive_analyze_Call(node_value)
            call_analysis['position'] = 0
            
            values.append({'value': call_analysis})
        elif isinstance(node_value, cst.SimpleString):
            values.append({'value': node_value.value,
                           'position': 0})
        if isinstance(node_value, cst.Tuple):
            for i, element in enumerate(node_value.elements):
                ##TODO: Parse element.value if this is somethin complicated....
                if isinstance(element.value, cst.SimpleString):
                    values.append({'value': element.value.value,
                                   'position': i})
                    
        # Base case: Every assignment has one return value
        if len(targets) == len(values):
            for target, value in zip(targets, values):
                self.assignments.append(Assignment(var_name=target, value=value))
                
        elif len(targets) > len(values):
            pass  # TODO: Values returns multiple args    


    def recursive_analyze_Call(self, call: cst.Call):
        func = call.func
        lib, attribute = "", ""
        if isinstance(func, cst.Attribute):  # TODO: Figure out what other flows can be returned by call
            func_value = func.value
            # Func Value is simple name
            if isinstance(func_value, cst.Name):
                lib = func_value.value
            elif isinstance(func_value, cst.Call):
                lib = self.recursive_analyze_Call(func_value)  # Recursive call

            func_attr = func.attr
            if isinstance(func_attr, cst.Name):
                attribute = func_attr.value

        arguments = []
        args = call.args
        keywords = []
        for arg in args:
            keyword, argument = "", ""
            arg_value = arg.value
            if arg.keyword:
                arg_keyword = arg.keyword
                if isinstance(arg_keyword, cst.Name) or isinstance(arg_keyword, cst.SimpleString):
                    keyword = arg.keyword.value
                elif isinstance(arg_keyword, cst.Call):
                    keyword = self.recursive_analyze_Call(arg_keyword)
            else:
                if isinstance(arg_value, cst.Arg) or isinstance(arg_value, cst.SimpleString):
                    argument = arg_value.value
                elif isinstance(arg_value, cst.Call):
                    argument = self.recursive_analyze_Call(arg_value)
                
            if keyword == "":
                arguments.append(argument)
            else:
                keywords.append({'keyword': keywords,
                                 'argument': argument})
                
        ## TODO: Persist this somehow...
        print(f'lib: {lib}')
        print(f'attribute: {attribute}')
        print(f'arguments: {arguments}')
        print(f'keywords: {keywords}')
        
        return_dict = {
            'lib': lib,
            'attribute': attribute,
            'arguments': arguments,
            'keywords': keywords
        }

        return return_dict


    def analyze_assignments(self):
        # First analyze all assignments
        for assignment in self.assignments:
            value = assignment.value['value']
            
            if isinstance(value, str):
                for df_operation in DF_OPERATIONS:            
                    if df_operation in value['lib']:
                        self.dfs.append(assignment)
            elif isinstance(value, dict):
                pass
            
        # Then analyze all DFs for SQL and AGGREGATIOn
        for df in self.dfs:
            print(df)
            pass

    
    def analyze_imports(self):
        for imp in self.imports:       
            ### PANDAS CHECK
            if imp.lib_name in PD_ALIASES or imp.alias in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = imp.alias
                if imp.alias == '':
                    self.pandas_alias = imp.lib_names
        for imp in self.imports_from:
            if imp.lib_name in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = imp.lib_name
    
    
    def print_summary(self):
        print("Report:")

        print(f"# imports {len(self.imports) + len(self.imports_from)}")
        for imp in self.imports:
            print(imp)
            
        for imp_from in self.imports_from:
            print(imp_from)

        print(f"pandas imported: {self.pandas_imported}")
        print(f"pandas_alias: {self.pandas_alias}")

        print(f"# assignments {len(self.assignments)}")
        for assignment in self.assignments:
            print(assignment.var_name)
            pprint(assignment.value)
            
            
        print(f"# dfs {len(self.dfs)}")
        for df in self.dfs:
            pprint(df)
