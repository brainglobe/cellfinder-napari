from cellfinder_napari.train import train
from cellfinder_napari.detect import detect
from napari_plugin_engine import napari_hook_implementation


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    return [
        (detect, {"name": "Cell detection"}),
        (train, {"name": "Train network"}),
    ]
