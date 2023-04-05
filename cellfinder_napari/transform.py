"""
Widget to allow transformation of detected cells from the source space to a
registered atlas space.
"""
from pathlib import Path
from typing import Optional

import bg_space as bgs
from cellfinder.analyse.analyse import transform_points_to_atlas_space
from magicgui import magicgui
from napari.layers import Image, Labels, Points
from napari.utils.notifications import show_info
from napari.viewer import current_viewer

# An internal flag to allow the deformation field files to be
# set in the tests, instead of being read in from a metadata file.
#
# Required because the deformation field files do not have a fixed
# absolute path when testing across different machines.
_DEFORMATION_FIELD_DIRECTORY: Optional[Path] = None


@magicgui(call_button=True)
def transform(
    cells: Points,
    source_brain: Image,
    registered_brain: Labels,
) -> None:
    if any(arg is None for arg in [cells, source_brain, registered_brain]):
        show_info("At least one input not selected")
        return None

    # Check that registered image has the metadata we need
    for req_key in [
        "data_orientation",
        "registration_output_folder",
        "voxel_sizes",
        "atlas_class",
    ]:
        if req_key not in registered_brain.metadata:
            show_info(
                "Required metadata not present in registered image. "
                "Make sure you have selected an image previously "
                "registered by brainreg."
            )
            return None

    reg_meta = registered_brain.metadata

    source_space = bgs.AnatomicalSpace(
        reg_meta["data_orientation"],
        shape=source_brain.data.shape,
        resolution=source_brain.scale,
    )

    downsampled_space = bgs.AnatomicalSpace(
        reg_meta["orientation"],
        shape=registered_brain.data.shape,
        resolution=registered_brain.scale,
    )

    if _DEFORMATION_FIELD_DIRECTORY is None:
        reg_dir = Path(reg_meta["registration_output_folder"])
    else:
        reg_dir = _DEFORMATION_FIELD_DIRECTORY
    deformation_field_paths = [
        str(reg_dir / f"deformation_field_{i}.tiff") for i in [0, 1, 2]
    ]

    transformed_cells = transform_points_to_atlas_space(
        cells.data,
        source_space,
        reg_meta["atlas_class"],
        deformation_field_paths,
        downsampled_space,
    )

    cell_properties = cells.as_layer_data_tuple()[1]
    cell_properties["scale"] = registered_brain.scale
    cell_properties["face_color"] = "red"
    cell_properties["name"] = "Transformed cells"

    current_viewer().add_layer(Points(transformed_cells, **cell_properties))


def get_transform_widget():
    return transform
