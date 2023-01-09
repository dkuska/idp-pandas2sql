from input.inputModule import InputModule
from model.new_models import IRNode, JoinNode, SetKeyNode, SQLNode


class PandasInput(InputModule):
    @property
    def module_name(self) -> str:
        return "pandas"

    def visit_call(self, func_name: str, args: list, kwargs: dict):
        if func_name == "read_sql":
            return SQLNode(*args, **kwargs)

    def visit_call_on_ir_node(self, ir_node: IRNode, func_name: str, args: list, kwargs: dict):
        print("CALLIR", ir_node, func_name, args, kwargs)
        if func_name == "join":
            return JoinNode(ir_node, *args, **kwargs)
        if func_name == "set_index":
            return SetKeyNode(ir_node, *args, **kwargs)
