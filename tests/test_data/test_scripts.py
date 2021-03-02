"""Test the CLI for data download and cleaning."""

from datetime import datetime
from pathlib import Path
from unittest.mock import patch

from click.testing import CliRunner

from nbaspa.data.endpoints.parameters import SEASONS
from nbaspa.data.scripts.clean import model, rating

def test_model_cli(data_dir, tmpdir):
    """Test running the model data cleaning pipeline."""
    location = tmpdir.mkdir("model-data")
    runner = CliRunner()
    with patch.dict(
        SEASONS,
        {
            "2018-19": {
                "START": datetime(2018, 12, 25),
                "END": datetime(2018, 12, 26)
            }
        }
    ):
        result = runner.invoke(
            model,
            [
                f"--data-dir={str(data_dir)}",
                f"--output-dir={str(location)}",
                "--season=2018-19"
            ]
        )
    assert result.exit_code == 0
    assert Path(
        str(location),
        "2018-19",
        "model-data",
        "data_00218DUMMY1.csv"
    ).is_file()
    assert Path(
        str(location),
        "2018-19",
        "model-data",
        "data_00218DUMMY2.csv"
    ).is_file()

def test_rating_cli(data_dir, tmpdir):
    """Test running the rating data cleaning pipeline."""
    location = tmpdir.mkdir("rating-data")
    runner = CliRunner()
    with patch.dict(
        SEASONS,
        {
            "2018-19": {
                "START": datetime(2018, 12, 25),
                "END": datetime(2018, 12, 26)
            }
        }
    ):
        result = runner.invoke(
            rating,
            [
                f"--data-dir={str(data_dir)}",
                f"--output-dir={str(location)}",
                "--season=2018-19"
            ]
        )
    
    assert result.exit_code == 0
    assert Path(
        str(location),
        "2018-19",
        "rating-data",
        "data_00218DUMMY1.csv"
    ).is_file()
    assert Path(
        str(location),
        "2018-19",
        "rating-data",
        "data_00218DUMMY2.csv"
    ).is_file()
