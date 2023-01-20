from src.code_manager import CodeManager
from src.evaluation.pipeline_examples import pipeline_with_filter, pipeline_with_join

from .conftest import given


@given(
    "pipeline_function",
    [pipeline_with_join, pipeline_with_filter],
)
def test_loading_from_function(pipeline_function):
    code_manager = CodeManager.from_function(pipeline_function)
    assert all(code_manager.execute_code() == pipeline_function())
