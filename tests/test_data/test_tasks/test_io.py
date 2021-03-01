"""Test the loader methods."""

from datetime import datetime
from pathlib import Path

from nbaspa.data.tasks import (
    GenericLoader,
    PlayByPlayLoader,
    WinProbabilityLoader,
    GameLogLoader
)

def test_load_scoreboard(data_dir, header, last_meeting):
    """Test loading scoreboard data."""
    for game, gamedate in [
        ("00218DUMMY1", datetime(2018, 12, 25)),
        ("00218DUMMY2", datetime(2018, 12, 26))
    ]:
        loader = GenericLoader(loader="Scoreboard")
        output = loader.run(
            output_dir=data_dir / Path("2018-19"),
            GameDate=gamedate.strftime("%m/%d/%Y")
        )

        assert output["GameHeader"].equals(
            header[
                header["GAME_DATE_EST"] == gamedate.strftime("%Y-%m-%dT%H:%M:%S")
            ].reset_index(drop=True)
        )
        assert output["LastMeeting"].equals(
            last_meeting[last_meeting["GAME_ID"] == game].reset_index(drop=True)
        )

def test_load_pbp(data_dir, header, pbp):
    """Test loading play-by-play data."""
    loader = PlayByPlayLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )

    assert output.equals(pbp)

def test_win_probability_loader(data_dir, header, win_prob):
    """Test loading NBA win probability data."""
    loader = WinProbabilityLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )
    assert output.equals(win_prob)

def test_gamelog_loader(data_dir, gamelog):
    """Test loading gamelogs."""
    loader = GameLogLoader()
    output = loader.run(
        season="2018-19",
        output_dir=data_dir / Path("2018-19")
    )
    assert output.equals(gamelog)
