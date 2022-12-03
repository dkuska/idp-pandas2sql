from typing import Any, Sequence

import libcst as cst


def get_Tuple_values(tuple: cst.Tuple) -> Sequence[str]:
    ret_values = []
    for element in tuple.elements:
        if isinstance(element.value, cst.Name):
            ret_values.append(get_Name_value(element.value))
        elif isinstance(element.value, cst.SimpleString):
            ret_values.append(get_SimpleString_value(element.value))
    return ret_values


def get_Name_value(name: cst.Name) -> str:
    return name.value


def get_SimpleString_value(simple_string: cst.SimpleString) -> str:
    return simple_string.value


def get_List_values(l: cst.List) -> Sequence[Any]:
    # TODO
    pass


def get_ImportAlias_information(import_alias: cst.ImportAlias) -> list[str]:
    asname = ""
    if import_alias.asname:
        asname = import_alias.asname
        if isinstance(asname, cst.Name):
            asname = get_Name_value(asname)
        elif isinstance(asname, cst.Tuple):
            asname = get_Tuple_values(asname)
        elif isinstance(asname, cst.List):
            asname = get_List_values(asname)
    return [import_alias.name.value, asname]


def get_Attribute_information(attribute: cst.Attribute) -> Any:
    value = attribute.value
    if isinstance(value, cst.Attribute):
        value = get_Attribute_information(value)
    elif isinstance(value, cst.Name):
        value = get_Name_value(value)

    attr = get_Name_value(attribute.attr)

    return [value, attr]
