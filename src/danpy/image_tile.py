import numpy as np

from pathlib import Path
from PIL import Image
from PIL.Image import Resampling
from typing import Sequence

from .grid_layout import grid_layout_2d

__all__ = [
    "image_tile",
    "image_tile_auto",
]


def image_tile(
    in_paths: Sequence[Sequence[str | Path]],
    out_path: str | Path,
    resolution: tuple[int, int] | None = None,
    background: str = "white",
):
    """
    Tile a set of images together & save the result.

    The layout of the combined images is determined by the shape of `in_paths`.
    Each element of `in_paths` is a sequence containing the paths to the images in that row.
    The rows need not have the same length, the largest row will determine the number of columns in the output image.

    If no resolution is provided the images will be combined at their original resolution.
    Any images smaller than others in their row or column will be padded with the background color.

    Args:
        in_paths: A ragged list of file paths.
        out_path: The path to save the combined image to.
        resolution: The (optional) resolution to save the image at.
        background: The background color to use for padding.
    """

    # Load the images into a ragged array with the same shape as `in_paths`.
    nrows = len(in_paths)
    ncols = 0
    images = []
    for path_row in in_paths:
        images_row = []
        for path in path_row:
            image = Image.open(path)
            images_row.append(image)
        images.append(images_row)
        ncols = max(ncols, len(images_row))

    # Calculate the maximum width of each column.
    widths = [0] * ncols
    for row in range(nrows):
        for col in range(len(in_paths[row])):
            image = images[row][col]
            widths[col] = max(widths[col], image.width)

    # Calculate the maximum height of each row.
    heights = [0] * nrows
    for row in range(nrows):
        for col in range(len(in_paths[row])):
            image = images[row][col]
            heights[row] = max(heights[row], image.height)

    # Calculate the total width and height of the combined image.
    width = sum(widths)
    height = sum(heights)

    # Create a new image with the combined size and paste the images into it.
    combined_img = Image.new("RGB", (width, height), background)

    for row in range(nrows):
        for col, img in enumerate(images[row]):
            x = sum(widths[:col])
            y = sum(heights[:row])
            combined_img.paste(img, (x, y))

    # Resize the combined image if requested.
    if resolution is not None:
        combined_img = combined_img.resize(resolution, Resampling.LANCZOS)

    combined_img.save(out_path)


def image_tile_auto(
    paths: list[str | Path],
    out_path: str | Path,
    layout: tuple[int, int] | None = None,
    resolution: tuple[int, int] | None = None,
    background: str = "white",
):
    """
    Tile a set of images together & save the result.

    Unlike ..py:meth:`~danpy.image_tile.image_tile`, this function takes a flat list of paths.
    It will automatically determine the layout of the images that is closest to a square.
    You can override this by providing the ``layout`` argument.


    Args:
        paths: A flat list of paths to images.
        out_path: The path to save the combined image to.
        layout: The (optional) layout of the images.
            The product of the two numbers must be greater than or equal to the number of images.
        resolution: The (optional) resolution to save the image at.
            See ..py:meth:`~danpy.image_tile.image_tile` for more details.
        background: The background color to use for padding.
            See ..py:meth:`~danpy.image_tile.image_tile` for more details.
    """

    layout = layout or grid_layout_2d(len(paths))

    paths_ = []
    idx = 0
    for _row in range(layout[0]):
        paths_row = []
        for _col in range(layout[1]):
            if idx < len(paths):
                paths_row.append(paths[idx])
            idx += 1
        paths_.append(paths_row)

    image_tile(
        paths_,
        out_path,
        resolution=resolution,
        background=background,
    )


if __name__ == "__main__":
    import argparse as ap

    parser = ap.ArgumentParser()
    parser.add_argument("-i", "--in", dest="in_paths", nargs="+")
    parser.add_argument("-o", "--out", dest="out_path")
    parser.add_argument("-l", "--layout", nargs=2, type=int)
    parser.add_argument("-r", "--resolution", nargs=2, type=int)
    parser.add_argument("-b", "--bkg-color", default="white")
    args = parser.parse_args()

    image_tile_auto(
        args.in_paths,
        args.out_path,
        layout=args.layout,
        resolution=args.resolution,
        background=args.bkg_color,
    )
