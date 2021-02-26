import napari
from magicgui import magic_factory
from napari_plugin_engine import napari_hook_implementation

from cellfinder_core.main import main as cellfinder_run

from .utils import cells_to_array


@magic_factory(
    voxel_size_z=dict(label="Voxel size (z)", step=0.1),
    voxel_size_y=dict(label="Voxel size (y)", step=0.1),
    voxel_size_x=dict(label="Voxel size (x)", step=0.1),
    ball_xy_size=dict(label="Ball filter (xy)"),
    ball_z_size=dict(label="Ball filter (z)"),
    Soma_diameter=dict(step=0.1),
    Ball_overlap=dict(step=0.1),
    Filter_width=dict(step=0.1),
    Cell_spread=dict(step=0.1),
    Classification_batch_size=dict(max=4096),
    call_button=True,
)
def cellfinder(
    Signal_image: "napari.layers.Image",
    Background_image: "napari.layers.Image",
    voxel_size_z: float = 5,
    voxel_size_y: float = 2,
    voxel_size_x: float = 2,
    Soma_diameter: float = 16.0,
    ball_xy_size: int = 6,
    ball_z_size: int = 15,
    Ball_overlap: float = 0.6,
    Filter_width: float = 0.2,
    Threshold: int = 10,
    Cell_spread: float = 1.4,
    Max_cluster: int = 100000,
    Start_plane: int = 0,
    End_plane: int = 0,
    Classification_batch_size: int = 32,
    Number_of_free_cpus: int = 2,
) -> napari.types.LayerDataTuple:

    if End_plane == 0:
        End_plane = len(Signal_image.data)

    voxel_sizes = (voxel_size_z, voxel_size_y, voxel_size_x)
    points = cellfinder_run(
        Signal_image.data,
        Background_image.data,
        voxel_sizes,
        soma_diameter=Soma_diameter,
        ball_xy_size=ball_xy_size,
        ball_z_size=ball_z_size,
        start_plane=Start_plane,
        end_plane=End_plane,
        ball_overlap_fraction=Ball_overlap,
        log_sigma_size=Filter_width,
        n_sds_above_mean_thresh=Threshold,
        soma_spread_factor=Cell_spread,
        max_cluster_size=Max_cluster,
        n_free_cpus=Number_of_free_cpus,
        batch_size=Classification_batch_size,
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
