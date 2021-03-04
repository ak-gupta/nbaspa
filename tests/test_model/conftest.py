"""Define some fixtures."""

import numpy as np
import pandas as pd
import pytest

@pytest.fixture(scope="session")
def data():
    """Create some test model input data."""
    netrating = np.random.uniform(-5.0, 5.0, size=30)
    gamenets = np.round(np.repeat(netrating, 5), 1)
    static_df = pd.DataFrame(
        {
            "GAME_ID": [f"00218DUMMY{idx}" for idx in range(1, 151)],
            "HOME_W_PCT": np.round(np.random.uniform(0.3, 0.7, size=150), 2),
            "VISITOR_W_PCT": np.round(np.random.uniform(0.3, 0.7, size=150), 2),
            "LAST_GAME_WIN": np.random.binomial(1, 0.5, size=150),
            "HOME_GAMES_IN_LAST_3_DAYS": np.random.randint(0, 2, size=150),
            "HOME_GAMES_IN_LAST_5_DAYS": np.random.randint(0, 3, size=150),
            "HOME_GAMES_IN_LAST_7_DAYS": np.random.randint(2, 4, size=150),
            "VISITOR_GAMES_IN_LAST_3_DAYS": np.random.randint(0, 2, size=150),
            "VISITOR_GAMES_IN_LAST_5_DAYS": np.random.randint(0, 3, size=150),
            "VISITOR_GAMES_IN_LAST_7_DAYS": np.random.randint(2, 4, size=150),
            "WIN": np.random.binomial(1, 0.5, size=150),
        }
    )
    np.random.shuffle(gamenets)
    static_df["HOME_NET_RATING"] = gamenets
    np.random.shuffle(gamenets)
    static_df["VISITOR_NET_RATING"] = gamenets
    # Create the dynamic df
    dfs = []
    for _, row in static_df.iterrows():
        new = pd.DataFrame(
            {
                "TIME": np.sort(np.random.randint(0, 2880, size=100)),
                "SCOREMARGIN": np.random.randint(-20, 20, size=100),
                "NBA_WIN_PROB": np.round(np.random.uniform(0.0, 0.999, size=100), 3),
                "HOME_LINEUP_PLUS_MINUS": 0.0,
                "VISITOR_LINEUP_PLUS_MINUS": 0.0
            }
        )
        for idx, value in row.iteritems():
            new[idx] = value

        dfs.append(new)
    
    final = pd.concat(dfs)
    final.sort_values(by=["GAME_ID", "TIME"], ascending=True, inplace=True)
    final.reset_index(drop=True, inplace=True)
    
    return final
