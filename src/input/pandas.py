from input.inputModule import InputModule
from model.nodes import AggregationNode, DataFrameNode, JoinNode, SetKeyNode, SQLNode


class PandasInput(InputModule):
    @property
    def module_name(self) -> str:
        return "pandas"

    # lib methods

    def visit_read_sql(self, *args, **kwargs):
        return SQLNode(*args, **kwargs)

    # df methods

    def visit_df_join(self, df_node: DataFrameNode, *args, **kwargs):
        return JoinNode(df_node, *args, **kwargs)

    def visit_df_merge(self, df_node: DataFrameNode, *args, **kwargs):
        return JoinNode(df_node, *args, **kwargs)

    def visit_df_set_index(self, df_node: DataFrameNode, *args, **kwargs):
        return SetKeyNode(df_node, *args, **kwargs)

    def visit_df_min(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "min", *args, **kwargs)

    def visit_df_max(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "max", *args, **kwargs)

    def visit_df_sum(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "sum", *args, **kwargs)

    def visit_df_mean(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "avg", *args, **kwargs)
