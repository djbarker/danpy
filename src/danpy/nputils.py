from typing import Literal
import numpy as np

__all__ = [
    "clip_vec",
    "rescale_vec",
    "unit_vec",
    "vec_2d_polar",
    "symlogspace",
]


def symlogspace(start: float, stop: float, num: int, base: float = 10) -> np.ndarray:
    """
    Create logspaced values in both the +ve and -ve directions.

    Arguments map directly to their equivalents in py:meth`numpy.logspace`.
    Whether to include zero or not is decided by whether `num` is even or odd.

    .. code-block:: Python

        symlogspace(-2, 0, 7)  # returns np.array([-1, -0.1, -0.01, 0, +0.01, +0.1, +1])
        symlogspace(-2, 0, 6)  # returns np.array([-1, -0.1, -0.01,    +0.01, +0.1, +1])

    Args:
        start: The exponent of the smallest non-zero value.
        stop: The exponent of the largest value.
        num: The total number of values in the output array.
        base: See py:meth`numpy.logspace`.

    Returns:
        The sample array.
    """

    assert start < stop
    assert num > 1

    z = num % 2  # Include zero or not?
    n = (num - z) // 2
    x = np.logspace(start, stop, n)
    print(num, z, n, x)
    x = np.concatenate([-x[::-1], [0] * z, x])

    return x


def clip_vec(v: np.ndarray, vmax: float, inplace: bool = False) -> np.ndarray:
    """
    Clip an array of vectors to be a maximum length.

    For an N dimensional array ``v`` this will clip the last axis to have a maximum (Euclidean) norm of ``vmax``.

    .. code-block:: Python

        vv = np.stack([vx, vy], axis=-1)
        vv = clip_vec(vv, 1.0)

    Args:
        v: The array to clip.
        vmax: The maximum length of the vectors.
        inplace: If ``True``, update ``v`` in place.

    Returns:
        The clipped array, which has the same size as the input array.
    """
    if not inplace:
        v = v.copy()

    vmag = np.sqrt(np.sum(v**2, axis=-1))
    mask = vmag > vmax
    v[mask] = vmax * (v[mask] / vmag[mask][:, None])

    return v


def rescale_vec(v: np.ndarray, vmag: float, inplace: bool = False) -> np.ndarray:
    """
    Rescale an array of vectors to be a specified length.

    For an N dimensional array ``v`` this will rescale the last axis to have a (Euclidean) norm of ``vmag``.

    .. code-block:: Python

        vv = np.stack([vx, vy], axis=-1)
        vv = rescale_vec(vv, 2.5)

    Args:
        v: The array to rescale.
        vmag: The new length of the vectors.
        inplace: If ``True``, update ``v`` in place.

    Returns:
        The rescale array, which has the same size as the input array.
    """
    if not inplace:
        v = v.copy()

    vmag_ = np.sqrt(np.sum(v**2, axis=-1))
    v[:] = vmag * v / vmag_[..., None]

    return v


def unit_vec(v: np.ndarray, inplace: bool = False) -> np.ndarray:
    """
    Normalize an array of vectors to be a unit length.

    For an N dimensional array ``v`` this will rescale the last axis to have a maximum (Euclidean) norm of 1.
    Shorthand for `rescale_vec(v, 1.0)`.

    .. code-block:: Python

        vv = np.stack([vx, vy], axis=-1)
        vv = unit_vec(vv)

    Args:
        v: The array to normalize.
        inplace: If ``True``, update ``v`` in place.

    Returns:
        The normalized array, which has the same size as the input array.
    """
    return rescale_vec(v, 1.0, inplace)


def vec_2d_polar(
    angle: float | np.ndarray,
    scale: float | np.ndarray,
    angle_units: Literal["deg", "rad"] = "deg",
) -> np.ndarray:
    """
    Make one or more vectors in Cartesian coordinates from the given polar coordinates.

    Args:
        angle: The angle(s) of the vector(s).
        scale: The length(s) of the vector(s).
        angle_units: Whether the angles are specified in degrees or radians.

    Returns:
        Either a 1d array with 2 elements if both ``angle`` and ``scale`` are scalars,
        Otherwise an array with one more dimension than the inputs having length 2.

    Note:
        If both ``angle`` and ``scale`` are numpy arrays then their shape must match.
    """

    # Wrap scalars in numpy arrays as appropriate.
    match (angle, scale):
        case np.ndarray(), np.ndarray():
            pass
        case np.ndarray(), _:
            scale = scale * np.ones_like(angle)
        case _, np.ndarray():
            angle = angle * np.ones_like(scale)
        case _, _:
            angle = np.array([angle])
            scale = np.array([scale])

    assert angle.shape == scale.shape, f"Size mismatch! [{angle.shape=}, {scale.shape=}]"

    if angle_units == "deg":
        angle = angle * np.pi / 180.0

    x = np.cos(angle) * scale
    y = np.sin(angle) * scale

    xy = np.stack([x, y], axis=-1)
    xy = np.squeeze(xy)

    return xy
