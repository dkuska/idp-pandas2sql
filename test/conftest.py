import pytest

given = pytest.mark.parametrize


def assert_equal_code(code1: str, code2: str) -> bool:
    assert code1.strip().replace("\n", "") == code2.strip().replace("\n", "")
