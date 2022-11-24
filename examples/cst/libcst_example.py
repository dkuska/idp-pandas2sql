import libcst as cst
from libcst.tool import dump

from cst_Visitor import Visitor
from cst_Transformer import Transformer

src = """
import pandas as pd
from pandas import read_sql

df1 = pd.read_sql("SELECT * FROM table1")
df2 = pd.read_sql("SELECT * FROM table2")
df3 = df1.join(df2, how='inner')
"""

def main():
    src_tree = cst.parse_module(src)
    print(dump(src_tree))
            
    visitor = Visitor()
    src_tree.visit(visitor)
    visitor.report()

    transformer = Transformer(visitor)
    modified_tree = src_tree.visit(transformer)
    
    if not modified_tree.deep_equals(src_tree):
        ### Write modified_tree.code somewhere
        modified_code = modified_tree.code


if __name__ == "__main__":
    main()