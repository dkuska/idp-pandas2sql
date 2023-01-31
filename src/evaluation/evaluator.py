import time
import warnings

from ..code_translation.orchestrator import Orchestrator
from .db import POSTGRES_TPC_H_10GB_CONFIG
from .examples import PipelineCode, PipelineExample

warnings.filterwarnings("ignore")

DB_CONFIG = POSTGRES_TPC_H_10GB_CONFIG


def evaluate_connectoin():
    start = time.time()

    from .db import PostgresConnection

    with PostgresConnection(DB_CONFIG):
        pass
    end = time.time()
    print(f"Connection time: {end - start:.2f}s")


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

    def evaluate_transofmation(self):
        start = time.time()
        Orchestrator().transform(self.pipeline.code)
        end = time.time()
        print(f"Transformation time: {end - start:.2f}s")


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

orders_join_one_customer_pipeline = PipelineExample(
    "Orders of Customer with name Customer#000000002",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        customer = pandas.read_sql("SELECT * FROM customer WHERE c_name = 'Customer#000000002'", conn)
        orders = pandas.read_sql("SELECT * FROM orders", conn)
        results = pandas.merge(customer, orders, left_on="c_custkey", right_on="o_custkey", how="inner")
        print(customer.memory_usage())
        print(orders.memory_usage())
        print(results.memory_usage())
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql(
        "SELECT * FROM \
            (SELECT * FROM customer WHERE c_name = 'Customer#000000002') AS t1\
            INNER JOIN (SELECT * FROM orders) AS t2\
            ON t1.c_custkey = t2.o_custkey",
        conn,
    )
    print(results.memory_usage())
    """,
)


def main():
    Evaluator(lineitem_join_orders_pipeline).evaluate()
    Evaluator(partsupp_join_parts_pipeline).evaluate()
    Evaluator(max_lineitem_discount_pipeline).evaluate()
    Evaluator(sum_orders_totalprice_pipeline).evaluate()
    Evaluator(orders_join_one_customer_pipeline).evaluate()


if __name__ == "__main__":
    main()

"""
s = 1
Evaluating LINEITEMS JOIN ORDERS:
Unoptimized code execution time: 10.17s
optimized code execution time: 14.85s
----------------
Evaluating PARTSUPP JOIN PARTS:
Unoptimized code execution time: 2.27s
optimized code execution time: 3.95s
----------------
Evaluating MAX DISCOUNT OF LINEITEMS:
Unoptimized code execution time: 5.25s
optimized code execution time: 0.36s
----------------
Evaluating SUM TOTALPRICE OF ORDERS:
Unoptimized code execution time: 1.42s
optimized code execution time: 0.09s
----------------

s = 10
Evaluating LINEITEMS JOIN ORDERS:
Unoptimized code execution time: 99.69s
{
    lineitem: 959.8 MB in 67.6s (13.1s on the db),
    orders: 24.0 MB in 17.8s (3.8s on the db),
    results: 2399.4 MB in 10.5s,
}
optimized code execution time: 145.54s
{
    results: 1919.6 MB in 145.4s (38.8s on the db),
}
----------------
Evaluating PARTSUPP JOIN PARTS:
Unoptimized code execution time: 22.60s
optimized code execution time: 37.68s
----------------
Evaluating MAX DISCOUNT OF LINEITEMS:
Unoptimized code execution time: 49.11s
optimized code execution time: 2.26s
----------------
Evaluating SUM TOTALPRICE OF ORDERS:
Unoptimized code execution time: 13.87s
optimized code execution time: 0.72s
----------------
Evaluating ORDERS OF CUSTOMER WITH NAME CUSTOMER#000000002:
Unoptimized code execution time: 43.18s
{
    lineitem: 192 B,
    orders: 1 GB,
    results: 432 B,
}
optimized code execution time: 0.72s
{
    results: 536 B,
}

transofrmation time: 0.01s for all pipelines
connection time: 0.43s for all pipelines
"""
