"""Test loading data."""

from pathlib import Path

import cloudpickle
from lifelines import CoxTimeVaryingFitter
from sklearn.isotonic import IsotonicRegression

from nbaspa.model.tasks import LoadData, LoadModel

def test_load_model_data(data, gamelocation):
    """Test loading fake model data."""
    # Run the task and compare
    tsk = LoadData()
    output = tsk.run(data_dir=gamelocation)
    output.sort_values(by=["GAME_ID", "TIME"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    assert output.equals(data)

def test_load_model(tmpdir):
    """Test writing and reading a model."""
    model = CoxTimeVaryingFitter(penalizer=1.0)
    location = tmpdir.mkdir("fake-model")
    with open(Path(str(location), "mymodel.pkl"), "wb") as outfile:
        cloudpickle.dump(model, outfile)
    calibrator = IsotonicRegression(out_of_bounds="clip")
    with open(Path(str(location), "calibrator.pkl"), "wb") as outfile:
        cloudpickle.dump(calibrator, outfile)
    
    tsk = LoadModel()
    output = tsk.run(filepath=Path(str(location), "mymodel.pkl"))

    assert isinstance(output[0], CoxTimeVaryingFitter)
    assert output[0].penalizer == 1.0
    assert isinstance(output[1], IsotonicRegression)
    assert output[1].out_of_bounds == "clip"