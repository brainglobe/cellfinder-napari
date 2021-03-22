import numpy as np
from qtpy import QtCore

from qtpy.QtWidgets import (
    QPushButton,
    QLabel,
    QComboBox,
    QWidget,
    QFileDialog,
    QGridLayout,
    QGroupBox,
)
from imlib.cells.cells import Cell


from .utils import add_combobox, add_button

import napari

# Constants used throughout
WINDOW_HEIGHT = 750
WINDOW_WIDTH = 1500
COLUMN_WIDTH = 150


class CurationWidget(QWidget):
    def __init__(
        self,
        viewer: napari.viewer.Viewer,
    ):
        super(CurationWidget, self).__init__()

        self.viewer = viewer

        self.image_layer_names = self._get_layer_names()

        self.background_layer = None

        self.signal_layer = None

        self.output_directory = None

        self.setup_main_layout()

        @self.viewer.layers.events.connect
        def update_layer_list(v):
            self.image_layer_names = self._get_layer_names()
            self.signal_image_choice.clear()
            self._update_combobox_options(
                self.signal_image_choice, self.image_layer_names
            )
            self._update_combobox_options(
                self.background_image_choice, self.image_layer_names
            )

    @staticmethod
    def _update_combobox_options(combobox, options_list):
        combobox.clear()
        combobox.addItems(options_list)

    def _get_layer_names(self, layer_type="image"):
        return [
            layer.name
            for layer in self.viewer.layers
            if layer._type_string == layer_type
        ]

    def setup_main_layout(self):
        """
        Construct main layout of widget
        """
        self.layout = QGridLayout()
        self.layout.setContentsMargins(10, 10, 10, 10)
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setSpacing(4)

        self.add_loading_panel(1)

        self.status_label = QLabel()
        self.status_label.setText("Ready")
        self.layout.addWidget(self.status_label, 7, 0)

        self.setLayout(self.layout)

    def add_loading_panel(self, row, column=0):

        self.load_data_panel = QGroupBox("Load data")
        self.load_data_layout = QGridLayout()
        self.load_data_layout.setSpacing(15)
        self.load_data_layout.setContentsMargins(10, 10, 10, 10)
        self.load_data_layout.setAlignment(QtCore.Qt.AlignBottom)

        self.signal_image_choice, _ = add_combobox(
            self.load_data_layout,
            "Signal image",
            self.image_layer_names,
            1,
            callback=self.get_signal_image,
        )
        self.background_image_choice, _ = add_combobox(
            self.load_data_layout,
            "Background image",
            self.image_layer_names,
            2,
            callback=self.get_background_image,
        )

        self.add_cells_button = add_button(
            "Add cell count",
            self.load_data_layout,
            self.add_cell_count,
            3,
            0,
            minimum_width=COLUMN_WIDTH,
        )

        self.load_data_layout.setColumnMinimumWidth(0, COLUMN_WIDTH)
        self.load_data_panel.setLayout(self.load_data_layout)
        self.load_data_panel.setVisible(True)
        self.layout.addWidget(self.load_data_panel, row, column, 1, 1)

    def add_cell_count(self):
        self.cell_layer = self.viewer.add_points(
            np.empty((0, 3)),
            symbol="ring",
            n_dimensional=True,
            size=10,
            opacity=0.6,
            face_color="lightgoldenrodyellow",
            name="cells",
            metadata=dict(point_type=Cell.UNKNOWN),
        )

    def get_signal_image(self):
        if self.signal_image_choice.currentText() != "":
            self.signal_layer = self.viewer.layers[
                self.signal_image_choice.currentText()
            ]

    def get_background_image(self):
        if self.background_image_choice.currentText() != "":
            self.background_layer = self.viewer.layers[
                self.background_image_choice.currentText()
            ]
