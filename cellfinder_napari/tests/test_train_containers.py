from inspect import signature
from typing import List

import pytest
from cellfinder_core.train.train_yml import run

from cellfinder_napari.input_container import InputContainer
from cellfinder_napari.train.train_containers import (
    MiscTrainingInputs,
    OptionalNetworkInputs,
    OptionalTrainingInputs,
    TrainingDataInputs,
)


@pytest.mark.parametrize(
    argnames="input_container",
    argvalues=[
        MiscTrainingInputs(),
        OptionalNetworkInputs(),
        OptionalTrainingInputs(),
        TrainingDataInputs(),
    ],
)
def test_core_args_passed(input_container):
    """
    Check that any keyword argument that napari passes
    to the training backend actually is also expected by the backend
    """
    backend_signature = signature(run)
    expected_kwargs_list = list(backend_signature.parameters.keys())
    actual_kwargs_list = list(input_container.as_core_arguments().keys())
    for key in actual_kwargs_list:
        assert key in expected_kwargs_list