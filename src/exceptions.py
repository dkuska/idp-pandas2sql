class NoResolveMethod(Exception):
    def __init__(self, cstNodeType: str) -> None:
        super().__init__(f'CSTNode of type "{cstNodeType}" has no method for resolving.')


class UnresolvableCSTNode(Exception):
    def __init__(self, cstNodeType: str) -> None:
        super().__init__(f'CSTNode of type "{cstNodeType}" failed to resolve.')


class LibMethodWithoutHandler(Exception):
    def __init__(self, lib_name: str, df: bool, method_name: str):
        message = f'Method of library "{lib_name}" has no handler for calls of "{method_name}"'
        if df:
            message += " on df"
        message += "."
        super().__init__(message)


class LibMethodUnresolved(Exception):
    def __init__(self, lib_name: str, df: bool, method_name: str):
        message = f'Method of library "{lib_name}" for calls of "{method_name}"'
        if df:
            message += " on df"
        message += "was not resolved by the InputModule."
        super().__init__(message)
