from src.code_translation.orchestrator import Orchestrator
from src.evaluation.pipeline_examples import PipelineExample

from .conftest import assert_equal_code, given


@given(
    "pipeline",
    [],
)
def test_keep_non_interested_code(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)


@given(
    "pipeline",
    [],
)
def test_with_unknown_modules(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)


@given(
    "pipeline",
    [],
)
def test_used_intermediate_results(pipeline: PipelineExample):
    assert_equal_code(Orchestrator().transform(pipeline.code), pipeline.optimized_code)
