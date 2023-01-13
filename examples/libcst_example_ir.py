import libcst as cst
from cst.cst_NodeSelector import NodeSelector
from model.new_models import DataFrameNode

src = """
import numpy
import pandas as pd
from pandas import *
from pandas import read_sql

con1 = blub()

df1 = read_sql("SELECT * FROM table1", con1)
df2 = pd.read_sql(sql="SELECT key1, key2 FROM table2", con=con1)

df3 = df1.join(df2, how='inner')
df4 = df1.set_index('key').join(df2.set_index('key'))

sum = df2.sum()
max = df1.max()


"""


def main():
    # Transform source into cst
    src_tree = cst.parse_module(src)

    node_selector = NodeSelector()

    src_tree.visit(node_selector)

    # nodes contain all visited statements in order
    for variable, node in node_selector.variables.items():
        print(variable, node.__class__.__name__, end=" ")
        if isinstance(node, DataFrameNode):
            print(node.to_code())
        else:
            print()


if __name__ == "__main__":
    main()
