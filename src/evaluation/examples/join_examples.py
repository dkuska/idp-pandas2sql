from .pipeline_example import PipelineExample

join_pipeline_examples = [
    PipelineExample(
        "normal join on indices",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con).set_index("key1")
        df2 = pd.read_sql("SELECT * FROM table2", con).set_index("key2")

        result = df1.join(df2)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 LEFT JOIN (SELECT * FROM table2) AS S2 ON S1.key1 = S2.key2", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "inner join on indices",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con).set_index("key1")
        df2 = pd.read_sql("SELECT * FROM table2", con).set_index("key2")

        result = df1.join(df2, how="inner")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 INNER JOIN (SELECT * FROM table2) AS S2 ON S1.key1 = S2.key2", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "join on attribute",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, on="key")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 LEFT JOIN (SELECT * FROM table2) AS S2 ON S1.key = S2.key", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "join on multiple attributes",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, on=["key1", "key2"])
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 LEFT JOIN (SELECT * FROM table2) AS S2 ON S1.key1 = S2.key1 AND S1.key2 = S2.key2", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "join on attribute with sort",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, "attribute", sort=True)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 LEFT JOIN (SELECT * FROM table2) AS S2 ON S1.attribute = S2.attribute ORDER BY attribute ASC", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "join on indices with sort",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con).set_index("key1")
        df2 = pd.read_sql("SELECT * FROM table2", con).set_index("key2")

        result = df1.join(df2, sort=True)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 LEFT JOIN (SELECT * FROM table2) AS S2 ON S1.key1 = S2.key2 ORDER BY key1 ASC", con)
        result # do something with result
        """,
    ),
]
