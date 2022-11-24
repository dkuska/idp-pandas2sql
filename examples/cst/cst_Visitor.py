import libcst as cst

class Visitor(cst.CSTVisitor):
    def __init__(self) -> None:
        self.pandas_imported = False
        self.pandas_alias = None
        self.import_stats = {}
        self.import_counter = 0
        self.assign_stats = {}
        self.assign_counter = 0
        self.df_stats = {}
        
        super().__init__()

    def visit_Import(self, node: cst.Import):
        print('Import:')
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                import_name = name.name.value
                alias_name = name.asname.name.value
                
                print(f'name: {import_name}')
                print(f'asname:{import_name}')
                
                ### PANDAS CHECK
                if import_name == 'pandas':
                    self.pandas_imported = True
                    self.pandas_alias = import_name
                    if alias_name != None:
                        self.pandas_alias = alias_name 
            self.import_counter += 1
        print()
        
    def visit_ImportFrom(self, node: cst.ImportFrom):
        print('ImportFrom:')
        module = node.module.value
        
        if module == 'pandas':
            self.pandas_imported = True
        
        print(f'module: {module}')
        for name in node.names:
            if isinstance(name, cst.ImportAlias):
                print(f'name: {name.name.value}')
        self.import_counter += 1   
        print()
        
    
    def visit_Assign(self, node: cst.Assign):
        print('Assign:')
        for target in node.targets:
            if isinstance(target, cst.Name):
                print(f'target.id: {target.value}')
            self.assign_counter += 1
            
        if isinstance(node.value, cst.Call):
            func = node.value.func
            if isinstance(func, cst.Attribute):
                print(f'func.value.id: {func.value.value}')
                print(f'func.attr:{func.attr.value}')
                
            args = node.value.args
            for arg in args:
                if isinstance(arg, cst.Arg):
                    if arg.keyword:
                        print(f'keyword.arg: {arg.keyword.value}')
                    print(f'arg.value: {arg.value.value}')        
        print()

    def report(self):
        print('Report:')
        print(f'pandas imported: {self.pandas_imported}')
        print(f'pandas_alias: {self.pandas_alias}')
        print(f'# imports {self.import_counter}')
        print(f'# assigns {self.assign_counter}')