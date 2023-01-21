from ..ir.nodes import DataFrameNode, JoinNode, SQLNode
from .inputModule import InputModule


class DaskInput(InputModule):
    @property
    def module_name(self) -> str:
        return "dask.dataframe"

    # lib methods

    def visit_read_sql_query(self, *args, **kwargs):
        return SQLNode(*args, **kwargs)

    def visit_read_sql_table(self, table_name: str, *args, **kwargs):
        return SQLNode(f"SELECT * FROM {table_name}", *args, **kwargs)

    # df methods

    def visit_df_merge(self, df_node: DataFrameNode, *args, **kwargs):
        return JoinNode(df_node, *args, **kwargs)
