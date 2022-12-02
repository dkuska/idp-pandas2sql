from dataclasses import dataclass
from typing import Any

@dataclass
class Import():
    lib_name: str
    alias: str

@dataclass
class ImportFrom():
    lib_name: str
    imports: list[str]
