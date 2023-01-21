from src.code_translation.orchestrator import Orchestrator
from src.evaluation.pipeline_examples import (
    PipelineExample,
    aggregation_pipeline_examples,
    join_pipeline_examples,
)

from .conftest import given


def is_equal_code(code1: str, code2: str) -> bool:
    return code1.strip() == code2.strip()


@given(
    "pipeline",
    join_pipeline_examples,
)
def test_join_pipeline(pipeline: PipelineExample):
    assert is_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)


@given(
    "pipeline",
    aggregation_pipeline_examples,
)
def test_aggregation_pipeline(pipeline: PipelineExample):
    assert is_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)
