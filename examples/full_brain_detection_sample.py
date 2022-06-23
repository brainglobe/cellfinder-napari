"""
Cell transformation example
===========================
This example loads the data needed to run a transformation of detected cells
from a source brain space to the registered brain space.

The following layers are loaded:
- A low resolution full brain image, taken from the ``brainreg-napari`` sample data.
- The output from registering this data using ``brainreg-napari``. This data must
  be present on the local filesystem at the path specified by the ``brainreg_output_folder``
  below.
- The detected cells in this data, saved as ``cells.xml`` in the same directory. For this
  dataset all the detected cells are marked as non-cells, but this is sufficient to
  demonstrate the transformation widget.

When the napari viewer opens, click "Run" in the widget and a new layer called "Transformed cells"
should appear in the viewer.
"""
from pathlib import Path

import napari
from brainglobe_napari_io.cellfinder.reader_xml import xml_reader
from brainreg_napari.register import add_registered_image_layers
from brainreg_napari.sample_data import load_test_brain
from napari.layers import Layer

brainreg_output_folder = Path.home() / "brainreg-napari-output"

# Create napari viewer and open cell detection widget
viewer = napari.Viewer()

# Add low resultion full brain data
layer_data = load_test_brain()[0]
background_layer = viewer.add_layer(Layer.create(*layer_data))
# Add brain registration outuput
add_registered_image_layers(
    viewer, registration_directory=brainreg_output_folder
)
# Add cell layers
cell_layers = xml_reader(brainreg_output_folder / "cells.xml")
for layer in cell_layers:
    viewer.add_layer(napari.layers.Layer.create(*layer))


# Open cell transformation widget
viewer.window.add_plugin_dock_widget(
    plugin_name="cellfinder-napari", widget_name="Transform"
)

if __name__ == "__main__":
    # The napari event loop needs to be run under here to allow the window
    # to be spawned from a Python script
    napari.run()
