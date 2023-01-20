from abc import ABC, abstractmethod
from typing import NamedTuple

import libcst as cst

# TODO:
# when translating forwards the args
# replace SOME CONN with the actual conn


def str_code_to_cst(code: str):
    cst_tree = cst.parse_expression(code)
    return cst_tree


class CSTTranslation(NamedTuple):
    code: cst.CSTNode
    precode: list[cst.CSTNode] = []
    postcode: list[cst.CSTNode] = []


class IRNode(ABC):
    def __init__(self, parent=None, library=None, *args, **kwargs):
        self.parent = parent
        self.library = library
        if args or kwargs:
            print(f"These args: {args} and kwargs: {list(kwargs.keys())} don't have a translation rule yet")

    @abstractmethod
    def to_cst_translation(self) -> CSTTranslation:
        pass


class DataFrameNode(IRNode):
    @property
    def sql_string(self):
        pass


class SQLNode(DataFrameNode):
    def __init__(self, sql: cst.CSTNode, con, *args, **kwargs):
        self.sql = sql
        self.con = con

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        return self.sql.replace('"', "")

    def to_code(self) -> str:
        return f'read_sql("{self.sql_string}", SOME CON)'

    def to_cst_translation(self) -> CSTTranslation:
        if True:
            func = cst.Name(value="read_sql")
        else:  # TODO: Needs awareness of used alias
            func = cst.Attribute(value=cst.Name(value=self.pandas_alias), attr=cst.Name(value="read_sql"))

        args = [cst.Arg(value=cst.SimpleString(value='"' + self.sql_string + '"'))]

        return CSTTranslation(code=cst.Call(func=func, args=args))


class JoinNode(DataFrameNode):
    def __init__(self, left: DataFrameNode, right: DataFrameNode, *args, **kwargs):
        left.parent = self
        right.parent = self

        self.left = left
        self.right = right

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        if self.left.sql_string and self.right.sql_string:  # check if two connections are the same
            return f"'SELECT * FROM ({self.left.sql_string}) JOIN ({self.right.sql_string})')"

    def to_code(self) -> str:
        if self.sql_string:
            return f'read_sql("{self.sql_string}", SOME CONN)'  # get the con from children
        else:
            return f"({self.left.to_code()}).join({self.right.to_code()})"

    def to_cst_translation(self) -> CSTTranslation:
        # Extract query and additional information from left node
        left_set_key = False
        if isinstance(self.left, SQLNode):
            left_sql = self.left.sql_string.replace('"', "")
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

        return CSTTranslation(code=cst.Call(func=func, args=args))


class SetKeyNode(DataFrameNode):
    def __init__(self, node: DataFrameNode, key: cst.CSTNode, *args, **kwargs):
        node.parent = self

        self.node = node
        self.key = key

        super().__init__(*args, **kwargs)

    def to_code(self) -> str:
        return f"({self.node.to_code()}).set_key({self.key})"

    def to_cst_translation(self) -> CSTTranslation:
        func = cst.Attribute(value=self.node.to_cst_statement(), attr="join")
        args = [cst.Arg(value=self.key)]

        return CSTTranslation(code=cst.Call(func=func, args=args))


class AggregationNode(DataFrameNode):
    @staticmethod
    def supported_aggregations():
        return ["max", "min", "sum", "avg"]

    def __init__(self, node: DataFrameNode, aggregation: str, *args, **kwargs):
        node.parent = self

        self.node = node
        if aggregation not in self.supported_aggregations():
            raise Exception("unsupported aggregation function was given")
        self.aggregation = aggregation

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        if self.node.sql_string:
            query = self.node.sql_string
            selected_columns = selected_columns_in_query(query)
            for column in selected_columns:
                query = query.replace(column, f"{self.aggregation.upper()}({column}) AS {self.aggregation}_{column}", 1)

            return query

    def to_code(self) -> str:
        if not self.node.sql_string:
            return f"({self.node.to_code()}).{self.aggregation}()"

        selected_columns = selected_columns_in_query(self.node.sql_string)
        if selected_columns == ["*"]:
            # we save results of pre_query in a temp variable. problematic if temp is already used
            variable_name = "temp"
            return (
                f'{variable_name} = pandas.read_sql("{self.node.sql_string} LIMIT 0", SOME CONN).columns'
                + "\n"
                + 'pandas.read_sql(f"'
                + self.node.sql_string.replace(
                    "*",
                    f"{{', '.join(['{self.aggregation.upper()}(' + c + ') AS {self.aggregation}_' + c for c in {variable_name}])}}",
                    1,
                )
                + '", SOME CONN)'
            )
        return f'read_sql("{self.sql_string}", SOME CONN)'

    def to_cst_translation(self) -> CSTTranslation:
        selected_columns = selected_columns_in_query(self.node.sql_string)
        precode = []
        sql_query = self.sql_string

        if selected_columns == ["*"]:
            variable_name = "temp"
            assign_target = cst.AssignTarget(target=cst.Name(value=variable_name))
            prequery = sql_query + " LIMIT 0"
            attribute = cst.Name(value="columns")
            call = cst.Call(
                func=cst.Name(value="read_sql"),
                args=[cst.Arg(value=str_code_to_cst('"' + prequery + '"'))],
            )
            precode = [cst.Assign(targets=(assign_target,), value=cst.Attribute(value=call, attr=attribute))]
            sql_query = self.node.sql_string.replace(
                "*",
                f"{{', '.join(['{self.aggregation.upper()}(' + c + ') AS {self.aggregation}_' + c for c in {variable_name}])}}",
                1,
            )

        code = cst.Call(func=cst.Name(value="read_sql"), args=[cst.Arg(value=str_code_to_cst('f"' + sql_query + '"'))])
        return CSTTranslation(code=code, precode=precode)


def selected_columns_in_query(query):
    lower_query = query.lower()
    return [column.strip() for column in (lower_query.split("select"))[1].split("from")[0].split(",")]
