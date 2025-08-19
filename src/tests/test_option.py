import pytest
from danpy.option import Some, to_opt, map_opt, unwrap, or_default, or_get_default


def test_to_opt():
    x = Some(5)
    assert to_opt(x) is x
    assert to_opt(10) == Some(10)
    assert to_opt(None) is None


def test_map_opt():
    x = Some(5)
    assert map_opt(x, lambda x: x * 2) == Some(10)
    assert map_opt(5, lambda x: x * 2) == Some(10)
    assert map_opt(None, lambda x: x * 2) is None  # type: ignore


def test_unwrap():
    x = Some(5)
    assert unwrap(x) == 5
    assert unwrap(5) == 5

    with pytest.raises(TypeError):
        unwrap(None)


def test_or_default():
    assert or_default(5, 10) == 5
    assert or_default(Some(5), 10) == 5
    assert or_default(None, 10) == 10


def test_or_get_default():
    assert or_get_default(5, lambda: 10) == 5
    assert or_get_default(Some(5), lambda: 10) == 5
    assert or_get_default(None, lambda: 10) == 10
