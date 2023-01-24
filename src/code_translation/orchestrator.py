import libcst as cst

from .NodeReplacer import NodeReplacer
from .NodeSelector import NodeSelector

src = """
from pandas import read_sql
import pandas
con1 = DBConnection()

df1 = read_sql("SELECT * FROM table1", "something")



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

        # Create new tree with old_nodes_new_nodes
        node_replacer = NodeReplacer(node_selector)
        new_tree = src_tree.visit(node_replacer)

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
