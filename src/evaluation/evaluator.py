import time
import warnings

from ..code_translation.orchestrator import Orchestrator
from .db import POSTGRES_TPC_H_30GB_CONFIG
from .examples import PipelineCode, PipelineExample

warnings.filterwarnings("ignore")

DB_CONFIG = POSTGRES_TPC_H_30GB_CONFIG
ITERATIONS = 3


def combine_results(results: float) -> float:
    return sum(results) / len(results)  # mean
    # return results[len(results) // 2] # median


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
        print(f"Optimized code execution time: {optimized_execution_time:.2f}s")
        print("----------------")

    def multiple_evaluate(self, optimized: bool = False):
        print(f"Evaluating {'optimized' if optimized else 'unoptimized'} {self.pipeline.name.upper()}:")
        results = []

        for _ in range(ITERATIONS):
            if optimized:
                result = self.evaluate_function(self.pipeline.optimized_code)
            else:
                result = self.evaluate_function(self.pipeline.code)
            results.append(result)
            print(f"Code execution time: {result:.2f}s")

        print(f"Average code execution time: {combine_results(results):.2f}s")

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
        order_prices = pandas.read_sql("SELECT o_totalprice FROM orders", conn)
        results = order_prices.sum(axis=0)[0]
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql("SELECT SUM(o_totalprice) FROM orders", conn)["sum"][0]
    """,
)

sorted_orders_by_total_price = PipelineExample(
    "Sort of Orders by Totalprice",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        orders = pandas.read_sql("SELECT * FROM orders", conn)
        results = orders.sort_values(by="o_totalprice")
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql("SELECT * FROM orders ORDER BY o_totalprice", conn)
    """,
)

orders_join_with_early_customers_pipeline = PipelineExample(
    "Orders of Customer with id smaller than 1000",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        customer = pandas.read_sql("SELECT * FROM customer WHERE c_name LIKE '%' || '000000' ||'%'", conn)
        orders = pandas.read_sql("SELECT * FROM orders", conn)
        results = pandas.merge(customer, orders, left_on="c_custkey", right_on="o_custkey", how="inner")
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql(
            "SELECT * FROM \
                (SELECT * FROM customer WHERE c_name LIKE '%' || '000000' ||'%') AS t1\
                INNER JOIN (SELECT * FROM orders) AS t2\
                ON t1.c_custkey = t2.o_custkey",
            conn,
        )
    
    """,
)

orders_join_with_half_customers_pipeline = PipelineExample(
    "Orders of Customer with id smaller than 1000000",
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        customer = pandas.read_sql("SELECT * FROM customer WHERE c_name LIKE '%' || '000' ||'%'", conn) # 0.89s on the db
        orders = pandas.read_sql("SELECT * FROM orders", conn) # 10.65s on the db 
        results = pandas.merge(customer, orders, left_on="c_custkey", right_on="o_custkey", how="inner") # 11.20s
    """,
    """
    import pandas
    from .db import PostgresConnection
    with PostgresConnection(DB_CONFIG) as conn:
        results = pandas.read_sql(
            "SELECT * FROM \
                (SELECT * FROM customer WHERE c_name LIKE '%' || '000' ||'%') AS t1\
                INNER JOIN (SELECT * FROM orders) AS t2\
                ON t1.c_custkey = t2.o_custkey",
            conn,
        ) # 19.58s on the db
    """,
)


def main():
    Evaluator(lineitem_join_orders_pipeline).multiple_evaluate()


if __name__ == "__main__":
    main()

"""
transofrmation time: 0.01s for all pipelines
connection time: 0.43s for all pipelines
"""
