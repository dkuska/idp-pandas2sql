from dataclasses import dataclass
from typing import Any

@dataclass
class Assignment():
    var_name: str
    value: dict[str, Any]
    
    pandas: bool = False
