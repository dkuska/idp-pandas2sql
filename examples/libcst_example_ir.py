import libcst as cst
from cst.cst_NodeSelector import NodeSelector

src = """
import numpy
import pandas as pd
from pandas import read_sql

con1 = blub()

df1 = pd.read_sql("SELECT * FROM table1", con1)
df2 = pd.read_sql(sql="SELECT * FROM table2", con=con1)
df3 = df1.join(df2, how='inner')

df1.set_index('key', inplace=True)

df3 = df1.set_index('key').join(df2.set_index('key'))

s,t = 'abc', 'def'

"""


def main():
    # Transform source into cst
    src_tree = cst.parse_module(src)

    node_selector = NodeSelector()

    # Parse every statement one by one
    for statement in src_tree.body:
        statement.visit(node_selector)

    for node in node_selector.nodes:
        print(type(node))

    for target_name, node_list in node_selector.variables.items():
        print(target_name)
        print(node_list)


if __name__ == "__main__":
    main()
