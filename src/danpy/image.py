"""
Methods to add labels to images, and tile multiple images into one.

This module can be run as a command line script.

.. code-block:: bash

    # For example
    python -m danpy.image out.png label in.png -t "A Caption" -l "top"

    # See help for full usage
    python -m danpy.image --help
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from PIL.Image import Resampling
from typing import Sequence, Literal, get_args

from .grid_layout import grid_layout_2d

__all__ = [
    "ImageT",
    "to_image",
    "AbsoluteLocT",
    "to_canonical_absloc",
    "FontT",
    "to_font",
    "label_image",
    "image_tile",
    "image_tile_auto",
]

ImageT = Image.Image | str | Path


def to_image(image: ImageT) -> Image.Image:
    """
    Convert a path or image to a PIL image.

    Args:
        image: The image to convert. Can be a path or an already loaded PIL image.
    """
    if isinstance(image, (str, Path)):
        return Image.open(image)
    elif isinstance(image, Image.Image):
        return image
    else:
        raise TypeError(f"Unsupported type: {type(image)}")


AbsoluteLocT = Literal[
    "top left",
    "top center",
    "top right",
    "center left",
    "center center",
    "center right",
    "bottom left",
    "bottom center",
    "bottom right",
    # Aliases:
    "top",  # == "top center"
    "left"  # == "center left"
    "center",  # == "center center"
    "right",  # == "center right"
    "bottom",  # == "bottom center"
]


def to_canonical_absloc(loc: str) -> AbsoluteLocT:
    """
    Convert an absolute location to its canonical form.

    Dashes are replaced with spaces (e.g. "top-left" -> "top left"),
    and aliases (e.g. "top") are mapped to their canonical form (e.g. "top center").

    This function is idempotent.

    Args:
        loc: The location to convert.
    """

    loc = loc.lower().replace("-", " ")

    aliases: dict[str, AbsoluteLocT] = {
        "top": "top center",
        "left": "center left",
        "center": "center center",
        "right": "center right",
        "bottom": "bottom center",
    }

    if loc in aliases:
        return aliases[loc]

    if loc not in get_args(AbsoluteLocT):
        raise ValueError(f"Unknown value for `loc`: {loc}")

    return loc  # type: ignore[return-value]


FontT = str | Path | ImageFont.FreeTypeFont | None


def to_font(font: FontT, font_size: int) -> ImageFont.FreeTypeFont:
    """
    Convert a font name or path to a PIL :py:class:`~Pillow.ImageFont.FreeTypeFont`.

    .. note::
        If ``font`` is already a PIL font, ``font_size`` is ignored.

    Args:
        font: The font to convert. Can be a font name, path, an already loaded PIL font or ``None``.
            If ``None``, the default font 'Noto Sans' will be used.
        font_size: The size of the font to use.
    """
    font = font or "NotoSans-BoldItalic"
    if isinstance(font, (str, Path)):
        return ImageFont.truetype(font, font_size)
    elif isinstance(font, ImageFont.FreeTypeFont):
        return font
    else:
        raise TypeError(str(font))


def label_image(
    image: ImageT,
    text: str,
    loc: AbsoluteLocT,
    font: FontT = None,
    size: int | None = None,
    stroke: bool = True,
    invert: bool = False,
) -> Image.Image:
    """
    Add a label to an image.

    This method is designed to calculate things like a sensible font size, anchor point, etc.
    It is a relatively thin wrapper around :py:meth:`~PIL.ImageDraw.ImageDraw.text`,
    if you require more control you should use that directly.

    .. note::
        If ``image`` is a pre-loaded Pillow image it will be modified in place.

    Args:
        image: The image to label.
        text: The text of the label.
        location: The location of the label.
        font: The font to use. If None, defaults to 'Noto Sans'.
        size: The size of the font. If None, this will choose a sensible default.
        stroke: Whether to add an outline to the text or not.
        invert: By default this will draw white text with a black outline.
            If ``invert`` is True, the text will instead be black with a white outline.
    """

    image = to_image(image)
    size = size or (image.height // 15)
    font = to_font(font, size)
    loc = to_canonical_absloc(loc)

    # Get the text anchor to use for the label.
    anchor = {
        "top left": "lt",
        "top center": "mt",
        "top right": "rt",
        "center left": "lm",
        "center center": "mm",
        "center right": "rm",
        "bottom left": "lb",
        "bottom center": "mb",
        "bottom right": "rb",
    }[loc]

    # Get the text size to offset the anchor xy.
    l, t, r, b = font.getbbox("#")
    w = r - l
    h = b - t

    # The text xy position is based on the absolute location & an offset based on the font-size.
    text_xy = {
        "top left": (0 + w, 0 + h),
        "top center": (image.width // 2, 0 + h),
        "top right": (image.width - w, 0 + h),
        "center left": (0 + w, image.height // 2),
        "center center": (image.width // 2, image.height // 2),
        "center right": (image.width - w, image.height // 2),
        "bottom left": (0 + w, image.height - h),
        "bottom center": (image.width // 2, image.height - h),
        "bottom right": (image.width - w, image.height - h),
    }[loc]

    tcol = "white" if not invert else "black"
    scol = "black" if not invert else "white"

    stroke_kw = {"stroke_width": size // 15, "stroke_fill": scol} if stroke else {}

    draw = ImageDraw.Draw(image)
    draw.text(
        text_xy,
        text,
        tcol,
        font=font,
        anchor=anchor,
        **stroke_kw,
    )

    return image


def image_tile(
    in_paths: Sequence[Sequence[ImageT]],
    resolution: tuple[int, int] | None = None,
    background: str = "white",
) -> Image.Image:
    """
    Tile a set of images together.

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
            image = to_image(path)
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

    return combined_img


