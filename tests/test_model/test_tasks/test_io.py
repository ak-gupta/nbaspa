"""Test loading data."""

from pathlib import Path

import cloudpickle
from lifelines import CoxTimeVaryingFitter

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
    
    tsk = LoadModel()
    output = tsk.run(filepath=Path(str(location), "mymodel.pkl"))

    assert isinstance(output, CoxTimeVaryingFitter)
    assert output.penalizer == 1.0