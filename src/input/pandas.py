from input.inputModule import InputModule
from model.nodes import AggregationNode, IRNode, JoinNode, SetKeyNode, SQLNode


class PandasInput(InputModule):
    @property
    def module_name(self) -> str:
        return "pandas"

    # lib methods

    def visit_read_sql(self, *args, **kwargs):
        return SQLNode(*args, **kwargs)

    # df methods

    def visit_df_join(self, ir_node: IRNode, *args, **kwargs):
        return JoinNode(ir_node, *args, **kwargs)

    def visit_df_merge(self, ir_node: IRNode, *args, **kwargs):
        return JoinNode(ir_node, *args, **kwargs)

    def visit_df_set_index(self, ir_node: IRNode, *args, **kwargs):
        return SetKeyNode(ir_node, *args, **kwargs)

    def visit_df_min(self, ir_node: IRNode, *args, **kwargs):
        return AggregationNode(ir_node, "min", *args, **kwargs)

    def visit_df_max(self, ir_node: IRNode, *args, **kwargs):
        return AggregationNode(ir_node, "max", *args, **kwargs)

    def visit_df_sum(self, ir_node: IRNode, *args, **kwargs):
        return AggregationNode(ir_node, "sum", *args, **kwargs)

    def visit_df_mean(self, ir_node: IRNode, *args, **kwargs):
        return AggregationNode(ir_node, "avg", *args, **kwargs)
