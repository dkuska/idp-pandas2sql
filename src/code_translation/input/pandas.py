from typing import Optional, Union

import libcst as cst

from ..ir.nodes import (
    AggregationNode,
    DataFrameNode,
    JoinNode,
    SetKeyNode,
    SortNode,
    SQLNode,
)
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

    def visit_df_sort_values(self, df_node: DataFrameNode, *args, **kwargs):
        return SortNode(df_node, *args, **kwargs)

    def visit_df_join(
        self,
        df_node: DataFrameNode,
        other: DataFrameNode,
        on: Optional[str] = None,
        how: Optional[str] = None,
        lsuffix="",
        rsuffix="",
        sort=False,
        validate: Optional[bool] = None,
    ):
        join_node = JoinNode(df_node, other, on=on, how=how, lsuffix=lsuffix, rsuffix=rsuffix, validate=validate)
        if sort:
            return SortNode(join_node)
        return join_node

    def visit_df_merge(
        self,
        df_node: DataFrameNode,
        right: DataFrameNode,
        how: Optional[str] = None,
        on: Optional[str] = None,
        left_on: Optional[str] = None,
        right_on: Optional[str] = None,
        left_index=False,
        right_index=False,
        sort=False,
        suffixes=("_x", "_y"),
        copy=True,
        indicator=False,
        validate: Optional[bool] = None,
    ):
        join_node = JoinNode(
            df_node,
            right,
            on=on,
            how=how,
            left_on=left_on,
            right_on=right_on,
            left_index=left_index,
            right_index=right_index,
            suffixes=suffixes,
            copy=copy,
            indicator=indicator,
            validate=validate,
        )
        if sort:
            return SortNode(join_node)
        return join_node

    def visit_df_set_index(self, df_node: DataFrameNode, *args, **kwargs):
        return SetKeyNode(df_node, *args, **kwargs)

    def visit_df_aggregate(self, df_node: DataFrameNode, func: Union[str, cst.CSTNode], *args, **kwargs):
        if isinstance(func, cst.Name):
            func = func.value
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
