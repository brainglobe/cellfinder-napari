import napari
from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation

from cellfinder_core.main import main as cellfinder_run

from .utils import cells_to_array


@magic_factory(
    voxel_size_z=dict(label="Voxel size (z)", step=0.1),
    voxel_size_y=dict(label="Voxel size (y)", step=0.1),
    voxel_size_x=dict(label="Voxel size (x)", step=0.1),
    call_button=True,
)
def cellfinder(
    signal: "napari.layers.Image",
    background: "napari.layers.Image",
    voxel_size_z: float = 5,
    voxel_size_y: float = 2,
    voxel_size_x: float = 2,
) -> napari.types.LayerDataTuple:

    voxel_sizes = (voxel_size_z, voxel_size_y, voxel_size_x)
    points = cellfinder_run(
        signal.data,
        background.data,
        voxel_sizes,
        start_plane=0,
        end_plane=-1,
        n_free_cpus=2,
    )

    points = cells_to_array(points)

    properties = {
        "name": "Points",
        "size": 15,
        "n_dimensional": True,
        "opacity": 0.6,
        "symbol": "ring",
        "face_color": "lightgoldenrodyellow",
    }
    return points, properties, "points"


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return cellfinder
