from pathlib import Path

from xml.etree import ElementTree

from cellfinder_napari.utils import get_cell_arrays

from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation(tryfirst=True)
def napari_get_reader(path):
    """A basic implementation of the napari_get_reader hook specification.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    if isinstance(path, str) and is_cellfinder_xml(path):
        return reader_function


def is_cellfinder_xml(path):
    if Path(path).suffix == ".xml":
        try:
            with open(path, "r") as xml_file:
                root = ElementTree.parse(xml_file).getroot()
                if root.tag == "CellCounter_Marker_File":
                    return True
                else:
                    return False
        except:
            return False
    else:
        return False


def reader_function(path, point_size=15, opacity=0.6, symbol="ring"):
    """Take a path or list of paths and return a list of LayerData tuples.

    Readers are expected to return data as a list of tuples, where each tuple
    is (data, [add_kwargs, [layer_type]]), "add_kwargs" and "layer_type" are
    both optional.

    Parameters
    ----------
    path : str or list of str
        Path to file, or list of paths.

    Returns
    -------
    layer_data : list of tuples
        A list of LayerData tuples where each tuple in the list contains
        (data, metadata, layer_type), where data is a numpy array, metadata is
        a dict of keyword arguments for the corresponding viewer.add_* method
        in napari, and layer_type is a lower-case string naming the type of
        layer.
        Both "meta", and "layer_type" are optional. napari will default to
        layer_type=="image" if not provided
    """

    layers = []
    layers = load_cells(
        layers,
        path,
        point_size,
        opacity,
        symbol,
        "lightgoldenrodyellow",
        "lightskyblue",
    )
    return layers


def load_cells(
    layers,
    classified_cells_path,
    point_size,
    opacity,
    symbol,
    cell_color,
    non_cell_color,
):
    cells, non_cells = get_cell_arrays(str(classified_cells_path))

    layers.append(
        (
            non_cells,
            {
                "name": "Non cells",
                "size": point_size,
                "n_dimensional": True,
                "opacity": opacity,
                "symbol": symbol,
                "face_color": non_cell_color,
            },
            "points",
        )
    )
    layers.append(
        (
            cells,
            {
                "name": "Cells",
                "size": point_size,
                "n_dimensional": True,
                "opacity": opacity,
                "symbol": symbol,
                "face_color": cell_color,
            },
            "points",
        )
    )
    return layers
