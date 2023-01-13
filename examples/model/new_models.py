from abc import ABC

from libcst import CSTNode

# TODO: when translating forwards the args


class IRNode(ABC):
    def __init__(self, parent=None, library=None, *args, **kwargs):
        self.parent = parent
        self.library = library
        if args or kwargs:
            print(f"These args: {args} and kwargs: {list(kwargs.keys())} don't have a translation rule yet")


class DataFrameNode(IRNode):
    @property
    def sql_string(self):
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
        return f'read_sql("{self.sql_string}", {self.con})'


class JoinNode(DataFrameNode):
    def __init__(self, left: DataFrameNode, right: DataFrameNode, *args, **kwargs):
        left.parent = self
        right.parent = self

        self.left = left
        self.right = right

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self):
        if self.left.sql_string and self.right.sql_string:  # check if two connections are the same
            return f"'SELECT * FROM ({self.left.sql_string}) JOIN ({self.right.sql_string})')"

    def to_code(self):
        if self.sql_string:
            return f'read_sql("{self.sql_string}", SOME CONN)'  # get the con from children
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

    @property
    def sql_string(self):
        if self.node.sql_string:
            return f"{inject_aggregation(self.aggregation, self.node.sql_string)}"

    def to_code(self):
        if self.sql_string:
            return f'read_sql("{self.sql_string}", SOME CONN)'
        else:
            return f"({self.node.to_code()}).{self.aggregation}()"


# inject_aggregation("max", "SELECT a, b, c FROM d") will output
# SELECT MAX(a) AS max_a, MAX(b) AS max_b, MAX(c) AS max_c FROM d
def inject_aggregation(aggregation, query):
    lower_query = query.lower()
    selected_columns = [column.strip() for column in (lower_query.split("select"))[1].split("from")[0].split(",")]
    for column in selected_columns:
        query = query.replace(column, f"{aggregation.upper()}({column}) AS {aggregation}_{column}")
    return query
