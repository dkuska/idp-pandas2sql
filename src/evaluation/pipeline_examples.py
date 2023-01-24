from textwrap import dedent

PipelineCode = str


# Do you have better name for this? Maybe UseCase?
class PipelineExample:
    name: str
    code: PipelineCode
    optimized_code: PipelineCode

    def __init__(self, name: str, code: PipelineCode, optimized_code: PipelineCode):
        self.name = name
        self.code = dedent(code)
        self.optimized_code = dedent(optimized_code)


join_pipeline_examples = [
    PipelineExample(
        "normal join",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT * FROM table1", "sqlite:///test.db")
        df2 = pd.read_sql("SELECT attr1, attr2 FROM table2", "sqlite:///test.db")

        result = df1.join(df2)
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) JOIN (SELECT * FROM table2)", "sqlite:///test.db")
        """,
    ),
    PipelineExample(
        "inner join",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT * FROM table1", "sqlite:///test.db")
        df2 = pd.read_sql("SELECT attr1, attr2 FROM table2", "sqlite:///test.db")

        result = df1.join(df2, how="inner")
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) INNER JOIN (SELECT * FROM table2)", "sqlite:///test.db")
        """,
    ),
    PipelineExample(
        "left join",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT * FROM table1", "sqlite:///test.db")
        df2 = pd.read_sql("SELECT attr1, attr2 FROM table2", "sqlite:///test.db")

        result = df1.join(df2, how="left")
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) LEFT JOIN (SELECT * FROM table2)", "sqlite:///test.db")
        """,
    ),
    PipelineExample(
        "join on key",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT * FROM table1", "sqlite:///test.db")
        df2 = pd.read_sql("SELECT attr1, attr2 FROM table2", "sqlite:///test.db")

        result = df1.join(df2, on="key")
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) JOIN (SELECT * FROM table2)" ON table1.key = table2.key, "sqlite:///test.db")
        """,
    ),
    PipelineExample(
        "inner join on key",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT * FROM table1", "sqlite:///test.db")
        df2 = pd.read_sql("SELECT attr1, attr2 FROM table2", "sqlite:///test.db")

        result = df1.join(df2, on="key", how="inner")
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT * FROM (SELECT * FROM table1) INNER JOIN (SELECT * FROM table2)" ON table1.key = table2.key, "sqlite:///test.db")
        """,
    ),
]

aggregation_pipeline_examples = [
    PipelineExample(
        "sum",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT attribute1 FROM table1", "sqlite:///test.db")

        result = df1.sum()
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT SUM(attribute1) AS sum_attribute1 FROM table1", "sqlite:///test.db")
        """,
    ),
    PipelineExample(
        "average",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT attribute1 FROM table1", "sqlite:///test.db")

        result = df1.mean()
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT AVG(attribute1) AS avg_attribute1 FROM table1", "sqlite:///test.db")
        """,
    ),
    PipelineExample(
        "aggregate with max",
        """
        import pandas as pd

        df1 = pd.read_sql("SELECT attribute1 FROM table1", "sqlite:///test.db")

        result = df1.aggregate("max")
        """,
        """
        import pandas as pd

        result = pd.read_sql("SELECT MAX(attribute1) AS max_attribute1 FROM table1", "sqlite:///test.db")
        """,
    ),
]
