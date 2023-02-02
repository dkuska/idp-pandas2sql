from typing import Literal, Optional, Union

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


def make_list(value: str | list[str]) -> list[str]:
    if isinstance(value, str):
        return [value]
    return value


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

    def visit_df_sort_values(self, df_node: DataFrameNode, by, *, ascending=True, **kwargs):
        return SortNode(df_node, make_list(by), ascending, **kwargs)

    def visit_df_join(
        self,
        df_node: DataFrameNode,
        other: DataFrameNode,
        on: Optional[str | list[str]] = None,
        how: Optional[str] = None,
        lsuffix="",
        rsuffix="",
        sort=False,
        validate: Optional[bool] = None,
    ):
        _on: list[str] | Literal["key"]
        if on is None:
            _on = "key"
        else:
            _on = make_list(on)

        join_node = JoinNode(
            df_node, other, how=how, left_on=_on, right_on=_on, lsuffix=lsuffix, rsuffix=rsuffix, validate=validate
        )
        if sort:
            orderby = _on if isinstance(_on, list) else ["*"]  # TODO: Add key sorting ability
            return SortNode(join_node, orderby)
        return join_node

    def visit_df_merge(
        self,
        df_node: DataFrameNode,
        right: DataFrameNode,
        how: str = "inner",
        on: Optional[list[str] | str] = None,
        left_on: Optional[list[str] | str] = None,
        right_on: Optional[list[str] | str] = None,
        left_index=False,
        right_index=False,
        sort=False,
        suffixes=("_x", "_y"),
        copy=True,
        indicator=False,
        validate: Optional[bool] = None,
    ):
        _left_on: list[str] | Literal["key", "natural"] = "natural"
        _right_on: list[str] | Literal["key", "natural"] = "natural"
        if on:
            _left_on = make_list(on)
            _right_on = make_list(on)
        if left_on:
            _left_on = make_list(left_on)
        if right_on:
            _right_on = make_list(right_on)
        if left_index:
            _left_on = "key"
        if right_index:
            _right_on = "key"
        join_node = JoinNode(
            df_node,
            right,
            on=on,
            how=how,
            left_on=_left_on,
            right_on=_right_on,
            left_index=left_index,
            right_index=right_index,
            suffixes=suffixes,
            copy=copy,
            indicator=indicator,
            validate=validate,
        )
        if sort:
            orderby = _left_on if isinstance(_left_on, list) else ["*"]  # TODO: Add key sorting ability
            return SortNode(join_node, orderby)
        return join_node

    def visit_df_set_index(self, df_node: DataFrameNode, keys: str | list[str], *args, **kwargs):
        return SetKeyNode(df_node, make_list(keys), *args, **kwargs)

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
