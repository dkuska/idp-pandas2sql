from .pipeline_example import PipelineExample

sort_pipeline_examples = [
    PipelineExample(
        "normal sort_values with arg",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT attribute1, attribute2 FROM table1", con)

        result = df.sort_values("attribute1")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT attribute1, attribute2 FROM table1 ORDER BY attribute1 ASC", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "sort_values with kwarg",
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
        "sort_values desc",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df = pd.read_sql("SELECT attribute1, attribute2 FROM table1", con)

        result = df.sort_values(["attribute1", "attribute2"], ascending=False)
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
