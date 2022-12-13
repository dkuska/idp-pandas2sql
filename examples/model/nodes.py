from abc import ABC
from dataclasses import dataclass
import libcst as cst
from typing import Union, Any, Optional

@dataclass
class Node(ABC):
    origin: cst.CSTNode

@dataclass
class PandasNode(Node):
    pass

@dataclass
class SQLNode(PandasNode):
    sql_str: Optional[str] = None


@dataclass
class JoinNode(PandasNode):
    parents: Optional[list[cst.CSTNode]] = None

@dataclass
class AggregationNode(PandasNode):
    parents: Optional[list[cst.CSTNode]] = None
