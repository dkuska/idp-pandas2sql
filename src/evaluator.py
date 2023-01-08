import time
from abc import ABC, abstractstaticmethod
from typing import NamedTuple

import pandas

from db import (
    LOCAL_CONFIG_01GB,
    PostgresConfig,
    PostgresConnection,
)


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
        if unoptimized_results.results.equals(optimized_results.results):
            print("Unoptimized code and optimized code have the same result")
        else:
            print("Unoptimized code and optimized code don't have the same result")

        print("----------------")

    def print_performance_evaluation(self, unoptimized_results, optimized_results):
        print(f"Unoptimized code execution time: {unoptimized_results.execution_time}")
        print(f"optimized code execution time: {optimized_results.execution_time}")
        print("----------------")

    def evaluate(self):
        print(f"Evaluating {self.__class__.__name__}:")
        unoptimized_results = self.evaluate_function(self.unoptimized_function)
        optimized_results = self.evaluate_function(self.optimized_function)
        self.evaluate_correctness(unoptimized_results, optimized_results)
        self.print_performance_evaluation(unoptimized_results, optimized_results)

    @abstractstaticmethod
    def unoptimized_function(db_config: PostgresConfig):
        pass

    @abstractstaticmethod
    def optimized_function(db_config: PostgresConfig):
        pass  # can be later replaced with Optimizer(self.unoptimized_function)


class JoinEvaluator(Evaluator):
    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            line_items = pandas.read_sql("SELECT * FROM lineitem", conn)
            orders = pandas.read_sql("SELECT * FROM orders", conn)
            return pandas.merge(line_items, orders, left_on="l_orderkey", right_on="o_orderkey", how="inner")
            # return pandas.merge(line_items, orders, on="orderkey", suffixes=("l_", "o_"), how="inner")

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql(
                "SELECT * FROM \
                (SELECT * FROM lineitem) AS t1\
                INNER JOIN (SELECT * FROM orders) AS t2\
                ON t1.l_orderkey = t2.o_orderkey",
                conn,
            )


class MaxEvaluator(Evaluator):
    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            line_items_discounts = pandas.read_sql("SELECT l_discount FROM lineitem", conn)
            return line_items_discounts.max(axis=0)

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql("SELECT MAX(l_discount) FROM lineitem", conn)


class SumEvaluator(Evaluator):
    @staticmethod
    def unoptimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            line_items_discounts = pandas.read_sql("SELECT o_totalprice FROM orders", conn)
            return line_items_discounts.sum(axis=0)

    @staticmethod
    def optimized_function(db_config: PostgresConfig):
        with PostgresConnection(db_config) as conn:
            return pandas.read_sql("SELECT SUM(o_totalprice) FROM orders", conn)


def main():
    MaxEvaluator().evaluate()
    SumEvaluator().evaluate()
    JoinEvaluator().evaluate()


if __name__ == "__main__":
    main()
