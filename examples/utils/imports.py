from dataclasses import dataclass


@dataclass
class Import:
    lib_name: str
    alias: str


@dataclass
class ImportFrom:
    lib_name: str
    imports: list[str]
