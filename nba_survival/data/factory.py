"""NBADataFactory.

This factory class will use rate-limiting to avoid spamming the API.
"""

from typing import Dict, List, Optional, Tuple

from alive_progress import alive_bar
from ratelimit import limits, sleep_and_retry

import nba_survival.data.endpoints as endpoints
from nba_survival.data.endpoints.base import BaseRequest

FIFTEEN_MINUTES = 900

class NBADataFactory:
    """Make multiple calls to the API.

    Parameters
    ----------

    Attributes
    ----------
    """

    def __init__(
        self,
        calls: List[Tuple[str, Dict[str, Dict]]],
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file"
    ):
        # Parse the calls
        self.calls = [
            getattr(endpoints, obj)(output_dir=output_dir, filesystem=filesystem, **params)
            for obj, params in calls
        ]
    
    def get(self) -> List[BaseRequest]:
        """Retrieve the data for each API call.

        Parameters
        ----------
        None

        Returns
        -------
        List
            The call objects with data.
        """
        with alive_bar(len(self.calls)) as bar:
            for callobj in self.calls:
                self._get(callobj=callobj)

                bar()
        
        return self.calls
    
    @sleep_and_retry
    @limits(calls=5, period=FIFTEEN_MINUTES)
    def _get(self, callobj: BaseRequest):
        """Run the ``get()`` method to retrieve data.

        Parameters
        ----------
        callobj : BaseRequest
            The endpoint object.
        
        Returns
        -------
        None
        """
        callobj.get()
