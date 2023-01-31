from src.code_translation.orchestrator import Orchestrator
from src.evaluation.examples import (
    PipelineExample,
    aggregation_pipeline_examples,
    join_pipeline_examples,
    operator_chaining_pipeline_examples,
    sort_pipeline_examples,
)

from .conftest import assert_equal_code, given


@given(
    "pipeline",
    sort_pipeline_examples,
)
def test_sort_pipeline(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)


@given(
    "pipeline",
    join_pipeline_examples,
)
def test_join_pipeline(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)


@given(
    "pipeline",
    aggregation_pipeline_examples,
)
def test_aggregation_pipeline(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)


@given(
    "pipeline",
    operator_chaining_pipeline_examples,
)
def test_operator_chaining_pipeline(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)
