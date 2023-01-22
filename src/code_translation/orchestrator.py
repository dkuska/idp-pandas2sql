import libcst as cst

from .ir.Optimizer import Optimizer
from .NodeReplacer import NodeReplacer
from .NodeSelector import NodeSelector

src = """
import numpy
import pandas as pd
from pandas import *
from pandas import read_sql

con1 = DBConnection()

df1 = read_sql("SELECT * FROM table1", con1)
df2 = pd.read_sql(sql="SELECT attr1, attr2 FROM table2", con=con1)

df3 = df1.join(df2, how='inner')
df4 = df1.set_index('key').join(df2.set_index('key'))

sum = df2.sum()
max = df1.max()

"""
# code for dask
"""
import dask.dataframe as dd

con1 = DBConnection()

dd1 = dd.read_sql_query("SELECT * FROM table1", con1)
dd2 = dd.read_sql_table("table2", con=con1)

dd3 = dd1.merge(dd2, how='inner')
"""


class Orchestrator:
    """
    This class manages the other parts of the processing.
    In the future this should open file, read content, optimize and write new content into another file.
    """

    def __init__(self):
        pass

    @staticmethod
    def transform(src: str) -> str:
        """
        One big function that does everything:
        1. create CST from source string
        2. Check if Pandas is imported - PandasImporter
        3. If it is, then select interesting nodes and create IR - PandasNodeSelector
            NOTE: At the moment this is where the IR is created, in the future, I'd like this to take place inside the Optimizer...
        4. Map old nodes to their replacement new_node - PandasOptimizer
            NOTE: This is where a lot of the logic should be moved to...
        5. Replace old nodes with their new nodes

        Args:
            src (str): string of source file contents

        Returns:
            new_src: string of new and optimized source file contents
        """
        # Transform into CST
        src_tree = cst.parse_module(src)

        # Create NodeSelector
        node_selector = NodeSelector()
        src_tree.visit(node_selector)

        # # nodes contain all visited statements in order
        # for variable, node in node_selector.variables.items():
        #     print(variable, type(node), end=" ")
        #     if isinstance(node, DataFrameNode):
        #         print(node.to_code())
        #     else:
        #         print()

        # Create Optimizer with information from NodeSelector
        optimizer = Optimizer(
            variables=node_selector.variables,
            interesting_nodes=node_selector.interesting_nodes,
            sql_access_methods=node_selector.get_sql_access_methods(),
        )
        optimizer.optimize()
        optimizer.map_old_to_new_nodes()
        old_nodes_new_nodes = optimizer.get_optimized_nodes()

        # Create new tree with old_nodes_new_nodes
        node_replacer = NodeReplacer()
        new_tree = node_replacer.replace(src_tree, old_nodes_new_nodes)

        # Export new_code
        new_src = new_tree.code

        return new_src


def main():
    print("Old Source:")
    print(src)
    orchestrator = Orchestrator()
    new_src = orchestrator.transform(src)
    print("New Source:")
    print(new_src)


if __name__ == "__main__":
    main()