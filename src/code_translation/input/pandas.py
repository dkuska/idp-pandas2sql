from typing import Union

import libcst as cst

from ..ir.nodes import AggregationNode, DataFrameNode, JoinNode, SetKeyNode, SQLNode
from .inputModule import InputModule


class PandasInput(InputModule):
    @property
    def module_name(self) -> str:
        return "pandas"

    @property
    def sql_access_method(self) -> str:
        return "read_sql"

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

    def visit_df_aggregate(self, df_node: DataFrameNode, func: Union[str, cst.Name], *args, **kwargs):
        # func could be '"max"'
        if isinstance(func, cst.Name):
            func = func.value
        elif isinstance(func, str):
            func = func.strip('"').strip("'")
        # we need to replace 'mean' with 'avg'
        if func == "mean":
            func = "avg"
        return AggregationNode(df_node, func, *args, **kwargs)

    def visit_df_min(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "min", *args, **kwargs)

    def visit_df_max(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "max", *args, **kwargs)

    def visit_df_sum(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "sum", *args, **kwargs)

    def visit_df_mean(self, df_node: DataFrameNode, *args, **kwargs):
        return AggregationNode(df_node, "avg", *args, **kwargs)
