from warnings import warn

warn(
    f"cellfinder-napari has merged with it's backend code and is now available as a combined package. To remain up to date, please install cellfinder: https://github.com/brainglobe/cellfinder",
    DeprecationWarning,
)

__version__ = "0.0.20"
__author__ = "Adam Tyson"
__license__ = "GPL-3.0"
