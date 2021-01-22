"""
This module is an example of a barebones function widget plugin for napari
It implements the ``napari_experimental_provide_function_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html
Replace code below according to your needs.
"""
from typing import TYPE_CHECKING
from magicgui import magicgui
import enum
import numpy as np
from napari_plugin_engine import napari_hook_implementation
from napari.types import ImageData, LayerDataTuple, PointsData
from cellfinder_core.main import main as cellfinder_run

import logging
import os
import yaml

import pandas as pd

from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element as EtElement

from imlib.cells.cells import (
    Cell,
    UntypedCell,
    pos_from_file_name,
    MissingCellsError,
)
from imlib.general.system import replace_extension

def cells_df_as_np(cells_df, new_order=[2, 1, 0], type_column="type"):
    cells_df = cells_df.drop(columns=[type_column])
    cells = cells_df[cells_df.columns[new_order]]
    cells = cells.to_numpy()
    return cells


@napari_hook_implementation
def napari_experimental_provide_function_widget():
    return detect, {'call_button':'Run'}


def detect(signal: ImageData,  background: ImageData,
           start_plane: int = 600, end_plane: int = 650,
           z_voxel: float=5, y_voxel: float = 2,
           x_voxel: float = 2) -> LayerDataTuple:

    voxel_sizes = (z_voxel, y_voxel, x_voxel)

    points = cellfinder_run(
        signal,
        background,
        voxel_sizes,
        start_plane=start_plane,
        end_plane=end_plane,
        n_free_cpus=6
    )
    df = pd.DataFrame([c.to_dict() for c in points])
    cells = df[df["type"] == Cell.CELL]

    points = cells_df_as_np(cells)

    properties = {
        "name": "Points",
        "size": 15,
        "n_dimensional": True,
        "opacity": 0.6,
        "symbol": "ring",
        "face_color": "lightgoldenrodyellow",
    }
    return points, properties, "points"