from danpy.grid_layout import grid_layout_2d, grid_layout_3d


def test_grid_layout_2d():
    assert grid_layout_2d(1) == (1, 1)
    assert grid_layout_2d(2) == (1, 2)
    assert grid_layout_2d(3) == (1, 3)
    assert grid_layout_2d(4) == (2, 2)
    assert grid_layout_2d(5) == (1, 5)
    assert grid_layout_2d(6) == (2, 3)
    assert grid_layout_2d(7) == (1, 7)
    assert grid_layout_2d(8) == (2, 4)
    assert grid_layout_2d(9) == (3, 3)
    assert grid_layout_2d(10) == (2, 5)


def test_grid_layout_3d():
    assert grid_layout_3d(1) == (1, 1, 1)
    assert grid_layout_3d(2) == (1, 1, 2)
    assert grid_layout_3d(3) == (1, 1, 3)
    assert grid_layout_3d(4) == (1, 2, 2)
    assert grid_layout_3d(5) == (1, 1, 5)
    assert grid_layout_3d(6) == (1, 2, 3)
    assert grid_layout_3d(7) == (1, 1, 7)
    assert grid_layout_3d(8) == (2, 2, 2)
    assert grid_layout_3d(9) == (1, 3, 3)
    assert grid_layout_3d(10) == (2, 1, 5)
