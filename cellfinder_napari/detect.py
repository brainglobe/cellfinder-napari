import napari
from pathlib import Path

from magicgui import magicgui
from typing import List
from pkg_resources import resource_filename

# TODO:
# how to store & fetch pre-trained models?

# TODO: params to add
NETWORK_VOXEL_SIZES = [5, 1, 1]
CUBE_WIDTH = 50
CUBE_HEIGHT = 20
CUBE_DEPTH = 20

# If using ROI, how much in z to analyse
MIN_PLANES_ANALYSE = 10

brainglobe_logo = resource_filename(
    "cellfinder_napari", "resources/brainglobe.png"
)


def detect():
    from math import ceil
    from napari.qt.threading import thread_worker
    from cellfinder_core.main import main as cellfinder_run
    from cellfinder_core.classify.cube_generator import get_cube_depth_min_max
    from .utils import cells_to_array

    @magicgui(
        logo=dict(
            widget_type="Label",
            label=f'<img src="{brainglobe_logo}" width="100">',
        ),
        header_label=dict(
            widget_type="Label",
            label="<h2>cellfinder</h2>",
        ),
        detection_label=dict(
            widget_type="Label",
            label="<h3>Cell detection</h3>",
        ),
        data_options=dict(
            widget_type="Label",
            label="<b>Data:</b>",
        ),
        detection_options=dict(
            widget_type="Label",
            label="<b>Detection:</b>",
        ),
        classification_options=dict(
            widget_type="Label",
            label="<b>Classification:</b>",
        ),
        misc_options=dict(
            widget_type="Label",
            label="<b>Misc:</b>",
        ),
        voxel_size_z=dict(label="Voxel size (z)", step=0.1),
        voxel_size_y=dict(label="Voxel size (y)", step=0.1),
        voxel_size_x=dict(label="Voxel size (x)", step=0.1),
        ball_xy_size=dict(label="Ball filter (xy)"),
        ball_z_size=dict(label="Ball filter (z)"),
        Soma_diameter=dict(step=0.1),
        Ball_overlap=dict(step=0.1),
        Filter_width=dict(step=0.1),
        Cell_spread=dict(step=0.1),
        Max_cluster=dict(min=0, max=10000000),
        Start_plane=dict(min=0, max=100000),
        End_plane=dict(min=0, max=100000),
        # Classification_batch_size=dict(max=4096),
        call_button=True,
        # widget_init=init,
        persist=True,
    )
    def widget(
        logo,
        header_label,
        detection_label,
        data_options,
        viewer: napari.Viewer,
        Signal_image: napari.layers.Image,
        Background_image: napari.layers.Image,
        voxel_size_z: float = 5,
        voxel_size_y: float = 2,
        voxel_size_x: float = 2,
        detection_options=None,
        Soma_diameter: float = 16.0,
        ball_xy_size: float = 6,
        ball_z_size: float = 15,
        Ball_overlap: float = 0.6,
        Filter_width: float = 0.2,
        Threshold: int = 10,
        Cell_spread: float = 1.4,
        Max_cluster: int = 100000,
        classification_options=None,
        Trained_model: Path = Path.home(),
        misc_options=None,
        Start_plane: int = 0,
        End_plane: int = 0,
        Number_of_free_cpus: int = 2,
        Analyse_field_of_view: bool = False,
    ) -> List[napari.types.LayerDataTuple]:
        """

        Parameters
        ----------
        voxel_size_z : float
            Size of your voxels in the axial dimension
        voxel_size_y : float
            Size of your voxels in x (left to right)
        voxel_size_z : float
            Size of your voxels in the y (top to bottom)
        Soma_diameter : float
            The expected in-plane soma diameter (microns)
        ball_xy_size : float
            Elliptical morphological in-plane filter size (microns)
        ball_z_size : float
            Elliptical morphological axial filter size (microns)
        Start_plane : int
            First plane to process (to process a subset of the data)
        End_plane : int
            Last plane to process (to process a subset of the data)
        Ball_overlap : float
            Fraction of the morphological filter needed to be filled
            to retain a voxel
        Filter_width : float
            Laplacian of Gaussian filter width (as a fraction of soma diameter)
        Threshold : int
            Cell intensity threshold (as a multiple of noise above the mean)
        Cell_spread : float
            Cell spread factor (for splitting up cell clusters)
        Max_cluster : int
            Largest putative cell cluster (in cubic um) where splitting
            should be attempted
        Number_of_free_cpus : int
            How many CPU cores to leave free
        Analyse_field_of_view : Only analyse the visible part of the image,
            with the minimum amount of 3D information
        """

        def add_layers(points):
            if Analyse_field_of_view:
                for point in points:
                    point.x = point.x + Signal_image.corner_pixels[0][2]
                    point.y = point.y + Signal_image.corner_pixels[0][1]

            points, rejected = cells_to_array(points)

            viewer.add_points(
                rejected,
                name="Rejected",
                size=15,
                n_dimensional=True,
                opacity=0.6,
                symbol="ring",
                face_color="lightskyblue",
                visible=False,
            )
            viewer.add_points(
                points,
                name="Detected",
                size=15,
                n_dimensional=True,
                opacity=0.6,
                symbol="ring",
                face_color="lightgoldenrodyellow",
            )

        @thread_worker
        def run(
            signal,
            background,
            voxel_sizes,
            Soma_diameter,
            ball_xy_size,
            ball_z_size,
            Start_plane,
            End_plane,
            Ball_overlap,
            Filter_width,
            Threshold,
            Cell_spread,
            Max_cluster,
            Trained_model,
            Number_of_free_cpus,
            # Classification_batch_size,
        ):

            points = cellfinder_run(
                signal,
                background,
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
                trained_model=Trained_model,
                n_free_cpus=Number_of_free_cpus,
                # batch_size=Classification_batch_size,
            )
            return points

        if End_plane == 0:
            End_plane = len(Signal_image.data)

        voxel_sizes = (voxel_size_z, voxel_size_y, voxel_size_x)
        if Trained_model == Path.home():
            Trained_model = None

        if Analyse_field_of_view:
            index = list(
                slice(int(i[0]), int(i[1]))
                for i in Signal_image.corner_pixels.T
            )
            index[0] = slice(0, len(Signal_image.data))

            signal_data = Signal_image.data[tuple(index)]
            background_data = Background_image.data[tuple(index)]

            current_plane = viewer.dims.current_step[0]

            # so a reasonable number of cells in the plane are detected
            planes_needed = MIN_PLANES_ANALYSE + int(
                ceil((CUBE_DEPTH * NETWORK_VOXEL_SIZES[0]) / voxel_size_z)
            )

            Start_plane, End_plane = get_cube_depth_min_max(
                current_plane, planes_needed
            )
            Start_plane = max(0, Start_plane)
            End_plane = min(len(Signal_image.data), End_plane)

        else:
            signal_data = Signal_image.data
            background_data = Background_image.data

        worker = run(
            signal_data,
            background_data,
            voxel_sizes,
            Soma_diameter,
            ball_xy_size,
            ball_z_size,
            Start_plane,
            End_plane,
            Ball_overlap,
            Filter_width,
            Threshold,
            Cell_spread,
            Max_cluster,
            Trained_model,
            Number_of_free_cpus,
            # Classification_batch_size,
        )
        worker.returned.connect(add_layers)
        worker.start()

    return widget
