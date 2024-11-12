"""
MLOps Pipeline
==============

This module initializs the MLOps pipeline

.. module:: pipeline
   :synopsis: MLOps pipeline
"""

from importlib.metadata import version

__version__ = version("pipeline")

import io
from functools import wraps

import matplotlib.pyplot as plt
import seaborn as sns
from loguru import logger
from matplotlib.colors import LinearSegmentedColormap

from .stages.base import PipelineStage

# DEFAULT COLOR PALETTE
COLORS = {
    "primary": "#4361EE",    # Vibrant blue
    "secondary": "#F72585",  # Vivid pink
    "tertiary": "#4CC9F0",   # Light blue
    "success": "#2EC4B6",    # Teal
    "warning": "#FF9F1C",    # Orange
    "danger": "#E71D36",     # Red
    "info": "#7209B7",       # Purple
    "gray": "#2B2D42",       # Dark gray
}  # fmt: off

#: List of colors for sequential colormap, from light to dark
SEQUENTIAL_COLORS = ["#F8F9FA", "#4361EE"]

#: Custom colormap for visualization consistency
CUSTOM_CMAP = LinearSegmentedColormap.from_list("custom", SEQUENTIAL_COLORS)

# Set global plotting style
plt.style.use("seaborn-v0_8-white")

#: Global matplotlib parameters for consistent visualization
PLOT_PARAMS = {
    # Figure settings
    "figure.dpi": 300,
    "savefig.dpi": 300,
    "figure.figsize": [10, 6.18],
    "figure.facecolor": "white",
    "figure.autolayout": True,
    # Font settings
    "font.family": ["Inter", "Roboto", "Arial", "sans-serif"],
    "font.weight": "regular",
    "axes.labelsize": 14,
    "axes.titlesize": 16,
    "axes.labelweight": "medium",
    "axes.titleweight": "bold",
    "xtick.labelsize": 12,
    "ytick.labelsize": 12,
    # Clean spines
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.spines.left": True,
    "axes.spines.bottom": True,
    "axes.linewidth": 1.2,
    # Grid settings
    "axes.axisbelow": True,
    "grid.linestyle": "-",
    "grid.alpha": 0.1,
    "grid.color": COLORS["gray"],
    # Legend settings
    "legend.fontsize": 12,
    "legend.frameon": False,
    "legend.borderaxespad": 0.5,
    "legend.markerscale": 1.5,
    # Color cycle
    "axes.prop_cycle": plt.cycler(
        color=[
            COLORS["primary"],
            COLORS["secondary"],
            COLORS["tertiary"],
            COLORS["success"],
            COLORS["warning"],
            COLORS["danger"],
            COLORS["info"],
        ]
    ),
}

plt.rcParams.update(PLOT_PARAMS)

# Set seaborn theme
sns.set_theme(style="white", context="paper", font_scale=1.6)


def plot_decorator(func):
    """Decorator for managing plot generation and buffer handling.

    This decorator wraps plotting functions to handle figure creation,
    buffer management, and error handling consistently.

    :param func: Function that creates a plot
    :type func: callable

    :returns: BytesIO buffer containing the plot image
    :rtype: io.BytesIO

    :raises Exception: Any exception that occurs during plot generation

    Example:
        >>> @plot_decorator
        ... def plot_data(data, buffer):
        ...     plt.plot(data)
        ...     plt.title("My Plot")

    Note:
        The decorated function should accept a `buffer` parameter
        and create the plot using matplotlib commands.
    """

    @wraps(func)
    def wrapper(*args, **kwargs) -> io.BytesIO:
        buffer = io.BytesIO()
        try:
            plt.figure()
            func(*args, **kwargs, buffer=buffer)
            plt.tight_layout()
            plt.savefig(buffer, format="png", bbox_inches="tight", facecolor="white")
            buffer.seek(0)
            return buffer
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise
        finally:
            plt.close()
            if "buffer" not in kwargs:
                buffer.close()

    return wrapper


__all__ = [
    "PipelineStage",
    "COLORS",
    "CUSTOM_CMAP",
    "plot_decorator",
]
