__all__ = [
    "grid_layout_2d",
    "grid_layout_3d",
]


def grid_layout_2d(count: int) -> tuple[int, int]:
    """
    Calculate the layout for a grid containing a set number of cells that is closest to a square.

    The result will always obey ``np.prod(layout_2d(N)) == N``.

    Args:
        count: How many grid cells to lay out.

    Returns:
        The count of cells along each dimension.
    """
    root = 1
    for i in range(2, int(count ** (1.0 / 2.0)) + 1):
        if count % i == 0:
            root = i

    return (root, count // root)


def grid_layout_3d(count: int) -> tuple[int, int, int]:
    """
    Calculate the layout for a grid containing a set number of cells that is closest to a cube.

    The result will always obey ``np.prod(layout_2d(N)) == N``.

    Args:
        count: How many grid cells to lay out.

    Returns:
        The count of cells along each dimension.
    """
    root = 1
    for i in range(2, int(count ** (1.0 / 3.0)) + 1):
        if count % i == 0:
            root = i

    (ny, nx) = grid_layout_2d(count // root)

    return (root, ny, nx)
