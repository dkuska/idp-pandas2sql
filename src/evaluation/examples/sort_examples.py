from .pipeline_example import PipelineExample

sort_pipeline_examples = [
    PipelineExample(
        "normal sort_values",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT attribute1, attribute2 FROM table1", con)

        result = df.sort_values()
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT attribute1, attribute2 FROM table1 ORDER BY attribute1, attribute2 ASC", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "sort_values with by='attribute1'",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT * FROM table1", con)

        result = df.sort_values(by='attribute1')
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM table1 ORDER BY attribute1 ASC", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "sort_values with by=['attribute1', 'attribute2']",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT * FROM table1", con)

        result = df.sort_values(by=['attribute1', 'attribute2'])
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT * FROM table1 ORDER BY attribute1, attribute2 ASC", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "sort_values with SELECT *",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT * FROM table1", con)

        result = df.sort_values()
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        temp = pd.read_sql("SELECT * FROM table1 LIMIT 0", con).columns
        result = pd.read_sql(f"SELECT * FROM table1 ORDER BY {', '.join(temp)} ASC", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "normal sort_values desc",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT attribute1, attribute2 FROM table1", con)

        result = df.sort_values(ascending=False)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT attribute1, attribute2 FROM table1 ORDER BY attribute1, attribute2 DESC", con)
        result # do something with result
        """,
    ),
]
