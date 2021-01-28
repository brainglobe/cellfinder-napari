try:
    from ._version import version as __version__
except ImportError:
    __version__ = "unknown"

from .cellfinder_napari import napari_experimental_provide_function

__all__ = ["napari_get_reader"]
