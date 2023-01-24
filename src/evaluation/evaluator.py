import time
import warnings

from .db import LOCAL_CONFIG_1GB
from .pipeline_examples import PipelineCode, PipelineExample

warnings.filterwarnings("ignore")

DB_CONFIG = LOCAL_CONFIG_1GB


class Evaluator:
    def __init__(self, pipeline: PipelineExample):
        self.pipeline = pipeline
        self.execution_time = None
        self.results = None

    def evaluate_function(self, code: PipelineCode) -> float:
        start = time.time()
        exec(code)
        end = time.time()
        execution_time = end - start

        return execution_time

    def evaluate(self):
        print(f"Evaluating {self.pipeline.name.upper()}:")
        unoptimized_execution_time = self.evaluate_function(self.pipeline.code)
        optimized_execution_time = self.evaluate_function(self.pipeline.optimized_code)
        print(f"Unoptimized code execution time: {unoptimized_execution_time:.2f}s")
        print(f"optimized code execution time: {optimized_execution_time:.2f}s")
        print("----------------")


lineitem_join_orders_pipeline = PipelineExample(
    "Lineitems Join Orders",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        line_items = pandas.read_sql("SELECT l_orderkey, l_quantity FROM lineitem", conn)  # 13.25s 96MB 1.3s on db
        orders = pandas.read_sql("SELECT o_orderkey, o_totalprice FROM orders", conn)  # 3.21 24MB 0.3s on db
        results = pandas.merge(
            line_items, orders, left_on="l_orderkey", right_on="o_orderkey", how="left"
        )  # 1.06s 240MB
        # results = pandas.merge(line_items, orders, on="orderkey", suffixes=("l_", "o_"), how="left")
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql(
            "SELECT * FROM \
            (SELECT l_orderkey, l_quantity FROM lineitem) AS t1\
            LEFT JOIN (SELECT o_orderkey, o_totalprice FROM orders) AS t2\
            ON t1.l_orderkey = t2.o_orderkey",
            conn,
        )  # 24.70s 192MB 0.7s on db
    """,
)


partsupp_join_parts_pipeline = PipelineExample(
    "Partsupp Join Parts",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        partsupps = pandas.read_sql("SELECT * FROM partsupp", conn)
        parts = pandas.read_sql("SELECT * FROM part", conn)
        result = pandas.merge(partsupps, parts, left_on="ps_partkey", right_on="p_partkey", how="left")
        # results = pandas.merge(line_items, orders, on="orderkey", suffixes=("l_", "o_"), how="left")
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        result = pandas.read_sql(
            "SELECT * FROM \
            (SELECT * FROM partsupp) AS t1\
            LEFT JOIN (SELECT * FROM part) AS t2\
            ON t1.ps_partkey = t2.p_partkey",
            conn,
        )
    """,
)


max_lineitem_discount_pipeline = PipelineExample(
    "Max Discount of Lineitems",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        line_items_discounts = pandas.read_sql("SELECT l_discount FROM lineitem", conn)
        result = line_items_discounts.max(axis=0)[0]
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        result = pandas.read_sql("SELECT MAX(l_discount) as max FROM lineitem", conn)["max"][0]
    """,
)


sum_orders_totalprice_pipeline = PipelineExample(
    "Sum Totalprice of Orders",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        line_items_discounts = pandas.read_sql("SELECT o_totalprice FROM orders", conn)
        results = line_items_discounts.sum(axis=0)[0]
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql("SELECT SUM(o_totalprice) FROM orders", conn)["sum"][0]
    """,
)


def main():
    Evaluator(lineitem_join_orders_pipeline).evaluate()
    Evaluator(partsupp_join_parts_pipeline).evaluate()
    Evaluator(max_lineitem_discount_pipeline).evaluate()
    Evaluator(sum_orders_totalprice_pipeline).evaluate()


if __name__ == "__main__":
    main()
