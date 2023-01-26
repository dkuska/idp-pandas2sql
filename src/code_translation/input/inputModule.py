from typing import Optional

from ...exceptions import LibMethodUnresolved, LibMethodWithoutHandler
from ..ir.nodes import IRNode


class InputModule:
    @property
    def module_name(self) -> str:
        return ""

    @property
    def all_symbol_names(self) -> list[str]:
        """Return every symbol that is imported when importing * from the library"""
        return []

    @property
    def sql_access_method(self) -> Optional[str]:
        pass

    def resolve_call(self, method_name: str, is_df: bool, *args, **kwargs) -> IRNode:
        visitor_method_name = f"visit_{'df_' if is_df else ''}{method_name}"

        if not hasattr(self, visitor_method_name):
            raise LibMethodWithoutHandler(self.module_name, is_df, method_name)

        visitor_method = getattr(self, visitor_method_name)
        result = visitor_method(*args, **kwargs)
        if not result:
            raise LibMethodUnresolved(self.module_name, is_df, method_name)
        if not result.library:
            result.library = self.module_name
        return result
