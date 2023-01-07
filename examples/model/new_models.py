from abc import ABC

from libcst import CSTNode
import libcst as cst


class IRNode(ABC):
    def __init__(self, parent=None, *args, **kwargs):
        self.parent = parent
        if args or kwargs:
            print(f"These args: {args} and kwargs: {list(kwargs.keys())} don't have a translation rule yet")


class DataFrameNode(IRNode):
    pass


class SQLNode(DataFrameNode):
    def __init__(self, sql: CSTNode, con, *args, **kwargs):
        self.sql = sql
        self.con = con

        super().__init__(*args, **kwargs)

    @property
    def sql_string(self):
        return self.sql.value #.replace('"', "") #TODO Find out where this .replace is necessary

    def to_code(self):
        return f"read_sql({self.sql_string}, SOME CON)"
    
    def to_cst_node(self):
        if True: 
            func = cst.Name(value='read_sql')
        else: # TODO: Needs awareness of used alias
            func = cst.Attribute(value=cst.Name(value=self.pandas_alias), 
                                 attr=cst.Name(value='read_sql'))
        
        args = [cst.Arg(value=cst.SimpleString(value=self.sql_string))]
        
        call = cst.Call(func=func, args=args)
        
        targets = [cst.AssignTarget(target=cst.Name('dummy_df'))] # TODO: Needs awareness of assignment name
        assign = cst.Assign(targets=targets, value=call)
        return assign
        
    def to_cst_statement(self):     
        return cst.SimpleStatementLine(body=[self.to_cst_node()])

class JoinNode(DataFrameNode):
    def __init__(self, left: DataFrameNode, right: DataFrameNode, *args, **kwargs):
        left.parent = self
        right.parent = self

        self.left = left
        self.right = right

        super().__init__(*args, **kwargs)

    def to_code(self):
        if hasattr(self.left, "sql_string") and hasattr(self.right, "sql_string"):
            return f"read_sql('SELECT * FROM ({self.left.sql_string}) JOIN ({self.right.sql_string})')"
        else:
            return f"({self.left.to_code()}).join({self.right.to_code()})"

    def to_cst_node(self):
        if isinstance(self.left, SQLNode):
            left_sql = self.left.sql_string
            pass
        elif isinstance(self.left, SetKeyNode):
            pass # TODO
        else:
            pass
        
        if isinstance(self.left, SQLNode):
            right_sql = self.right.sql_string
            pass
        elif isinstance(self.left, SetKeyNode):
            pass # TODO
        else:
            pass
        
        query_str = f"SELECT * FROM ({left_sql}) JOIN ({right_sql})"
        query_str = "\"" + query_str + "\""
        print(query_str)
        
        if True: 
            func = cst.Name(value='read_sql')
        else: # TODO: Needs awareness of used alias
            func = cst.Attribute(value=cst.Name(value=self.pandas_alias), 
                                 attr=cst.Name(value='read_sql'))
        args = [cst.Arg(value=cst.SimpleString(value=query_str))]
        
        call = cst.Call(func=func, args=args)
        
        targets = [cst.AssignTarget(target=cst.Name('dummy_df'))] # TODO: Needs awareness of assignment name
        assign = cst.Assign(targets=targets, value=call)
        
        # left_cst = self.left.to_cst_node()
        # right_cst = self.right.to_cst_node()
        
        # func = cst.Attribute(value=left_cst, attr='join')
        # args = [cst.Arg(value=right_cst)]
        
        # call = cst.Call(func=func, args=args)
        
        # targets = [cst.AssignTarget(target=cst.Name('dummy_df'))] # TODO: Need to be made aware of target name
        # assign = cst.Assign(targets=targets, value=call)
        return assign
    
    def to_cst_statement(self):
        return cst.SimpleStatementLine(body=[self.to_cst_node()])

class SetKeyNode(DataFrameNode):
    def __init__(self, node: DataFrameNode, key: CSTNode, *args, **kwargs):
        node.parent = self

        self.node = node
        self.key = key

        super().__init__(*args, **kwargs)

    def to_code(self):
        return f"({self.node.to_code()}).set_key({self.key.value})"
    
    def to_cst_node(self):
        func = cst.Attribute(value=self.node.to_cst_statement(), attr='join')
        args = [cst.Arg(value=self.key)]
        
        call = cst.Call(func=func, args=args)
        
        targets = [cst.AssignTarget(target=cst.Name('dummy_df'))]
        assign = cst.Assign(targets=targets, value=call)
        
        return assign
        
    def to_cst_statement(self):
        return cst.SimpleStatementLine(body=[self.to_cst_node()])