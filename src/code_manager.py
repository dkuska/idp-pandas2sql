import inspect
from typing import Callable

NEW_FUNCTION_NAME = "new_function"


class CodeManager:
    code: str

    @classmethod
    def from_function(cls, function: Callable):
        manager = cls()
        funcion_name = function.__name__
        manager.code = inspect.getsource(function).replace(f"def {funcion_name}", f"def {NEW_FUNCTION_NAME}")
        return manager

    # * it is nice to work with files but working with functions is easier, especially when comparing results
    # @classmethod
    # def from_file(cls, path: str):
    #     inspector = cls()
    #     with open(path, "r") as input_file:
    #         inspector.code = input_file.read()
    #     return inspector

    # TODO
    @classmethod
    def from_ast(cls, ast):
        pass

    def execute_code(self):
        return exec(f"{self.code}{NEW_FUNCTION_NAME}()")

    # def write_to_file(self, path):
    #     pass
