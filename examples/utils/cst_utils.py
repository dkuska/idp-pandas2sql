from collections.abc import Sequence
from typing import Any

import libcst as cst


def get_Attribute_information(attribute: cst.Attribute) -> tuple:
    value = attribute.value
    if isinstance(value, cst.Attribute):
        value = get_Attribute_information(value)
    elif isinstance(value, cst.Name):
        value = get_Name_value(value)

    attr = get_Name_value(attribute.attr)

    return value, attr


def get_Arg_information(arg: cst.Arg) -> tuple:
    argument, keyword = "", ""
    arg_value = arg.value
    # Keyword is either a name or None
    if arg.keyword:
        arg_keyword = arg.keyword
        if isinstance(arg_keyword, cst.Name):
            keyword = get_Name_value(arg_keyword)

    # if isinstance(arg_value, cst.Arg):
    #     argument = arg_value.value
    if isinstance(arg_value, cst.SimpleString):
        argument = get_SimpleString_value(arg_value)
    elif isinstance(arg_value, cst.Name):
        argument = get_Name_value(arg_value)
    elif isinstance(arg_value, cst.Call):
        argument = recursive_analyze_Call(arg_value)

    return argument, keyword


def get_ImportAlias_information(import_alias: cst.ImportAlias) -> tuple:
    asname = ""
    if import_alias.asname:
        asname = import_alias.asname
        if isinstance(asname, cst.Name):
            asname = get_Name_value(asname)
        elif isinstance(asname, cst.Tuple):
            asname = get_Tuple_values(asname)
        elif isinstance(asname, cst.List):
            asname = get_List_values(asname)
        elif isinstance(asname, cst.AsName):
            asname = get_AsName_value(asname)

    return import_alias.name.value, asname


def get_AsName_value(asname: cst.AsName) -> str:
    asname = asname.name
    if isinstance(asname, cst.Name):
        asname = get_Name_value(asname)
    elif isinstance(asname, cst.Tuple):
        asname = get_Tuple_values(asname)
    elif isinstance(asname, cst.List):
        asname = get_List_values(asname)

    return asname


def get_List_values(l: cst.List) -> Sequence[Any]:
    # TODO
    pass


def get_Name_value(name: cst.Name) -> str:
    return name.value


def get_SimpleString_value(simple_string: cst.SimpleString) -> str:
    return simple_string.value


def get_Tuple_values(tuple: cst.Tuple) -> Sequence[str]:
    ret_values = []
    for element in tuple.elements:
        if isinstance(element.value, cst.Name):
            ret_values.append(get_Name_value(element.value))
        elif isinstance(element.value, cst.SimpleString):
            ret_values.append(get_SimpleString_value(element.value))
    return ret_values


def parse_targets(targets: Sequence[cst.BaseAssignTargetExpression]) -> Sequence[Any]:
    """Helper function for visit_Assign"""
    ret_targets = []
    for target in targets:
        target_target = target.target
        if isinstance(target_target, cst.Name):
            ret_targets.append(get_Name_value(target_target))
        elif isinstance(target_target, cst.Tuple):
            ret_targets.extend(get_Tuple_values(target_target))
    return ret_targets


def parse_values(value: cst.BaseExpression) -> Sequence[Any]:
    """Helper function for visit_Assign"""
    values = []
    if isinstance(value, cst.Call):
        values.append({"value": recursive_analyze_Call(value), "position": 0})
    elif isinstance(value, cst.SimpleString):
        values.append({"value": get_SimpleString_value(value), "position": 0})
    if isinstance(value, cst.Tuple):
        tuple_values = get_Tuple_values(value)
        for i, tuple_value in enumerate(tuple_values):
            values.append({"value": tuple_value, "position": i})
    return values


def recursive_analyze_Call(call: cst.Call):
    """
    recursively analyze the Call object and return a dict containing information about it.
    cst.Call consists of 2 main parts: func & args
    func is the calling variable (can also be another call in case of chained invocations )
    args is the list of arguments in the order in which they appear
    """
    # Parse first part of the call - caller/func
    caller, attribute = parse_func(call.func)
    # Parse second part - args
    arguments, keywords = parse_args(call.args)

    # DEBUG
    # print(f'lib: {lib}')
    # print(f'attribute: {attribute}')
    # print(f'arguments: {arguments}')
    # print(f'keywords: {keywords}')

    # TODO: Rethink the way this is structured....
    return_dict = {
        "caller": caller,  # Variable on which the function is called
        "attribute": attribute,  # Attribute/Function of the caller
        "args": arguments,  # For functions this includes positional arguments, should include order in the future probably
        "keyword_args": keywords,  # Keyword arguments with name of the keyword and value.
    }
    return return_dict


def parse_func(func: cst.BaseExpression) -> tuple:
    """Helper function for recursive_analyze_Call"""
    caller, attribute = "", ""
    if isinstance(func, cst.Attribute):
        caller, attribute = get_Attribute_information(func)
        # Func Value is a variable name
        if isinstance(caller, cst.Name):
            caller = get_Name_value(caller)
        # Func value itself is another call
        elif isinstance(caller, cst.Call):
            caller = recursive_analyze_Call(caller)  # Recursive call
        else:
            pass  # TODO:
    else:
        pass  # TODO:

    return caller, attribute


def parse_args(args: Sequence[cst.Arg]) -> tuple:
    """Helper function for recursive_analyze_Call"""
    arguments, keywords = [], []
    for arg in args:
        argument, keyword = get_Arg_information(arg)

        if keyword == "":
            arguments.append(argument)
        else:
            keywords.append({"keyword": keyword, "argument": argument})

    return arguments, keywords
