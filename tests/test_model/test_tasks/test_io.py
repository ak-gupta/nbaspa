"""Test loading data."""

from pathlib import Path

from nbaspa.model.tasks import LoadData

def test_load_model_data(data, tmpdir):
    """Test loading fake model data."""
    # First, write the data
    location = tmpdir.mkdir("data")
    Path(str(location), "2018-19", "model-data").mkdir(parents=True)
    for name, game in data.groupby("GAME_ID"):
        game.to_csv(Path(str(location), "2018-19", "model-data", f"data_{name}.csv"), sep="|")
    # Run the task and compare
    tsk = LoadData()
    output = tsk.run(data_dir=str(location))
    output.sort_values(by=["GAME_ID", "TIME"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    assert output.equals(data)
