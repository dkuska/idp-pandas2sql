import libcst as cst
from cst.cst_Transformer import Transformer
from cst.cst_Visitor import Visitor
from libcst.tool import dump

src = """
import numpy
import pandas as pd
from pandas import read_sql

df1 = pd.read_sql("SELECT * FROM table1")
df2 = pd.read_sql("SELECT * FROM table2")

df3 = df1.join(df2, how='inner')

df3 = df1.set_index('key').join(df2.set_index('key'))

s,t = 'abc', 'def'

"""


def main():
    visitor = Visitor()

    for line in src.splitlines():
        line_tree = cst.parse_module(line)
        line_tree.visit(visitor)

    visitor.analyze_imports()
    visitor.analyze_assignments()
    visitor.print_summary()


if __name__ == "__main__":
    main()
