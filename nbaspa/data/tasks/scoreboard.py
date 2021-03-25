"""Scoreboard data.

This module creates Prefect tasks for retrieving

* team identifiers,
* game date,
* last meeting result, and
* team win percentage.
"""

import pandas as pd
from prefect import Task


class AddTeamID(Task):
    """Add the team identifiers and game date."""

    def run(self, pbp: pd.DataFrame, header: pd.DataFrame) -> pd.DataFrame:  # type: ignore
        """Add the team identifiers and game date.

        Adds the following columns:

        * ``HOME_TEAM_ID``,
        * ``VISITOR_TEAM_ID``, and
        * ``GAME_DATE_EST``.

        Parameters
        ----------
        pbp : pd.DataFrame
            The output of ``PlayByPlay.get_data()``.
        header : pd.DataFrame
            The output of ``Scoreboard.get_data("GameHeader")``.

        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        pbp = pbp.merge(
            header[["GAME_ID", "GAME_DATE_EST", "HOME_TEAM_ID", "VISITOR_TEAM_ID"]],
            on="GAME_ID",
            how="left",
        )
        pbp["GAME_DATE_EST"] = pd.to_datetime(pbp["GAME_DATE_EST"])

        return pbp


class AddLastMeetingResult(Task):
    """Add the last meeting result."""

    def run(self, pbp: pd.DataFrame, last_meeting: pd.DataFrame) -> pd.DataFrame:  # type: ignore
        """Add an indicator to show who won the last meeting.

        Adds the following column:

        * ``LAST_GAME_WIN``

        Parameters
        ----------
        pbp : pd.DataFrame
            The output from ``AddTeamID``.
        last_meeting : pd.DataFrame
            The output from ``Scoreboard.get_data("LastMeeting")``.

        Returns
        -------
        pd.DataFrame
            The updated dataset.
        """
        # Assign a new variable with the winning team ID from the last meeting
        last_meeting.loc[
            last_meeting["LAST_GAME_HOME_TEAM_POINTS"]
            > last_meeting["LAST_GAME_VISITOR_TEAM_POINTS"],
            "LAST_GAME_TEAM_ID",
        ] = last_meeting["LAST_GAME_HOME_TEAM_ID"]
        last_meeting.loc[
            last_meeting["LAST_GAME_HOME_TEAM_POINTS"]
            < last_meeting["LAST_GAME_VISITOR_TEAM_POINTS"],
            "LAST_GAME_TEAM_ID",
        ] = last_meeting["LAST_GAME_VISITOR_TEAM_ID"]
        try:
            last_meeting["LAST_GAME_TEAM_ID"] = last_meeting["LAST_GAME_TEAM_ID"].astype(
                int
            )
        except ValueError:
            self.logger.warning(
                f"Dropping {sum(pd.isnull(last_meeting['LAST_GAME_TEAM_ID']))} rows with null "
                "last meeting results"
            )
            last_meeting = last_meeting[~pd.isnull(last_meeting["LAST_GAME_TEAM_ID"])].copy()
            last_meeting["LAST_GAME_TEAM_ID"] = last_meeting["LAST_GAME_TEAM_ID"].astype(
                int
            )
        # Merge with the pbp dataframe
        pbp = pbp.merge(
            last_meeting[["GAME_ID", "LAST_GAME_TEAM_ID"]], on="GAME_ID", how="left"
        )
        pbp.loc[pbp["HOME_TEAM_ID"] == pbp["LAST_GAME_TEAM_ID"], "LAST_GAME_WIN"] = 1
        pbp["LAST_GAME_WIN"] = pbp["LAST_GAME_WIN"].fillna(0)
        pbp["LAST_GAME_WIN"] = pbp["LAST_GAME_WIN"].astype(int)
        # Drop the extra column
        pbp.drop(columns="LAST_GAME_TEAM_ID", inplace=True)

        return pbp
