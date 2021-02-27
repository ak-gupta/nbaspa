"""Test loading NBA win probability."""

from nbaspa.data.endpoints import WinProbability

def test_win_probability(output_dir):
    """Test loading win probability."""
    pbp = WinProbability(GameID="00218DUMMY", output_dir=output_dir)
    pbp.get()

    for dataset in pbp.datasets:
        assert pbp.get_data(dataset).empty
