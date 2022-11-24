from ast import *
import astor


from ast_nodetransformer import *
from ast_nodevisitor import * 

sample = """
import numpy
import pandas as pd

df1 = pd.read_sql("SELECT * FROM table1")
df2 = pd.read_sql("SELECT * FROM table2")
df3 = df1.join(df2, how='inner')
"""

def main():
    tree = parse(sample, mode='exec')
    print(dump(tree, indent=2))
            
    analyzer = Analyzer()
    analyzer.visit(tree)
    analyzer.report()

    # transformer = Transformer(analyzer)
    # transformer.visit(tree)


if __name__ == "__main__":
    main()