from abc import ABC


class IRNode(ABC):
    def __init__(self, parent=None):
        self.parent = parent


class DataFrameNode(IRNode):
    pass


class SQLNode(DataFrameNode):
    def __init__(self, sql_query: str = None, con=None, **kwargs):
        self.sql_query = sql_query
        self.con = con

        super().__init__(**kwargs)


class JoinNode(DataFrameNode):
    def __init__(self, left: DataFrameNode = None, right: DataFrameNode = None, **kwargs):
        self.left = left
        self.right = right

        super().__init__(**kwargs)