def image_tile_auto(
    paths: list[ImageT],
    layout: tuple[int, int] | None = None,
    resolution: tuple[int, int] | None = None,
    background: str = "white",
) -> Image.Image:
    """
    Tile a set of images together.

    Unlike :py:meth:`~danpy.image_tile.image_tile`, this function takes a flat list of paths.
    It will automatically determine the layout of the images that is closest to a square.
    You can override this by providing the ``layout`` argument, but the layout cannot be ragged.

    Args:
        paths: A flat list of paths to images.
        layout: The (optional) layout of the images.
            The product of the two numbers must be greater than or equal to the number of images.
        resolution: The (optional) resolution to save the image at.
        background: The background color to use for padding.
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

    return image_tile(
        paths_,
        resolution=resolution,
        background=background,
    )


if __name__ == "__main__":
    import argparse as ap

    parser = ap.ArgumentParser()
    parser.add_argument("out", dest="out_path")

    subparsers = parser.add_subparsers(dest="command")

    # tile images
    parser_tile = subparsers.add_parser("tile", help="Tile a set of images together.")
    parser_tile.add_argument("in_paths", nargs="+")
    parser_tile.add_argument("-l", "--layout", nargs=2, type=int)
    parser_tile.add_argument("-r", "--resolution", nargs=2, type=int)
    parser_tile.add_argument("-b", "--bkg-color", default="white")

    # label image
    # fmt: off
    parser_label = subparsers.add_parser("label", help="Label an image.")
    parser_label.add_argument("in_path")
    parser_label.add_argument("-t", "--text")
    parser_label.add_argument("-l", "--loc", default="top-left", type=to_canonical_absloc)
    parser_label.add_argument("-f", "--font")
    parser_label.add_argument("-s", "--size", type=int)
    parser_label.add_argument("--no-stroke", action="store_true")
    parser_label.add_argument("--invert", action="store_true", help="Draw black text with white outline.")
    # fmt: on

    args = parser.parse_args()

    if args.command == "tile":
        image = image_tile_auto(
            args.in_paths,
            layout=args.layout,
            resolution=args.resolution,
            background=args.bkg_color,
        )
    elif args.command == "label":
        image = label_image(
            args.in_path,
            args.text,
            loc=args.loc,
            font=args.font,
            size=args.size,
            stroke=not args.no_stroke,
            invert=args.invert,
        )
    else:
        parser.print_help()
        exit(1)

    image.save(args.out_path)
