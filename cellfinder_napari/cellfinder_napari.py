from napari_plugin_engine import napari_hook_implementation
from cellfinder_core.main import main as cellfinder_run

from magicgui import magicgui

from .utils import cells_to_array


def widget_wrapper():
    @magicgui(
        signal=dict(label="Signal image"),
        background=dict(label="Background image"),
        voxel_size_z=dict(
            widget_type="FloatSpinBox",
            label="Voxel size (z)",
            min=0.0,
            max=100.0,
            step=0.1,
            value=5.0,
        ),
        voxel_size_y=dict(
            widget_type="FloatSpinBox",
            label="Voxel size (z)",
            min=0.0,
            max=100.0,
            step=0.1,
            value=2.0,
        ),
        voxel_size_x=dict(
            widget_type="FloatSpinBox",
            label="Voxel size (z)",
            min=0.0,
            max=100.0,
            step=0.1,
            value=2.0,
        ),
        call_button=True,
    )
    def widget(
        signal: "napari.layers.Image",
        background: "napari.layers.Image",
        voxel_size_z: float,
        voxel_size_y: float,
        voxel_size_x: float,
    ) -> "napari.types.LayerDataTuple":

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

    return widget


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return widget_wrapper, {"name": "cellfinder"}
