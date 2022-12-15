from abc import ABC
from dataclasses import dataclass
from typing import Optional

import libcst as cst


@dataclass
class Node(ABC):
    origin: cst.CSTNode


@dataclass
class PandasNode(Node):
    # TODO: Figure out what information we need to save
    pass


@dataclass
class DataFrameNode(PandasNode):
    sql_based: bool = False
    index: Optional[str] = None


@dataclass
class SQLNode(PandasNode):
    sql_str: Optional[str] = None
    con: Optional[str] = None
    index: Optional[str] = None

    def __init__(self, origin: cst.CSTNode):
        self.origin = origin

        self.sql_str = self.extract_sql_str(origin)
        self.con = self.extract_con(origin)
        self.index = self.extract_index(origin)

    def extract_sql_str(self, origin: cst.CSTNode) -> str:
        return ""  # TODO: Implement by traversing origin

    def extract_con(self, origin: cst.CSTNode) -> str:
        return "" # TODO: Implement by traversing origin

    def extract_index(self, origin: cst.CSTNode) -> str:
        return "" # TODO: Implement by traversing origin


@dataclass
class JoinNode(PandasNode):
    parents: Optional[list[cst.CSTNode]] = None #TODO: Figure out what this could be used for...
    left: Optional[SQLNode] = None
    right: Optional[SQLNode] = None
    on: Optional[tuple[str]] = None
    how: Optional[str] = ""
    lsuffix: Optional[str] = ""
    rsuffix: Optional[str] = ""
    sort: Optional[bool] = False
    validate: Optional[str] = ""

    def __init__(self, origin, parents = None):
        self.origin = origin
        self.parents = parents
        self.left, self.right = self.extract_join_partners(origin)
        self.on = self.extract_on(origin)
        self.how = self.extract_how(origin)
        self.lsuffix, self.rsuffix = self.extract_suffix(origin)
        self.sort = self.extract_sort(origin)
        self.validate = self.extract_validate(origin)

    def extract_join_partners(self, origin: cst.CSTNode) -> tuple[cst.CSTNode, cst.CSTNode]:
        pass # TODO: Implement by traversing origin, will also need additional information about all other nodes

    def extract_on(self, origin: cst.CSTNode) -> str:
        pass # TODO: Implement by traversing origin

    def extract_how(self, origin: cst.CSTNode) -> str:
        pass # TODO: Implement by traversing origin

    def extract_suffix(self, origin: cst.CSTNode) -> tuple[str, str]:
        pass # TODO: Implement by traversing origin

    def extract_sort(self, origin: cst.CSTNode) -> bool:
        pass # TODO: Implement by traversing origin

    def extract_validate(self, origin: cst.CSTNode) -> str:
        pass # TODO: Implement by traversing origin


    def create_sql_query(self) -> str:
        return ''

@dataclass
class AggregationNode(PandasNode):
    parents: Optional[list[cst.CSTNode]] = None
