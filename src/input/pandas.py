from input.inputModule import InputModule
from model.nodes import AggregationNode, IRNode, JoinNode, SetKeyNode, SQLNode


class PandasInput(InputModule):
    @property
    def module_name(self) -> str:
        return "pandas"

    def visit_call(self, func_name: str, args: list, kwargs: dict):
        if func_name == "read_sql":
            return SQLNode(*args, **kwargs)
        if func_name == "merge":
            return JoinNode(*args, **kwargs)

    def visit_call_on_ir_node(self, ir_node: IRNode, func_name: str, args: list, kwargs: dict):
        if func_name == "join":
            return JoinNode(ir_node, *args, **kwargs)
        if func_name == "set_index":
            return SetKeyNode(ir_node, *args, **kwargs)
        if func_name == "min":
            return AggregationNode(ir_node, "min", *args, **kwargs)
        if func_name == "max":
            return AggregationNode(ir_node, "max", *args, **kwargs)
        if func_name == "sum":
            return AggregationNode(ir_node, "sum", *args, **kwargs)
        if func_name == "mean":  # watch out, mean is avg
            return AggregationNode(ir_node, "avg", *args, **kwargs)
