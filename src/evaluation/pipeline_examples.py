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
