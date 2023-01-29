from .pipeline_example import PipelineExample

aggregation_pipeline_examples = [
    PipelineExample(
        "sum",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)

        result = df1.sum()
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT SUM(attribute1) AS sum_attribute1 FROM table1", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "average",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)

        result = df1.mean()
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT AVG(attribute1) AS avg_attribute1 FROM table1", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "aggregate with max",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)

        result = df1.aggregate(max)
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT MAX(attribute1) AS max_attribute1 FROM table1", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        'aggregate with "max"',
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)

        result = df1.aggregate("max")
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT MAX(attribute1) AS max_attribute1 FROM table1", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "aggregate with 'min'",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT attribute1 FROM table1", con)

        result = df1.aggregate('min')
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        result = pd.read_sql("SELECT MIN(attribute1) AS min_attribute1 FROM table1", con)
        result # do something with result
        """,
    ),
    PipelineExample(
        "max with SELECT *",
        """
        import pandas as pd

        con = "sqlite:///test.db"

        df1 = pd.read_sql("SELECT * FROM table1", con)

        result = df1.max()
        result # do something with result
        """,
        """
        import pandas as pd

        con = "sqlite:///test.db"

        temp = pd.read_sql("SELECT * FROM table1 LIMIT 0", con).columns
        result = pd.read_sql(f"SELECT {', '.join(['MAX(' + c + ') AS max_' + c for c in temp])} FROM table1", con)
        result # do something with result
        """,
    ),
]
