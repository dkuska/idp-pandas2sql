from input.inputModule import InputModule
from model.nodes import IRNode, JoinNode, SQLNode


class DaskInput(InputModule):
    @property
    def module_name(self) -> str:
        return "dask.dataframe"

    # lib methods

    def visit_read_sql_query(self, *args, **kwargs):
        return SQLNode(*args, **kwargs)

    def visit_read_sql_table(self, *args, **kwargs):
        if "table_name" in kwargs:
            table_name = kwargs["table_name"]
            del kwargs["table_name"]
        else:
            table_name = args[0]
            args = args[1:]
        return SQLNode(f"SELECT * FROM {table_name}", *args, **kwargs)

    # df methods

    def visit_df_merge(self, ir_node: IRNode, *args, **kwargs):
        return JoinNode(ir_node, *args, **kwargs)
