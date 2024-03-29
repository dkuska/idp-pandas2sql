import ast
from abc import ABC, abstractmethod
from typing import NamedTuple, Optional

import libcst as cst

# TODO:
# when translating forwards the args


def str_code_to_cst(code: str) -> cst.CSTNode:
    return cst.parse_expression(code)


def evaluate_cst(node: cst.CSTNode) -> any:
    return ast.literal_eval(cst.Module(body=[node]).code)


class CSTTranslation(NamedTuple):
    code: cst.CSTNode
    precode: list[cst.CSTNode] = []
    postcode: list[cst.CSTNode] = []


class IRNode(ABC):
    parent: Optional["IRNode"]
    library: Optional[str]

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

    @abstractmethod
    def to_cst_translation(self, sql_access_method) -> CSTTranslation:
        pass

    @property
    def con(self):
        return self.node.con


class SQLNode(DataFrameNode):
    def __init__(self, sql: str, con: cst.CSTNode, *args, **kwargs):
        self.sql = sql
        self._con = con

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        return self.sql

    @property
    def con(self) -> cst.CSTNode:
        return self._con

    def to_cst_translation(self, sql_access_method) -> CSTTranslation:
        func = sql_access_method
        args = [
            cst.Arg(value=cst.SimpleString(value='"' + self.sql_string + '"')),
            cst.Arg(value=self.con),
        ]

        return CSTTranslation(code=cst.Call(func=func, args=args))


class SortNode(DataFrameNode):
    def __init__(
        self,
        node: DataFrameNode,
        by: Optional[str] = None,
        ascending: bool = True,
        *args,
        **kwargs,
    ):
        node.parent = self
        self.node = node
        if isinstance(by, cst.CSTNode):
            by = evaluate_cst(by)
        if isinstance(by, str):
            by = [by]
        self.by = by
        if isinstance(ascending, cst.CSTNode):
            ascending = evaluate_cst(ascending)
        self.ascending = ascending

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> Optional[str]:
        if self.node.sql_string:
            if self.by:
                return f"{self.node.sql_string} ORDER BY {', '.join(self.by)} {'ASC' if self.ascending else 'DESC'}"

            selected_columns = selected_columns_in_query(self.node.sql_string)
            if selected_columns != ["*"]:
                return f"{self.node.sql_string} ORDER BY {', '.join(selected_columns)} {'ASC' if self.ascending else 'DESC'}"

    def to_cst_translation(self, sql_access_method) -> CSTTranslation:
        selected_columns = selected_columns_in_query(self.node.sql_string)
        if not self.sql_string and selected_columns == ["*"]:
            variable_name = "temp"
            assign_target = cst.AssignTarget(target=cst.Name(value=variable_name))
            attribute = cst.Name(value="columns")
            call = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst(f'"{self.node.sql_string} LIMIT 0"')), cst.Arg(value=self.con)],
            )
            precode = [cst.Assign(targets=(assign_target,), value=cst.Attribute(value=call, attr=attribute))]
            sql_query = self.node.sql_string + f" ORDER BY {{', '.join({variable_name})}} "
            sql_query += "ASC" if self.ascending else "DESC"

            code = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst('f"' + sql_query + '"')), cst.Arg(value=self.con)],
            )
        else:
            precode = []
            code = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst('"' + self.sql_string + '"')), cst.Arg(value=self.con)],
            )

        return CSTTranslation(code=code, precode=precode)


