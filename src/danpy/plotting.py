import logging

from pathlib import Path
from typing import Literal, Sequence

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

from matplotlib.axes import Axes
from matplotlib.colors import LinearSegmentedColormap, Colormap
from matplotlib.figure import Figure

logger = logging.getLogger(__name__)

try:
    from IPython.display import Image, SVG, display
except ImportError:
    logger.warning("Error importing IPython. Some functions will not work.")


__all__ = [
    "annotate",
    "arrow",
    "save_show",
    "set_maths_style_axes",
    "style",
    "make_cmap",
    "OrangeBlue",
    "OrangeBlue_r",
    "InkyBlueRed",
    "InkyBlueRed_r",
]


def style():
    """
    Setup the rcParams.
    """

    mpl.rcParams["axes.prop_cycle"] = mpl.cycler(  # type: ignore
        color=[
            "#683b86",
            "#c95f76",
            "#fdb73b",
            "#008000",
        ]
    )


def save_show(fname: str | Path, *args, fig: Figure | None = None, **kwargs):
    """
    Save a figure using `Figure.savefig` then display the result.

    This is needed because `plt.show` uses a different engine than `plt.savefig` and so layouts can differ.
    This is especially pronouced when using things like `subplots_adjust`.
    """
    fig = fig or plt.gcf()
    fname = str(fname)
    fig.savefig(fname, *args, **kwargs)
    fig.clear()
    img = SVG(fname) if fname.endswith(".svg") else Image(fname)
    display(img)


def set_maths_style_axes(ax: Axes | None = None, below: bool = True):
    """
    Set the axes to be "maths" style.
    See: https://matplotlib.org/stable/gallery/spines/centered_spines_with_arrows.html
    """
    ax = ax or plt.gca()
    if below:
        ax.set_axisbelow(True)
        ax.set_zorder(-1)
    ax.spines[["left", "bottom"]].set_position(("data", 0))
    ax.spines[["right", "top"]].set_visible(False)
    ax.plot(1, 0, ">k", transform=ax.get_yaxis_transform(), clip_on=False)
    ax.plot(0, 1, "^k", transform=ax.get_xaxis_transform(), clip_on=False)


# fmt: off
LocT = Literal[
    "above",        # N
    "above right",  # NE
    "right",        # E
    "below right",  # SE
    "below",        # S
    "below left",   # SW
    "left",         # W
    "above left",   # NW
    "center",
]
# fmt: on


def annotate(
    text: str,
    xytext: Sequence[float],
    *args,
    loc: LocT = "center",
    pad: float = 0.3,
    ax: Axes | None = None,
    **kwargs,
):
    """
    Annotate a point with text but make it easy to locate the text relative to the annotated point.

    Extra arguments are passed through to `Axes.annotate`.
    """
    ax = ax or plt.gca()

    forbidden_args = ["textcoords", "arrowprops", "xy"]
    for arg in forbidden_args:
        if kwargs.pop(arg, None):
            raise ValueError(f"Cannot specify `{arg}`!")

    match loc:
        case "above":
            xyt = (0, pad)
            ha = "center"
            va = "bottom"
        case "above right":
            xyt = (pad, pad)
            ha = "left"
            va = "bottom"
        case "right":
            xyt = (pad, 0)
            ha = "left"
            va = "center"
        case "below right":
            xyt = (pad, -pad)
            ha = "left"
            va = "top"
        case "below":
            xyt = (0, -pad)
            ha = "center"
            va = "top"
        case "below left":
            xyt = (-pad, -pad)
            ha = "right"
            va = "top"
        case "left":
            xyt = (-pad, 0)
            ha = "right"
            va = "center"
        case "above left":
            xyt = (-pad, pad)
            ha = "right"
            va = "bottom"
        case "center":
            xyt = (0, 0)
            ha = "center"
            va = "center"
        case _:
            raise ValueError(f"Unknown value for `loc`: {loc}")

    ax.annotate(
        text,
        xytext,
        *args,
        **kwargs,
        xytext=xyt,
        textcoords="offset fontsize",
        horizontalalignment=ha,
        verticalalignment=va,
    )


def arrow(
    xyfrom: Sequence[float],
    xyto: Sequence[float],
    ax: Axes | None = None,
    **kwargs,
):
    """
    A simple "draw an arrow" function.
    Unlike the Axes.arrow function this scales the head correctly by using Axes.annotate under the hood.
    """

    ax = ax or plt.gca()

    forbidden_args = ["textcoords", "xy", "xytext"]
    for arg in forbidden_args:
        if kwargs.pop(arg, None):
            raise ValueError(f"Cannot specify `{arg}`!")

    arrowprops = kwargs.pop("arrowprops", {"arrowstyle": "->"})
    ax.annotate("", xyto, xyfrom, arrowprops=arrowprops)


def make_cmap(name: str, colors: list) -> LinearSegmentedColormap:
    """
    Make a custom colormap from a list of colors which are evenly spaced.
    """
    nodes = np.linspace(0, 1, len(colors))
    return LinearSegmentedColormap.from_list(name, list(zip(nodes, colors)))


_colors = [
    "#ffe359",
    "#ff8000",
    "#734c26",
    "#17151a",
    "#17151a",
    "#17151a",
    "#265773",
    "#0f82b8",
    "#8fceff",
]

_nodes = [0.0, 0.16666667, 0.33333333, 0.49, 0.5, 0.51, 0.66666667, 0.83333333, 1.0]

OrangeBlue = LinearSegmentedColormap.from_list("OrangeBlue", list(zip(_nodes, _colors)))
OrangeBlue_r = LinearSegmentedColormap.from_list("OrangeBlue_r", list(zip(_nodes, _colors[::-1])))

_colors = [
    "#10396a",
    "#1968c2",
    "#198fe3",
    "#19cdff",
    "#ffffff",
    "#ffffff",
    "#ffffff",
    "#ffaf18",
    "#f3681a",
    "#e32b2b",
    "#890000",
]

_nodes = [0.0, 0.125, 0.25, 0.375, 0.49, 0.5, 0.51, 0.625, 0.75, 0.875, 1.0]

InkyBlueRed = LinearSegmentedColormap.from_list("InkyBlueRed", list(zip(_nodes, _colors)))
InkyBlueRed_r = LinearSegmentedColormap.from_list("InkyBlueRed_r", list(zip(_nodes, _colors[::-1])))

# Register our custom colourmaps.
mpl.colormaps.register(cmap=OrangeBlue)
mpl.colormaps.register(cmap=OrangeBlue_r)
mpl.colormaps.register(cmap=OrangeBlue, name="BlueOrange_r")
mpl.colormaps.register(cmap=OrangeBlue_r, name="BlueOrange")
mpl.colormaps.register(cmap=InkyBlueRed)
mpl.colormaps.register(cmap=InkyBlueRed_r)
mpl.colormaps.register(cmap=InkyBlueRed, name="InkyRedBlue_r")
mpl.colormaps.register(cmap=InkyBlueRed_r, name="InkyRedBlue")
