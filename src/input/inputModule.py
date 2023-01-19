from typing import Optional

from model.nodes import IRNode


class InputModule:
    @property
    def module_name(self) -> str:
        pass

    @property
    def all_symbol_names(self) -> list[str]:
        """Return every symbol that is imported when importing * from the library"""
        return []

    def visit_method(self, func_name: str, args: list, kwargs: dict) -> Optional[IRNode]:
        visitor_method_name = f"visit_{func_name}"

        if not hasattr(self, visitor_method_name):
            print(f'Warning: Call of method "{func_name}" of library "{self.module_name}" has no handler.')
            return None

        visitor_method = getattr(self, visitor_method_name)
        result = visitor_method(*args, **kwargs)
        if not result:
            print(f'Warning: Call of method "{func_name}" of library "{self.module_name}" returns no IR.')
            return None
        if not result.library:
            result.library = self.module_name
        return result

    def visit_df_method(self, ir_node: IRNode, func_name: str, args: list, kwargs: dict) -> Optional[IRNode]:
        visitor_method_name = f"visit_df_{func_name}"

        if not hasattr(self, visitor_method_name):
            print(f'Warning: Call of method "{func_name}" on dataframe of library "{self.module_name}" has no handler.')
            return None

        visitor_method = getattr(self, visitor_method_name)
        result = visitor_method(ir_node, *args, **kwargs)
        if not result:
            print(f'Warning: Call of method "{func_name}" on dataframe of library "{self.module_name}" returns no IR.')
            return None
        if not result.library:
            result.library = self.module_name
        return result
