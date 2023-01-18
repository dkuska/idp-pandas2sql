from abc import ABC

from libcst import CSTNode

# TODO:
# when translating forwards the args
# replace SOME CONN with the actual conn


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
            query = self.node.sql_string
            selected_columns = selected_columns_in_query(query)
            for column in selected_columns:
                query = query.replace(column, f"{self.aggregation.upper()}({column}) AS {self.aggregation}_{column}", 1)

            return query

    def to_code(self):
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


def selected_columns_in_query(query):
    lower_query = query.lower()
    return [column.strip() for column in (lower_query.split("select"))[1].split("from")[0].split(",")]
