from model.nodes import IRNode


class InputModule:
    @property
    def module_name(self) -> str:
        pass

    @property
    def all_symbol_names(self) -> list[str]:
        """Return every symbol that is imported when importing * from the library"""
        return []

    def visit_call(self, func_name: str, args: list, kwargs: dict) -> IRNode:
        pass

    def visit_call_on_ir_node(self, ir_node: IRNode, func_name: str, args: list, kwargs: dict) -> IRNode:
        pass
