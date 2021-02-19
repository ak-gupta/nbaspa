==========
Definition
==========

SPA is an impact metric based on the change in win probability on a play-by-play basis.

------------
Basic Events
------------

We can attribute the impact of many event types to one or two players:

+-------------------+--------------------------------------------+------------------------------------------+
| Event             | Primary player impact                      | Secondary player impact                  |
|                   |                                            |                                          |
+===================+============================================+==========================================+
| Free throw        | | The player shooting the free throws is   | N/A                                      |
|                   | | attributed with the change in win        |                                          |
|                   | | probability.                             |                                          |
+-------------------+--------------------------------------------+------------------------------------------+
| Rebound           | | The player that rebounded the ball is    | N/A                                      |
|                   | | attributed with the change in win        |                                          |
|                   | | probability.                             |                                          |
+-------------------+--------------------------------------------+------------------------------------------+
| Turnover          | | The player that turned the ball over is  | | If a live-ball turnover, the player    |
|                   | | attributed with the change in win        | | that stole the ball is attributed with |
|                   | | probability.                             | | an equal change in win probability.    |
+-------------------+--------------------------------------------+------------------------------------------+
| Foul              | | The player that committed the foul is    | | The player that drew the foul is       |
|                   | | attributed with the change in win        | | attributed with an equal change in win |
|                   | | probability.                             | | probability.                           |
+-------------------+--------------------------------------------+------------------------------------------+
| Missed field goal | | The player that missed the shot is       | N/A                                      |
|                   | | attributed with the change in win        |                                          |
|                   | | probability.                             |                                          |
+-------------------+--------------------------------------------+------------------------------------------+

----------------
Made Field Goals
----------------

There is one key event that is missing from the table above: made field goals. That's because
determining credit for a field goal can be a bit tricker. Let's split all field goals into two
buckets: assisted and unassisted. Unassisted field goals are simple: the player that made the shot
is given credit. However, we need to determine what share of the change in win probability should
be attributed to an assisting player. For this metric, we will use the following system for
attributing credit:

.. math::

    a = \frac{p \cdot f \cdot 100}{o} - 1

* :math:`a` is the percentage of the change in win probability attributed to the assisting player,
* :math:`p` is the number of points associated with the field goal attempt,
* :math:`f` is the shooter's field goal percentage from the area of the shot, and
* :math:`o` is the team's offensive rating.

In short, we will be giving the assisting player credit for the percentage lift in points per 100
possessions driven by the shot they created.

---------
Sequences
---------

There is another corner case we need to address: **sequences**. A **sequence** is a combination
of events that occur in the same time period. For instance, a shooting foul sequence will consist
of the foul and free throw(s) in a single timestamp. We need to firmly define how much impact each
player involved in the sequence should get. Below we've defined some common sequences:

+-----------------------------------------+-----------------------+-----------------------------------------+
| Sequence                                | Events                | Attribution                             |
|                                         |                       |                                         |
+=========================================+=======================+=========================================+
| Offensive foul                          | | * Foul              | | Offensive foul row dropped, player    |
|                                         | | * Turnover          | | committing the foul given blame.      |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (2PT FGA)                 | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit.                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (2PT FGA - Missed FT)     | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit. Unknown effect for      |
|                                         | | * Rebound           | | rebound.                              |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (3PT FGA)                 | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit.                         |
|                                         | | * Free throw        |                                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (3PT FGA - Missed FT)     | | * Foul              | | Player committing the foul given      |
|                                         | | * Free throw        | | blame. Player shooting free throws    |
|                                         | | * Free throw        | | given credit. Unknown effect for      |
|                                         | | * Free throw        | | rebound.                              |
|                                         | | * Rebound           |                                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (FGM)                     | | * Field goal made   | | Player committing the foul given      |
|                                         | | * Foul              | | blame. Player shooting the free throw |
|                                         | | * Free throw        | | given credit.                         |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (FGM - Missed FT)         | | * Field goal made   | | Player committing the foul given      |
|                                         | | * Foul              | | blame. Player shooting the free throw |
|                                         | | * Free throw        | | given credit. Unknown effect for      |
|                                         | | * Rebound           | | rebound.                              |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Putback FGM                             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal made   | | credit proportional to the quality    |
|                                         |                       | | of the shot taken (similar to         |
|                                         |                       | | assist). Player making the shot given |
|                                         |                       | | rest of credit.                       |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Putback FGA                             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal missed | | credit proportional to the quality of |
|                                         |                       | | shot taken (similar to assist).       |
|                                         |                       | | Player taking the shot given rest of  |
|                                         |                       | | credit.                               |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGM)             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal made   | | credit proportional to the quality of |
|                                         | | * Foul              | | the shot. Quality of shot includes    |
|                                         | | * Free throw        | | expected value from free throw.       |
|                                         |                       | | Player that made the shot and shoots  |
|                                         |                       | | the free throw given rest of credit.  |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGA)             | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Foul              | | credit proportional to the expected   |
|                                         | | * Free throw        | | value from free throws. Player taking |
|                                         | | * Free throw        | | free throws given rest of credit.     |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGM - Missed FT) | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Field goal made   | | credit proportional to the quality of |
|                                         | | * Foul              | | the shot. Quality of shot includes    |
|                                         | | * Free throw        | | expected value from free throw.       |
|                                         | | * Rebound           | | Player that made the shot and shoots  |
|                                         |                       | | the free throw given rest of credit.  |
|                                         |                       | | Unknown effect for following rebound. |
+-----------------------------------------+-----------------------+-----------------------------------------+
| Shooting foul (Putback FGA - Missed FT) | | * Rebound           | | Player getting the rebound given      |
|                                         | | * Foul              | | credit proportional to the expected   |
|                                         | | * Free throw        | | value from free throws. Player taking |
|                                         | | * Free throw        | | free throws given rest of credit.     |
|                                         | | * Rebound           | | Unknown effect for following rebound. |
+-----------------------------------------+-----------------------+-----------------------------------------+

.. note::

        In the table above, we're defining "proportional" credit similarly to assists.
