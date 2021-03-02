"""Test the loader methods."""

from datetime import datetime
from pathlib import Path

import pandas as pd

from nbaspa.data.tasks import (
    GenericLoader,
    PlayByPlayLoader,
    WinProbabilityLoader,
    GameLogLoader,
    LineupLoader,
    RotationLoader,
    ShotChartLoader,
    BoxScoreLoader,
    ShotZoneLoader,
    GeneralShootingLoader,
)

pd.options.display.max_columns = 35

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
    output.sort_values(by=["GAME_ID", "EVENTNUM"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    print(output)
    print(pbp)

    assert output.equals(pbp)

def test_win_probability_loader(data_dir, header, win_prob):
    """Test loading NBA win probability data."""
    loader = WinProbabilityLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["GAME_ID", "EVENT_NUM"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)
    
    print(output)
    print(win_prob)

    assert output.equals(win_prob)

def test_gamelog_loader(data_dir, gamelog):
    """Test loading gamelogs."""
    loader = GameLogLoader()
    output = loader.run(
        season="2018-19",
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["Team_ID", "GAME_DATE"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)
    
    print(output)
    print(gamelog)

    assert output.equals(gamelog)

def test_lineup_loader(data_dir, lineup_stats):
    """Test loading lineup stats."""
    loader = LineupLoader()
    output = loader.run(
        season="2018-19",
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["GROUP_ID"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    print(output)
    print(lineup_stats)

    assert output.equals(lineup_stats)

def test_rotation_loader(data_dir, header, homerotation, awayrotation):
    """Test loading the rotation data."""
    loader = RotationLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19"),
    )
    output["AwayTeam"].sort_values(
        by=["GAME_ID", "PERSON_ID"], ascending=True, inplace=True
    )
    output["AwayTeam"].reset_index(drop=True, inplace=True)
    output["HomeTeam"].sort_values(
        by=["GAME_ID", "PERSON_ID"], ascending=True, inplace=True
    )
    output["HomeTeam"].reset_index(drop=True, inplace=True)

    print(output["AwayTeam"])
    print(awayrotation)

    print(output["HomeTeam"])
    print(homerotation)

    assert output["AwayTeam"].equals(awayrotation)
    assert output["HomeTeam"].equals(homerotation)

def test_shotchart_loader(data_dir, header, shotchart):
    """Test loading the shotchart data."""
    loader = ShotChartLoader()
    output = loader.run(
        header=header,
        season="2018-19",
        output_dir=data_dir / Path("2018-19")
    )
    assert output.sort_values(by=["GAME_ID", "GAME_EVENT_ID"], ascending=True).equals(
        shotchart.sort_values(by=["GAME_ID", "GAME_EVENT_ID"], ascending=True)
    )

def test_boxscore_loader(data_dir, header, boxscore):
    """Test loading boxscore data."""
    loader = BoxScoreLoader()
    output = loader.run(
        header=header,
        output_dir=data_dir / Path("2018-19")
    )
    output.sort_values(by=["GAME_ID", "PLAYER_ID"], ascending=True, inplace=True)
    output.reset_index(drop=True, inplace=True)

    print(output)
    print(boxscore)

    assert output.equals(boxscore)

def test_shotzone_loader(data_dir, boxscore, shotzonedashboard):
    """Test loading shotzone data."""
    # Only test one game of data since we have repeated games
    loader = ShotZoneLoader()
    output = loader.run(
        boxscore=boxscore[boxscore["GAME_ID"] == "00218DUMMY1"],
        output_dir=data_dir / Path("2018-19")
    )
    assert output.equals(shotzonedashboard)

def test_overall_shooting_loader(data_dir, boxscore, overallshooting):
    """Test loading overall shooting data."""
    loader = GeneralShootingLoader()
    output = loader.run(
        boxscore=boxscore[boxscore["GAME_ID"] == "00218DUMMY1"],
        output_dir=data_dir / Path("2018-19")
    )
    assert output.equals(overallshooting)
