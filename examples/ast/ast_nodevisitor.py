from ast import *

# from pd_df_operations import DF_OPERATIONS


#### NodeVisitor
class Analyzer(NodeVisitor):
    def __init__(self) -> None:
        self.pandas_imported = False
        self.pandas_alias = None
        self.import_stats = {}
        self.import_counter = 0
        self.assign_stats = {}
        self.assign_counter = 0

        self.df_stats = {}

        super().__init__()

    def visit_Import(self, node: Import):
        print("Import:")
        for name in node.names:
            if isinstance(name, alias):
                print(f"name: {name.name}")
                print(f"asname:{name.asname}")

                ### PANDAS CHECK
                if name.name == "pandas":
                    self.pandas_imported = True
                    if name.asname != None:
                        self.pandas_alias = name.asname

            self.import_counter += 1
        print()
        self.generic_visit(node)

    def visit_ImportFrom(self, node: ImportFrom):
        # TODO:
        self.generic_visit(node)

    def visit_Assign(self, node: Assign):
        print("Assign:")
        for target in node.targets:
            if isinstance(target, Name):
                print(f"target.id: {target.id}")
            self.assign_counter += 1

        if isinstance(node.value, Call):
            func = node.value.func
            if isinstance(func, Attribute):
                print(f"func.value.id: {func.value.id}")
                print(f"func.attr:{func.attr}")

            args = node.value.args
            for arg in args:
                if isinstance(arg, Constant):
                    print(f"arg.value: {arg.value}")

            keywords = node.value.keywords
            for keyword in keywords:
                print(f"keyword.arg: {keyword.arg}")
                print(f"keyword.value.value: {keyword.value.value}")
                pass

        print()
        self.generic_visit(node)

    def report(self):
        print(f"pandas imported: {self.pandas_imported}")
        print(f"pandas_alias: {self.pandas_alias}")
        print(f"# imports {self.import_counter}")
        print(f"# assigns {self.assign_counter}")
