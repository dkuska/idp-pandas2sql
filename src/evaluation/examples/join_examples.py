from .pipeline_example import PipelineExample

join_pipeline_examples = [
    PipelineExample(
        "normal join",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) JOIN (SELECT * FROM table2)", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "inner join",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, how="inner")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) INNER JOIN (SELECT * FROM table2)", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "left join",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, how="left")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) LEFT JOIN (SELECT * FROM table2)", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "join on key",
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

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 JOIN (SELECT * FROM table2) AS S2 ON S1.key = S2.key", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "inner join on key",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, on="key", how="inner")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) AS S1 INNER JOIN (SELECT * FROM table2) AS S2 ON S1.key = S2.key", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "join with sort",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)
        df2 = pd.read_sql("SELECT * FROM table2", con)

        result = df1.join(df2, sort=True)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        temp = pd.read_sql("SELECT * FROM (SELECT * FROM table1) JOIN (SELECT * FROM table2) LIMIT 0", con).columns
        result = pd.read_sql(f"SELECT * FROM (SELECT * FROM table1) JOIN (SELECT * FROM table2) ORDER BY {', '.join(temp)} ASC", con)
        result # do something with result
        """,
    ),
]
