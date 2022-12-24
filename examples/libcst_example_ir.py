import libcst as cst
from cst.cst_NodeSelector import NodeSelector

src = """
import numpy
import pandas as pd
from pandas import *
from pandas import read_sql

con1 = blub(hello())

df1 = read_sql("SELECT * FROM table1", con1)
df2 = pd.read_sql(sql="SELECT * FROM table2", con=con1)

df3 = df1.join(df2, how='inner')

df1.set_index('key', inplace=True)
df3 = df1.set_index('key').join(df2.set_index('key'))

([1] * 2).append(2)
a5.append(1)
append(1)

a1 = 1
a2 = 1.2
a3 = "hi"
a4 = True
a5 = [1, 2, 3]

"""


def main():
    # Transform source into cst
    src_tree = cst.parse_module(src)

    node_selector = NodeSelector()

    src_tree.visit(node_selector)

    # nodes contain all visited statements in order
    for variable, node in node_selector.variables.items():
        print(variable, type(node))


if __name__ == "__main__":
    main()
