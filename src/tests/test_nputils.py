import numpy as np
import pytest

from danpy.nputils import symlogspace, clip_vec, rescale_vec, unit_vec, vec_2d_polar

EPS = 1e-8


def test_symlogspace():
    # fmt: off
    assert np.allclose(np.array([-1, -0.1, -0.01, 0, 0.01, 0.1, 1]), symlogspace(-2, 0, 7))
    assert np.allclose(np.array([-1, -0.1, -0.01,    0.01, 0.1, 1]), symlogspace(-2, 0, 6))
    # fmt: on


def test_clip_vec():
    np.random.seed(42)

    # Test not in place.
    XX = np.random.normal(size=(100, 100, 2))
    YY = clip_vec(XX, 0.5)

    eps = 1e-8
    assert np.max(np.sqrt(np.sum(XX**2, axis=-1))) > 0.5 - eps
    assert np.max(np.sqrt(np.sum(YY**2, axis=-1))) <= 0.5 + eps

    # Now test updating in place.
    clip_vec(XX, 0.5, inplace=True)

    assert np.max(np.sqrt(np.sum(XX**2, axis=-1))) <= 0.5 + eps


def test_rescale_vec():
    np.random.seed(42)

    # Test not in place.
    XX = np.random.normal(size=(100, 100, 2))
    YY = rescale_vec(XX, 2.0)

    # fmt: off
    assert not np.allclose(np.sum(XX**2, axis=-1), 4.0)
    assert     np.allclose(np.sum(YY**2, axis=-1), 4.0)
    # fmt: on

    # Now test updating in place.
    rescale_vec(XX, 2.0, inplace=True)

    assert np.allclose(np.sum(XX**2, axis=-1), 4.0)


def test_unit_vec():
    np.random.seed(42)

    # Test not in place.
    XX = np.random.normal(size=(100, 100, 2))
    YY = unit_vec(XX)

    # fmt: off
    assert not np.allclose(np.sum(XX**2, axis=-1), 1.0)
    assert     np.allclose(np.sum(YY**2, axis=-1), 1.0)
    # fmt: on

    # Now test updating in place.
    unit_vec(XX, inplace=True)

    assert np.allclose(np.sum(XX**2, axis=-1), 1.0)


def test_vec_2d_polar():
    """
    Some basic tests on input- and output sizes and vector magnitudes.
    """

    vecs = [
        vec_2d_polar(0, 1.0),
        vec_2d_polar(90, 2.0),
        vec_2d_polar(45, 0.5),
    ]

    assert all(v.shape == (2,) for v in vecs)
    assert np.allclose([np.sum(v**2) for v in vecs], [1.0, 4.0, 0.25])

    angs = np.linspace(0, 90, 4)
    vecs = vec_2d_polar(angs, 1.0)
    assert vecs.shape == (len(angs), 2)
    assert np.allclose(np.sum(vecs**2, -1), np.ones_like(angs))

    scls = np.linspace(1, 10, 4)
    vecs = vec_2d_polar(0, scls)
    assert vecs.shape == (len(angs), 2)
    assert np.allclose(np.sum(vecs**2, -1), scls**2)

    with pytest.raises(AssertionError):
        vec_2d_polar(np.linspace(0, 90, 10), np.linspace(0, 10, 20))

    assert np.allclose(
        vec_2d_polar(180, 10, "deg"),
        vec_2d_polar(np.pi, 10, "rad"),
    )