class JoinNode(DataFrameNode):
    def __init__(
        self,
        left: DataFrameNode,
        right: DataFrameNode,
        how: Optional[str] = None,
        on: Optional[str] = None,
        *args,
        **kwargs,
    ):
        left.parent = self
        right.parent = self

        self.left = left
        self.right = right
        self.how = how
        self.on = on

        super().__init__(*args, **kwargs)

    @property
    def con(self) -> cst.CSTNode:
        left_con = self.left.con
        right_con = self.right.con
        if left_con.value != right_con.value:
            raise Exception("Join partners from different sources")
        else:
            return left_con

    @property
    def node(self):
        return self.left

    @property
    def sql_string(self) -> Optional[str]:
        join_operator = "JOIN"
        if self.how:
            join_operator = f"{self.how.upper()} {join_operator}"

        # Extract query and additional information from left node
        left_set_key = False
        if isinstance(self.left, SQLNode):
            left_sql = self.left.sql_string
        elif isinstance(self.left, JoinNode):
            left_sql = self.left.sql_string
        elif isinstance(self.left, AggregationNode):
            # This is where the dependency injection starts to get complicated
            # TODO: find out if there is a precode condition for the CSTTranslation
            left_cst_translation = self.left.to_cst_translation(sql_access_method="")  #
            if left_cst_translation.precode != []:
                raise Exception("No support for prequeries in JoinNodes yet")  # TODO: Investigate this further...
            left_sql = self.left.sql_string
        elif isinstance(self.left, SetKeyNode):
            left_set_key = True
            left_sql = self.left.node.sql_string
            left_key = self.left.key
        else:
            return None

        # Extract query and additional information from right node
        right_set_key = False
        if isinstance(self.right, SQLNode):
            right_sql = self.right.sql_string
        elif isinstance(self.right, JoinNode):
            right_sql = self.right.sql_string
        elif isinstance(self.right, AggregationNode):
            # Same as above with the left-hand side...
            right_cst_translation = self.right.to_cst_translation(sql_access_method="")
            if right_cst_translation.precode != []:
                raise Exception("No support for prequeries in JoinNodes yet")
            right_sql = self.right.sql_string
        elif isinstance(self.right, SetKeyNode):
            right_set_key = True
            right_sql = self.right.node.sql_string
            right_key = self.right.key  # TODO: Implement for more complex types
        else:
            return None

        # Build query string
        if left_set_key and right_set_key:
            # TODO: DataFrameNode needs key also aka 'index_col' in read_sql
            left_table_alias = "S1"
            right_table_alias = "S2"
            return f"SELECT * FROM ({left_sql}) AS {left_table_alias} {join_operator} ({right_sql}) AS {right_table_alias} ON {left_table_alias}.{left_key} = {right_table_alias}.{right_key}"
        elif self.on:
            left_table_alias = "S1"
            right_table_alias = "S2"
            return f"SELECT * FROM ({left_sql}) AS {left_table_alias} {join_operator} ({right_sql}) AS {right_table_alias} ON {left_table_alias}.{self.on} = {right_table_alias}.{self.on}"
        else:
            return f"SELECT * FROM ({left_sql}) {join_operator} ({right_sql})"

    def to_cst_translation(self, sql_access_method) -> CSTTranslation:
        query_str = '"' + self.sql_string + '"'

        # Build cst.Assign Object
        func = sql_access_method
        # Assume both left and right have the same con
        args = [cst.Arg(value=cst.SimpleString(value=query_str)), cst.Arg(value=self.con)]

        return CSTTranslation(code=cst.Call(func=func, args=args))


class SetKeyNode(DataFrameNode):
    def __init__(self, node: DataFrameNode, key: cst.CSTNode, *args, **kwargs):
        node.parent = self

        self.node = node
        self.key = key

        super().__init__(*args, **kwargs)

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
            raise Exception(f"unsupported aggregation function was given: {aggregation}")
        self.aggregation = aggregation

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> Optional[str]:
        if self.node.sql_string:
            query = self.node.sql_string
            selected_columns = selected_columns_in_query(query)
            for column in selected_columns:
                query = query.replace(column, f"{self.aggregation.upper()}({column}) AS {self.aggregation}_{column}", 1)

            return query

    def to_cst_translation(self, sql_access_method) -> CSTTranslation:
        selected_columns = selected_columns_in_query(self.node.sql_string)
        precode = []
        sql_query = self.sql_string

        if selected_columns == ["*"]:
            variable_name = "temp"
            assign_target = cst.AssignTarget(target=cst.Name(value=variable_name))
            attribute = cst.Name(value="columns")
            call = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst(f'"{self.node.sql_string} LIMIT 0"')), cst.Arg(value=self.con)],
            )
            precode = [cst.Assign(targets=(assign_target,), value=cst.Attribute(value=call, attr=attribute))]
            sql_query = self.node.sql_string.replace(
                "*",
                f"{{', '.join(['{self.aggregation.upper()}(' + c + ') AS {self.aggregation}_' + c for c in {variable_name}])}}",
                1,
            )

            code = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst('f"' + sql_query + '"')), cst.Arg(value=self.con)],
            )

        else:
            code = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst('"' + sql_query + '"')), cst.Arg(value=self.con)],
            )

        return CSTTranslation(code=code, precode=precode)


def selected_columns_in_query(query):
    lower_query = query.lower()
    return [column.strip() for column in (lower_query.split("select"))[1].split("from")[0].split(",")]
