from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Literal, NamedTuple, Optional

import libcst as cst

# TODO:
# when translating forwards the args


def str_code_to_cst(code: str) -> cst.BaseExpression:
    return cst.parse_expression(code)


@dataclass
class TempVar:
    var_name: str
    sql: str

    def to_cst_node(self, sql_access_method: cst.BaseExpression, con: cst.BaseExpression):
        statement = cst.Assign(
            targets=(cst.AssignTarget(target=cst.Name(value=self.var_name)),),
            value=cst.Attribute(
                value=cst.Call(
                    func=sql_access_method,
                    args=[
                        cst.Arg(value=str_code_to_cst(f'"{self.sql} LIMIT 0"')),
                        cst.Arg(value=con),
                    ],
                ),
                attr=cst.Name(value="columns"),
            ),
        )
        return statement


class CSTTranslation(NamedTuple):
    code: cst.CSTNode
    precode: list[cst.CSTNode] = []
    postcode: list[cst.CSTNode] = []


class IRNode(ABC):
    parent: Optional["IRNode"]
    library: str | None

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
    @abstractmethod
    def sql_string(self) -> str:
        pass

    @property
    @abstractmethod
    def tempVars(self) -> list[TempVar]:
        pass

    @property
    @abstractmethod
    def columns(self) -> list[str] | TempVar:
        pass

    @property
    @abstractmethod
    def con(self) -> cst.Name:
        pass

    def to_cst_translation(self, sql_access_method) -> CSTTranslation:
        if self.tempVars:
            precode = [tempvar.to_cst_node(sql_access_method, self.con) for tempvar in self.tempVars]
            code = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst('f"' + self.sql_string + '"')), cst.Arg(value=self.con)],
            )
        else:
            precode = []
            code = cst.Call(
                func=sql_access_method,
                args=[cst.Arg(value=str_code_to_cst('"' + self.sql_string + '"')), cst.Arg(value=self.con)],
            )

        return CSTTranslation(code=code, precode=precode)

    def tempVar_for_query_cols(self, var_name: str):
        return TempVar(var_name=var_name, sql=self.sql_string)


class SQLNode(DataFrameNode):
    def __init__(self, sql: str, con: cst.Name, *args, **kwargs):
        self.sql = sql
        self._con = con

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        return self.sql

    @property
    def tempVars(self) -> list[TempVar]:
        return []

    @property
    def columns(self) -> list[str] | TempVar:
        selected_columns = selected_columns_in_query(self.sql_string)
        if selected_columns != ["*"]:
            return selected_columns
        return self.tempVar_for_query_cols("temp")

    @property
    def con(self) -> cst.Name:
        return self._con


class SortNode(DataFrameNode):
    def __init__(
        self,
        node: DataFrameNode,
        by: list[str],
        ascending: bool = True,
        *args,
        **kwargs,
    ):
        node.parent = self
        self.node = node
        if by == ["*"] and isinstance(self.node.columns, list):
            self.by = self.node.columns
        else:
            self.by = by
        self.ascending = ascending

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        if self.by == ["*"]:
            cols = self.node.columns
            assert isinstance(cols, TempVar)  # safe to say because of __init__
            return (
                f"{self.node.sql_string} ORDER BY {{', '.join({cols.var_name})}} {'ASC' if self.ascending else 'DESC'}"
            )
        return f"{self.node.sql_string} ORDER BY {', '.join(self.by)} {'ASC' if self.ascending else 'DESC'}"

    @property
    def tempVars(self) -> list[TempVar]:
        tempVars = self.node.tempVars
        if self.by == ["*"]:
            cols = self.node.columns
            if isinstance(cols, TempVar) and cols not in tempVars:
                tempVars.append(cols)
        return tempVars

    @property
    def columns(self) -> list[str] | TempVar:
        return self.node.columns

    @property
    def con(self) -> cst.Name:
        return self.node.con


class JoinNode(DataFrameNode):
    def __init__(
        self,
        left: DataFrameNode,
        right: DataFrameNode,
        how: str | None = None,
        left_on: list[str] | Literal["key", "natural"] = "key",
        right_on: list[str] | Literal["key", "natural"] = "key",
        *args,
        **kwargs,
    ):
        left.parent = self
        right.parent = self

        self.left = left
        self.right = right
        self.how = how
        self.left_on = left_on
        self.right_on = right_on

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
    def columns(self) -> list[str] | TempVar:
        leftcols = self.left.columns
        rightcols = self.right.columns
        if isinstance(leftcols, list) and isinstance(rightcols, list):
            return list(set(leftcols + rightcols))
        return self.tempVar_for_query_cols("temp")

    @property
    def sql_string(self) -> str | None:
        join_operator = "JOIN"
        if self.how:
            join_operator = f"{self.how.upper()} {join_operator}"

        # Extract query and additional information from left node

        left_sql = self.left.sql_string
        left_on: list[str]
        if self.left_on == "key":
            assert isinstance(self.left, SetKeyNode)  # TODO: Don't do that
            left_on = self.left.key
        else:
            assert isinstance(self.left_on, list)  # this is fine
            left_on = self.left_on

        # Extract query and additional information from right node
        right_sql = self.right.sql_string
        right_on: list[str]
        if self.right_on == "key":
            assert isinstance(self.right, SetKeyNode)  # TODO: Don't do that
            right_on = self.right.key
        else:
            assert isinstance(self.right_on, list)  # this is fine
            right_on = self.right_on

        # Build query string
        # TODO: DataFrameNode needs key also aka 'index_col' in read_sql
        left_table_alias = "S1"
        right_table_alias = "S2"
        return f"SELECT * FROM ({left_sql}) AS {left_table_alias} {join_operator} ({right_sql}) AS {right_table_alias} ON {' AND '.join(f'{left_table_alias}.{left} = {right_table_alias}.{right}' for (left, right) in zip(left_on, right_on))}"

    @property
    def tempVars(self) -> list[TempVar]:
        return list(set(self.left.tempVars + self.right.tempVars))


class SetKeyNode(DataFrameNode):
    def __init__(self, node: DataFrameNode, key: list[str], *args, **kwargs):
        node.parent = self

        self.node = node
        self.key = key

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self) -> str:
        return self.node.sql_string

    @property
    def tempVars(self) -> list[TempVar]:
        return self.node.tempVars

    @property
    def columns(self) -> list[str] | TempVar:
        return self.node.columns

    @property
    def con(self) -> cst.Name:
        return self.node.con


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
    def sql_string(self) -> str | None:
        cols = self.node.columns
        from_where = self.node.sql_string[self.node.sql_string.find("FROM") :]
        if isinstance(cols, TempVar):
            return f"SELECT {{', '.join(f'{self.aggregation.upper()}({{c}}) AS {self.aggregation}_{{c}}' for c in {cols.var_name})}} {from_where}"
        else:
            return f"SELECT {', '.join(f'{self.aggregation.upper()}({c}) AS {self.aggregation}_{c}' for c in cols)} {from_where}"

    @property
    def tempVars(self) -> list[TempVar]:
        tempVars = self.node.tempVars
        cols = self.node.columns
        if isinstance(cols, TempVar) and cols not in tempVars:
            tempVars.append(cols)
        return tempVars

    @property
    def columns(self) -> list[str] | TempVar:
        return self.tempVar_for_query_cols("temp")

    @property
    def con(self) -> cst.Name:
        return self.node.con


def selected_columns_in_query(query: str):
    lower_query = query.lower()
    return [column.strip() for column in (lower_query.split("select"))[1].split("from")[0].split(",")]
