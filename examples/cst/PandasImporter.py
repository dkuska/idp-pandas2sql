import libcst as cst

class PandasImporter(cst.CSTVisitor):
    """
    Traverses Tree, detects if pandas was imported and saves
    """

    def __init__(self) -> None:
        self.pandas_imported: bool = False
        self.pandas_star_imported: bool = True  # TODO: use this in code
        self.pandas_aliases = ["pandas"]
        self.imported_pandas_aliases: list[cst.ImportAlias] = []

        super().__init__()

    def visit_Import(self, node: cst.Import):
        imported_modules = list(node.names)

        for imported_module in imported_modules:
            if imported_module.evaluated_name != "pandas":
                continue
            if imported_module.evaluated_alias:
                self.pandas_aliases.append(imported_module.evaluated_alias)

    def visit_ImportFrom(self, node: cst.ImportFrom):
        imported_module_name = node.module.value
        if imported_module_name != "pandas":
            return

        # if it is an import star
        if isinstance(node.names, cst.ImportStar):
            self.pandas_star_imported = True
            return

        imported_elements = list(node.names)
        self.imported_pandas_aliases.extend(imported_elements)
