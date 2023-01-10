import time
import warnings
from abc import ABC, abstractproperty, abstractstaticmethod
from math import isclose
from typing import NamedTuple

warnings.filterwarnings("ignore")

import pandas

from db import LOCAL_CONFIG_01GB, PostgresConfig, PostgresConnection


class EvaluationResult(NamedTuple):
    results: pandas.DataFrame
    execution_time: float


class Evaluator(ABC):
    def __init__(self, db_config=LOCAL_CONFIG_01GB):
        self.db_config = db_config
        self.execution_time = None
        self.results = None

    def evaluate_function(self, function) -> EvaluationResult:
        start = time.time()
        results = function(self.db_config)
        end = time.time()
        execution_time = end - start

        return EvaluationResult(results, execution_time)

    def evaluate_correctness(self, unoptimized_results, optimized_results):
        are_equal = False
        if isinstance(unoptimized_results, pandas.DataFrame):
            # if unoptimized_results.equals(optimized_results):
            if unoptimized_results[~unoptimized_results.apply(tuple, 1).isin(optimized_results.apply(tuple, 1))].empty:
                are_equal = True
        elif isinstance(unoptimized_results, float):
            if isclose(unoptimized_results, optimized_results, rel_tol=1e-09, abs_tol=0.0):
                are_equal = True
        else:
            if unoptimized_results == optimized_results:
                are_equal = True

        if are_equal:
            print("Unoptimized code and optimized code have the same result")
        else:
            print("Unoptimized code and optimized code DON'T have the same result")

    def print_performance_evaluation(self, unoptimized_execution_time, optimized_execution_time):
        print(f"Unoptimized code execution time: {unoptimized_execution_time}")
        print(f"optimized code execution time: {optimized_execution_time}")

    def evaluate(self):
        print(f"Evaluating {self.name}:")
        unoptimized_results = self.evaluate_function(self.unoptimized_function)
        optimized_results = self.evaluate_function(self.optimized_function)
        self.evaluate_correctness(unoptimized_results.results, optimized_results.results)
        self.print_performance_evaluation(unoptimized_results.execution_time, optimized_results.execution_time)
        print("----------------")

    @abstractstaticmethod
    def unoptimized_function(db_config: PostgresConfig):
        pass

    @abstractstaticmethod
    def optimized_function(db_config: PostgresConfig):
        pass  # can be later replaced with Optimizer(self.unoptimized_function)

    @abstractproperty
    def name(self):
        pass


class LineItemOrdersJoinEvaluator(Evaluator):
    @property
    def name(self):
        return "Lineitems Join Orders"

    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            line_items = pandas.read_sql("SELECT l_orderkey, l_quantity FROM lineitem", conn)
            orders = pandas.read_sql("SELECT o_orderkey, o_totalprice FROM orders", conn)
            return pandas.merge(line_items, orders, left_on="l_orderkey", right_on="o_orderkey", how="left")
            # return pandas.merge(line_items, orders, on="orderkey", suffixes=("l_", "o_"), how="left")

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql(
                "SELECT * FROM \
                (SELECT l_orderkey, l_quantity FROM lineitem) AS t1\
                LEFT JOIN (SELECT o_orderkey, o_totalprice FROM orders) AS t2\
                ON t1.l_orderkey = t2.o_orderkey",
                conn,
            )


class PartsuppPartJoinEvaluator(Evaluator):
    @property
    def name(self):
        return "Partsupps Join Parts"

    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            partsupps = pandas.read_sql("SELECT * FROM partsupp", conn)
            parts = pandas.read_sql("SELECT * FROM part", conn)
            return pandas.merge(partsupps, parts, left_on="ps_partkey", right_on="p_partkey", how="left")
            # return pandas.merge(line_items, orders, on="orderkey", suffixes=("l_", "o_"), how="left")

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql(
                "SELECT * FROM \
                (SELECT * FROM partsupp) AS t1\
                LEFT JOIN (SELECT * FROM part) AS t2\
                ON t1.ps_partkey = t2.p_partkey",
                conn,
            )


class L_DiscountMaxEvaluator(Evaluator):
    @property
    def name(self):
        return "Max Discount of Lineitems"

    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            line_items_discounts = pandas.read_sql("SELECT l_discount FROM lineitem", conn)
            return line_items_discounts.max(axis=0)[0]

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql("SELECT MAX(l_discount) as max FROM lineitem", conn)["max"][0]


class O_TotalPriceSumEvaluator(Evaluator):
    @property
    def name(self):
        return "Sum Totalprice Orders"

    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            line_items_discounts = pandas.read_sql("SELECT o_totalprice FROM orders", conn)
            return line_items_discounts.sum(axis=0)[0]

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql("SELECT SUM(o_totalprice) FROM orders", conn)["sum"][0]


def main():
    L_DiscountMaxEvaluator().evaluate()
    O_TotalPriceSumEvaluator().evaluate()
    PartsuppPartJoinEvaluator().evaluate()
    LineItemOrdersJoinEvaluator().evaluate()


if __name__ == "__main__":
    main()
