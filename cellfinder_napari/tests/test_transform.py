from pathlib import Path

import numpy as np
from brainreg_napari.register import add_registered_image_layers
from brainreg_napari.sample_data import load_test_brain
from napari.layers import Layer, Points

from cellfinder_napari.transform import transform


def test_transform(make_napari_viewer):
    # Create cells
    cells_layer = Points(np.atleast_2d([0, 0, 0]))

    # Create brain data
    brain_layer_data = load_test_brain()[0]
    brain_layer = Layer.create(*brain_layer_data)

    viewer = make_napari_viewer()

    labels_layer, boundaries_layer = add_registered_image_layers(
        viewer, registration_directory=Path.home() / "brainreg-napari-output"
    )
    viewer.add_layer(brain_layer)
    viewer.add_layer(cells_layer)

    _, plugin = viewer.window.add_plugin_dock_widget(
        plugin_name="cellfinder-napari", widget_name="Transform"
    )

    plugin.cells.value = cells_layer
    plugin.source_brain.value = brain_layer
    plugin.registered_brain.value = labels_layer

    assert len(viewer.layers) == 4

    # Run cell transformation
    plugin()

    # Check the new layer that should have been added
    assert len(viewer.layers) == 5
    new_layer = viewer.layers[-1]
    assert isinstance(new_layer, Points)
    # This value has not been checked for correctness, but has been put here to
    # catch any future changes in the cell transformation code
    np.testing.assert_equal(new_layer.data, [[19, -1, 4]])
