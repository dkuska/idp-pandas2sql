from abc import ABC

import libcst as cst
from libcst import CSTNode


class IRNode(ABC):
    def __init__(self, parent=None, library=None, *args, **kwargs):
        self.parent = parent
        self.library = library
        if args or kwargs:
            print(f"These args: {args} and kwargs: {list(kwargs.keys())} don't have a translation rule yet")


class DataFrameNode(IRNode):
    pass


class SQLNode(DataFrameNode):
    def __init__(self, sql: CSTNode, con, *args, **kwargs):
        self.sql = sql
        self.con = con

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self):
        return self.sql.replace('"', "")

    def to_code(self):
        return f"read_sql({self.sql_string}, SOME CON)"

    def to_cst_node(self, variable: str):
        if True:
            func = cst.Name(value="read_sql")
        else:  # TODO: Needs awareness of used alias
            func = cst.Attribute(value=cst.Name(value=self.pandas_alias), attr=cst.Name(value="read_sql"))

        args = [cst.Arg(value=cst.SimpleString(value= '"' + self.sql_string + '"'))]

        call = cst.Call(func=func, args=args)

        targets = [cst.AssignTarget(target=cst.Name(variable))]  # TODO: Needs awareness of assignment name
        assign = cst.Assign(targets=targets, value=call)
        return assign

    def to_cst_statement(self, variable: str):
        return cst.SimpleStatementLine(body=[self.to_cst_node(variable)])


class JoinNode(DataFrameNode):
    def __init__(self, left: DataFrameNode, right: DataFrameNode, *args, **kwargs):
        left.parent = self
        right.parent = self

        self.left = left
        self.right = right

        super().__init__(*args, **kwargs)

    def to_code(self):
        if hasattr(self.left, "sql_string") and hasattr(self.right, "sql_string"):
            return f"read_sql('SELECT * FROM ({self.left.sql_string}) JOIN ({self.right.sql_string})')"
        else:
            return f"({self.left.to_code()}).join({self.right.to_code()})"

    def to_cst_node(self, variable: str):
        # Extract query and additional information from left node
        left_set_key = False
        if isinstance(self.left, SQLNode):
            left_sql = self.left.sql_string.replace('"', "")
            pass
        elif isinstance(self.left, SetKeyNode):
            left_set_key = True
            left_sql = self.left.node.sql_string.replace('"', "")
            left_key = self.left.key.replace('"', "").replace("'", "")
        else:
            pass

        # Extract query and additional information from right node
        right_set_key = False
        if isinstance(self.left, SQLNode):
            right_sql = self.right.sql_string.replace('"', "")
            pass
        elif isinstance(self.left, SetKeyNode):
            right_set_key = True
            right_sql = self.right.node.sql_string.replace('"', "")
            right_key = self.right.key.replace('"', "").replace("'", "")  # TODO: Implement for more complex types
        else:
            pass

        # Build query string
        if left_set_key or right_set_key:
            # TODO: DataFrameNode needs key also aka 'index_col' in read_sql
            left_table_alias = "S1"
            right_table_alias = "S2"
            query_str = f"SELECT * FROM ({left_sql}) AS {left_table_alias} JOIN ({right_sql}) AS {right_table_alias} ON {left_table_alias}.{left_key} = {right_table_alias}.{right_key}"

        else:
            query_str = f"SELECT * FROM ({left_sql}) JOIN ({right_sql})"

        query_str = '"' + query_str + '"'

        # Build cst.Assign Object
        if True:
            func = cst.Name(value="read_sql")
        else:  # TODO: Needs awareness of used alias
            func = cst.Attribute(value=cst.Name(value=self.pandas_alias), attr=cst.Name(value="read_sql"))
        args = [cst.Arg(value=cst.SimpleString(value=query_str))]

        call = cst.Call(func=func, args=args)

        targets = [cst.AssignTarget(target=cst.Name(variable))]  # TODO: Needs awareness of assignment name
        assign = cst.Assign(targets=targets, value=call)

        return assign

    def to_cst_statement(self, variable: str):
        return cst.SimpleStatementLine(body=[self.to_cst_node(variable)])


class SetKeyNode(DataFrameNode):
    def __init__(self, node: DataFrameNode, key: CSTNode, *args, **kwargs):
        node.parent = self

        self.node = node
        self.key = key

        super().__init__(*args, **kwargs)

    def to_code(self):
        return f"({self.node.to_code()}).set_key({self.key})"

    def to_cst_node(self, target):
        func = cst.Attribute(value=self.node.to_cst_statement(), attr="join")
        args = [cst.Arg(value=self.key)]

        call = cst.Call(func=func, args=args)

        targets = [cst.AssignTarget(target=cst.Name(value=target))]
        assign = cst.Assign(targets=targets, value=call)

        return assign

    def to_cst_statement(self):
        return cst.SimpleStatementLine(body=[self.to_cst_node()])
