==============
Model Features
==============

The survival analysis model will use a dataset with the following variables:

+------------------------------------+--------------+-------------------------------------------------------+
| Variable                           | Time-Varying | Description                                           |
|                                    |              |                                                       |
+====================================+==============+=======================================================+
| ``WIN``                            | Yes          | | A boolean indicator of whether or not the home team |
|                                    |              | | won the game. This is the "event" that the survival |
|                                    |              | | analysis model will predict.                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``TIME``                           | Yes          | | Elapsed game time, in seconds. This is the time     |
|                                    |              | | variable for the survival analysis model.           |
+------------------------------------+--------------+-------------------------------------------------------+
| ``SCOREMARGIN``                    | Yes          | | The scoring margin at time ``TIME`` in the game.    |
|                                    |              | | For example, if the home team is leading 2-0, the   |
|                                    |              | | value of this variable is 2.                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_LINEUP_PLUS_MINUS`` [*]_    | Yes          | | The net rating of the current lineup for the home   |
|                                    |              | | team.                                               |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_LINEUP_PLUS_MINUS`` [*]_ | Yes          | | The net rating of the current lineup for the        |
|                                    |              | | visiting team.                                      |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_NET_RATING``                | No           | The net rating of the home team entering the game.    |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_NET_RATING``             | No           | | The net rating of the visiting team entering the    |
|                                    |              | | game.                                               |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_W_PCT``                     | No           | | The win percentage of the home team entering the    |
|                                    |              | | game.                                               |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_W_PCT``                  | No           | | The win percentage of the visiting team entering    |
|                                    |              | | the game.                                           |
+------------------------------------+--------------+-------------------------------------------------------+
| ``LAST_GAME_WIN``                  | No           | | A boolean indicator of whether or not the current   |
|                                    |              | | home team won the last meeting between these two    |
|                                    |              | | teams.                                              |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_3_DAYS``      | No           | | The number of games the home team has played in the |
|                                    |              | | last 3 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_3_DAYS``   | No           | | The number of games the visiting team has played in |
|                                    |              | | the last 3 days.                                    |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_5_DAYS``      | No           | | The number of games the home team has played in the |
|                                    |              | | last 5 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_5_DAYS``   | No           | | The number of games the visiting team has played in |
|                                    |              | | last 5 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``HOME_GAMES_IN_LAST_7_DAYS``      | No           | | The number of games the home team has played in the |
|                                    |              | | last 7 days.                                        |
+------------------------------------+--------------+-------------------------------------------------------+
| ``VISITOR_GAMES_IN_LAST_7_DAYS``   | No           | | The number of games the visiting team has played in |
|                                    |              | | the last 7 days.                                    |
+------------------------------------+--------------+-------------------------------------------------------+

.. [*] For any rows where the lineup can't be parsed, the value will be the home team's net rating.
.. [*] For any rows where the lineup can't be parsed, the value will be the visiting team's net rating.