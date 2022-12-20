from abc import ABC
from typing import Optional, Union

import libcst as cst


class Node(ABC):
    origin: cst.CSTNode

    def __init__(self, origin: cst.CSTNode):
        self.origin = origin


class DataFrameNode(Node):
    targets: Optional[list] = None
    values: Optional[Union[dict, list]] = None
    sql_based: bool = False
    index: Optional[str] = None

    def __init__(self, origin, targets, values):
        super().__init__(origin)
        self.targets = targets
        self.values = values

class SQLNode(DataFrameNode):
    sql_str: Optional[str] = None
    con: Optional[str] = None
    index: Optional[str] = None

    def __init__(self, origin, targets, values):
        super().__init__(origin=origin, targets=targets, values=values)
        self.sql_based = True
        self.sql_str = self.extract_sql_str(origin)
        self.con = self.extract_con(origin)
        self.index = self.extract_index(origin)

        # DEBUG
        # print(self.sql_str)
        # print(self.con)

    def extract_sql_str(self, origin: cst.CSTNode) -> str:
        args = self.values['args']
        # Iterate over Arguments to check if it was called as keyword parameter
        for arg in args:
            if isinstance(arg, tuple):
                keyword_name, keyword_value = arg        
                if keyword_name == 'sql':
                    return keyword_value
        # If this is not the case, return positional argument         
        return args[0]

    def extract_con(self, origin: cst.CSTNode) -> str:
        args = self.values['args']
        # Iterate over Arguments to check if it was called as keyword parameter
        for arg in args:
            if isinstance(arg, tuple):
                keyword_name, keyword_value = arg        
                if keyword_name == 'con':
                    return keyword_value
        # If this is not the case, return positional argument  
        return args[1]

    def extract_index(self, origin: cst.CSTNode) -> str:
        return ""  # TODO: Implement by traversing origin


class JoinNode(DataFrameNode):
    # parents: Optional[list[cst.CSTNode]] = None  # TODO: Figure out what this could be used for...
    left: Optional[SQLNode] = None
    right: Optional[SQLNode] = None
    on: Optional[tuple[str]] = None
    how: Optional[str] = ""
    lsuffix: Optional[str] = ""
    rsuffix: Optional[str] = ""
    sort: Optional[bool] = False
    validate: Optional[str] = ""

    def __init__(self, origin, targets, values):
        super().__init__(origin=origin, targets=targets, values=values)
        self.sql_based = True

        self.left, self.right = self.extract_join_partners(origin)
        self.on = self.extract_on(origin)
        self.how = self.extract_how(origin)
        self.lsuffix, self.rsuffix = self.extract_suffix(origin)
        self.sort = self.extract_sort(origin)
        self.validate = self.extract_validate(origin)

    def extract_join_partners(self, origin: cst.CSTNode) -> tuple[cst.CSTNode, cst.CSTNode]:
        return (
            None,
            None,
        )  # TODO: Implement by traversing origin, will also need additional information about all other nodes

    def extract_on(self, origin: cst.CSTNode) -> str:
        return ""  # TODO: Implement by traversing origin

    def extract_how(self, origin: cst.CSTNode) -> str:
        return ""  # TODO: Implement by traversing origin

    def extract_suffix(self, origin: cst.CSTNode) -> tuple[str, str]:
        return "", ""  # TODO: Implement by traversing origin

    def extract_sort(self, origin: cst.CSTNode) -> bool:
        return False  # TODO: Implement by traversing origin

    def extract_validate(self, origin: cst.CSTNode) -> str:
        return ""  # TODO: Implement by traversing origin

    def create_sql_query(self) -> str:
        return ""


class AggregationNode(DataFrameNode):
    parents: Optional[list[cst.CSTNode]] = None
    # TODO: Figure out what we need and how to access it

    def __init(self, origin, targets, values):
        super().__init__(origin=origin, targets=targets, values=values)
        self.sql_based = True
