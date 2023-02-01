from .pipeline_example import PipelineExample

operator_chaining_examples = [
    PipelineExample(
        "first join then aggregate",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)
        df2 = pd.read_sql("SELECT * from table2", con)

        result = df1.join(df2).max()
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        temp = pd.read_sql("SELECT * FROM (SELECT attribute1 FROM table1) JOIN (SELECT * from table2) LIMIT 0", con).columns
        result = pd.read_sql(f"SELECT {', '.join(['MAX(' + c + ') AS max_' + c for c in temp])} FROM (SELECT attribute1 FROM table1) JOIN (SELECT * from table2)", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "first aggregate(without prequery!) then join",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)
        df2 = pd.read_sql("SELECT * from table2", con)

        result = df1.max().join(df2)
        result # do something with result

        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT MAX(attribute1) AS max_attribute1 FROM table1) JOIN (SELECT * from table2)", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "multiple joins",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)
        df3 = pd.read_sql("SELECT * FROM table3", con)

        result = df1.join(df2).join(df3)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM (SELECT * FROM table1) JOIN (SELECT * FROM table2)) JOIN (SELECT * FROM table3)", con)
        result # do something with result
        """,
    ),
]
