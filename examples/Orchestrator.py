import libcst as cst

# from cst.NodeReplacer import NodeReplacer
from cst.PandasImporter import PandasImporter
from cst.PandasNodeSelector import PandasNodeSelector
# from cst.PandasOptimizer import PandasOptimizer
from model.new_models import DataFrameNode

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


class Orchestrator():
    
    def __init__(self):
        pass
        # self.pandas_importer = PandasImporter()
        # self.pandas_node_selector = PandasNodeSelector()
        # self.pandas_optimizer = PandasOptimizer()
        # self.node_replacer = NodeReplacer()
        
        
    def transform(self, src: str) -> str:
        # Transform into CST
        src_tree = cst.parse_module(src)
        # Check with PandasImporter
        pandas_importer = PandasImporter()
        src_tree.visit(pandas_importer)
        
        print(pandas_importer.pandas_imported)
        
        # Create NodeSelector with information from PandasImporter
        if pandas_importer.pandas_imported:
            pandas_node_selector = PandasNodeSelector(pandas_star_imported = pandas_importer.pandas_star_imported,
                                               pandas_aliases = pandas_importer.pandas_aliases,
                                               imported_pandas_aliases = pandas_importer.imported_pandas_aliases)
            
            src_tree.visit(pandas_node_selector)
            
            # DEBUG
            # nodes contain all visited statements in order
            for variable, node in pandas_node_selector.variables.items():
                print(variable, type(node), end=" ")
                if isinstance(node, DataFrameNode):
                    cst_statement = node.to_cst_statement(variable)
                    # print(type(cst_statement))
                    # print(cst_statement)
                    module = cst.Module(body=[cst_statement])
                    print(module.code)
                else:
                    print()
            
            
            # # Create PandasOptimizer with information from NodeSelector
            # pandas_optimizer = PandasOptimizer(pandas_node_selector.variables)
            # pandas_optimizer.optimize()
            # old_nodes_new_nodes = pandas_optimizer.get_optimized_nodes()
            
            # # Create new tree with old_nodes_new_nodes
            # node_replacer = NodeReplacer()
            # new_tree = node_replacer.replace(src_tree, old_nodes_new_nodes)
        
            # # Export new_code
            # new_src = new_tree.code

            # return new_src

def main():
    orchestrator = Orchestrator()
    new_src = orchestrator.transform(src)
    print(new_src)


if __name__ == "__main__":
    main()