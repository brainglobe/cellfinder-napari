from napari_plugin_engine import napari_hook_implementation

from typing import List, Tuple, Dict, Any
from imlib.IO.cells import save_cells
from cellfinder_napari.utils import convert_layer_to_cells


@napari_hook_implementation
def napari_get_writer(path: str):
    """Returns a h5 Napari project writer if the path file format is h5.
    Parameters
    ----------
    path: str
        Napari h5 project file
    Returns
    -------
    Callable or None
        Napari h5 project file writer if the path file extension is correct
    """
    if isinstance(path, str) and path.endswith(".xml"):
        return write_points_to_xml
    else:
        return None


def write_points_to_xml(
    path: str, layer_data: List[Tuple[Any, Dict, str]]
) -> str:
    """Returns a list of LayerData tuples from the project file required by Napari.
    Parameters
    ----------
    path: str
        xml output directory
    layer_data: list[tuple[numpy array, dict, str]]
        List of LayerData tuples produced by Napari IO writer
    Returns
    -------
    str
        Final output file path
    """
    cells_to_save = []
    for layer in layer_data:
        data, state, type = layer
        if state["name"] == "Cells":
            cells_to_save.extend(convert_layer_to_cells(data))
        if state["name"] == "Non cells":
            cells_to_save.extend(convert_layer_to_cells(data, cells=False))

    if cells_to_save:
        save_cells(cells_to_save, path)

    return path
