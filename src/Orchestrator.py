import libcst as cst

from cst.NodeReplacer import NodeReplacer
from cst.PandasImporter import PandasImporter
from cst.PandasNodeSelector import PandasNodeSelector
from cst.PandasOptimizer import PandasOptimizer

src = """
import numpy
import pandas as pd
from pandas import *
from pandas import read_sql

con1 = blub()

df1 = read_sql("SELECT * FROM table1", con1)
df2 = pd.read_sql(sql="SELECT * FROM table2", con=con1)

df3 = df1.join(df2, how='inner')
df4 = df1.set_index('key').join(df2.set_index('key'))

"""


class Orchestrator:
    """
    This class manages the other parts of the processing.
    In the future this should open file, read content, optimize and write new content into another file.
    """

    def __init__(self):
        pass

    def transform(self, src: str) -> str:
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
        # Check with PandasImporter
        pandas_importer = PandasImporter()
        src_tree.visit(pandas_importer)

        # Create NodeSelector with information from PandasImporter
        if pandas_importer.pandas_imported:
            pandas_node_selector = PandasNodeSelector(
                pandas_star_imported=pandas_importer.pandas_star_imported,
                pandas_aliases=pandas_importer.pandas_aliases,
                imported_pandas_aliases=pandas_importer.imported_pandas_aliases,
            )
            src_tree.visit(pandas_node_selector)

            # Create PandasOptimizer with information from NodeSelector
            pandas_optimizer = PandasOptimizer(
                variables=pandas_node_selector.variables, interesting_nodes=pandas_node_selector.interesting_nodes
            )
            pandas_optimizer.optimize()
            pandas_optimizer.map_old_to_new_nodes()
            old_nodes_new_nodes = pandas_optimizer.get_optimized_nodes()

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
