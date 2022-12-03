import libcst as cst
from cst.cst_Transformer import Transformer
from cst.cst_Visitor import Visitor

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
    # Transform source into cst
    src_tree = cst.parse_module(src)

    # Create object that traverses CST and gathers information
    visitor = Visitor()

    # Parse every statement one by one
    for statement in src_tree.body:
        statement.visit(visitor)

    # Analyze imports for Pandas
    visitor.analyze_imports()
    # Analyze the variable assignements for DataFrames, read_sql, joins and aggregations
    visitor.analyze_assignments()
    # DEBUG
    visitor.print_summary()

    # TODO: Create IR and IR-Optimizer from visitor
    # TODO: Create transformer from IR-Optimizer

    # Create transformer with information from the visitor
    transformer = Transformer(visitor)
    # Modify the CST, Replace old nodes with new ones
    modified_tree = src_tree.visit(transformer)

    if not modified_tree.deep_equals(src_tree):
        ### Write modified_tree.code somewhere
        modified_code = modified_tree.code
        # TODO: Actually persist the modified code somewhere....


if __name__ == "__main__":
    main()
