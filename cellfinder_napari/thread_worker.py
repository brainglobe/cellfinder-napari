from typing import Generator

from cellfinder_core.main import MainRunner
from napari.qt.threading import thread_worker

from cellfinder_napari.input_containers import (
    ClassificationInputs,
    DataInputs,
    DetectionInputs,
    MiscInputs,
)


@thread_worker
def run(
    data_inputs: DataInputs,
    detection_inputs: DetectionInputs,
    classification_inputs: ClassificationInputs,
    misc_inputs: MiscInputs,
) -> Generator:
    """
    Runs cellfinder in a separate thread, to prevent GUI blocking.

    To give user feedback this function should yield a dictionary of attributes
    to set on a `magicgui.widgets.ProgressBar`, e.g. to set the min and max
    of the progress bar to 0, 10:

        >>> yield {'min': 0, 'max': 10}
    """

    runner = MainRunner()
    runner.run(
        **data_inputs.as_core_arguments(),
        **detection_inputs.as_core_arguments(),
        **classification_inputs.as_core_arguments(),
        **misc_inputs.as_core_arguments(),
    )

    yield {"label": "Detecting"}
    yield {"max": runner.detect_runner.nplanes}
    planes_done = 0
    while planes_done < runner.detect_runner.nplanes:
        runner.detect_runner.planes_done_queue.get(block=True)
        planes_done += 1
        yield {"value": planes_done}

    runner.detect_runner.join()
    # Finished detection
    points = runner.join()
    return points
