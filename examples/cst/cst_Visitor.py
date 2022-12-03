import typing

import libcst as cst
from pprint import pprint

from utils.pd_df_operations import DF_OPERATIONS, PD_AGGREGATIONS, PD_ALIASES, PD_JOINS, PD_SQL
from utils.assignment import Assignment
from utils.imports import Import, ImportFrom

class Visitor(cst.CSTVisitor):
    def __init__(self) -> None:
        self.pandas_imported = False
        self.pandas_alias = None

        self.imports: list[Import] = []  # Object used to keep track of imports in file
        self.imports_from: list[ImportFrom] = []

        self.assignments: list[Assignment] = []  # Object used to keep track of assignments

        self.dfs: list[Assignment] = []  # Object used to keep track of DataFrames
        self.sql_dfs: list[Assignment] = []
        self.join_dfs: list[Assignment] = []
        self.aggregation_dfs: list[Assignment] = []

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
        """
        recursively analyze the Call object and return a dict containing information about it.
        cst.Call consists of 2 main parts: func & args
        func is the calling variable (can also be another call in case of chained invocations )
        args is the list of arguments in the order in which they appear
        """   

        # Parse first part of the call - caller/func
        func = call.func
        caller, attribute = "", ""
        if isinstance(func, cst.Attribute):  # TODO: Figure out what other flows can be returned by call
            func_value = func.value
            # Func Value is a variable name
            if isinstance(func_value, cst.Name):
                caller = func_value.value
            # Func value itself is another call
            elif isinstance(func_value, cst.Call):
                caller = self.recursive_analyze_Call(func_value)  # Recursive call

            ## func.attr is always a cst.Name
            func_attr = func.attr
            if isinstance(func_attr, cst.Name):
                attribute = func_attr.value

        # Parse second part - args
        arguments = []
        args = call.args
        keywords = []
        for arg in args:
            keyword, argument = "", ""
            arg_value = arg.value
            # Keyword is either a name or None
            if arg.keyword:
                arg_keyword = arg.keyword
                if isinstance(arg_keyword, cst.Name):
                    keyword = arg.keyword.value
                    
                    
            if isinstance(arg_value, cst.Arg):
                argument = arg_value.value
            elif isinstance(arg_value, cst.SimpleString):
                argument = arg_value.value
            elif isinstance(arg_value, cst.Name):
                argument = arg_value.value
            elif isinstance(arg_value, cst.Call):
                argument = self.recursive_analyze_Call(arg_value)
                
            if keyword == "":
                arguments.append(argument)
            else:
                keywords.append({'keyword': keyword,
                                 'argument': argument})
                
        ## TODO: Persist this somehow...
        # print(f'lib: {lib}')
        # print(f'attribute: {attribute}')
        # print(f'arguments: {arguments}')
        # print(f'keywords: {keywords}')
        
        return_dict = {
            'caller': caller,   # Variable on which the function is called
            'attribute': attribute, # Attribute/Function of the caller
            'arguments': arguments, # For functions this includes positional arguments, should include order in the future probably
            'keyword_arguments': keywords # Keyword arguments with name of the keyword and value. 
        }
        return return_dict


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
            value = assignment.value['value']  # TODO: Rethink these god damn names....
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
                for relevant_key in ['caller', 'attribute']:
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
                if imp.alias == '':
                    self.pandas_alias = imp.lib_names
                    
        for imp in self.imports_from:
            if imp.lib_name in PD_ALIASES:
                self.pandas_imported = True
                self.pandas_alias = imp.lib_name
    
    
    def print_summary(self):
        """
        Util for debugging purposes.
        """
        print('### Imports ###')
        print(f"# imports {len(self.imports) + len(self.imports_from)}")
        for imp in self.imports:
            print(imp)
        for imp_from in self.imports_from:
            print(imp_from)

        print(f"pandas imported: {self.pandas_imported}")
        print(f"pandas_alias: {self.pandas_alias}")
        print()
        
        print('### Assignments ###')
        print(f"# assignments {len(self.assignments)}")
        for assignment in self.assignments:
            print(assignment.var_name)
            print('=')
            pprint(assignment.value)
        print()
            
        print('### DataFrames ###')
        print(f"# dfs {len(self.dfs)}")
        for df in self.dfs:
            print(df.var_name)
            print('=')
            pprint(df.value)
        print()
            
        print('### SQL ###')
        print(f"# sql_dfs {len(self.sql_dfs)}")
        for sql_df in self.sql_dfs:
            print(sql_df.var_name)
            print('=')
            pprint(sql_df.value)
        print()
            
        print('### JOIN ###')
        print(f"# join_dfs {len(self.join_dfs)}")
        for join_df in self.join_dfs:
            print(join_df.var_name)
            print('=')
            pprint(join_df.value)
        print()
            
        print('### Aggregations ###')
        print(f"# aggregation_dfs {len(self.aggregation_dfs)}")
        for agg_df in self.aggregation_dfs:
            print(agg_df.var_name)
            print('=')
            pprint(agg_df.value)
        print()
