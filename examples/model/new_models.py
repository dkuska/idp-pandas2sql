from abc import ABC

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
        return self.sql.value.replace('"', "")

    def to_code(self):
        return f"read_sql({self.sql_string}, SOME CON)"


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


class SetKeyNode(DataFrameNode):
    def __init__(self, node: DataFrameNode, key: CSTNode, *args, **kwargs):
        node.parent = self

        self.node = node
        self.key = key

        super().__init__(*args, **kwargs)

    def to_code(self):
        return f"({self.node.to_code()}).set_key({self.key.value})"


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

    def to_code(self):
        return f'{self.aggregation.upper()}({self.node.to_code()})["{self.aggregation()}"]'
