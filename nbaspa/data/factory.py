"""NBADataFactory.

This factory class will use rate-limiting to avoid spamming the API.
"""

import logging
from typing import Dict, List, Optional, Tuple

from alive_progress import alive_bar
import pandas as pd
from ratelimit import limits, sleep_and_retry

import nbaspa.data.endpoints as endpoints
from .endpoints.base import BaseRequest

LOG = logging.getLogger(__name__)


class NBADataFactory:
    """Make multiple calls to the API.

    Parameters
    ----------
    calls : list
        A list containing the calls. Each entry in the list should be a tuple,
        with the first entry being the name of the ``BaseRequest`` subclass
        you want to call. The second element of the tuple should be a dictionary
        with the parameters for the API call.
    output_dir : str, optional (default None)
        A base output directory to use. If provided, each successful request
        will stream to a JSON file in the specified directory, within a subfolder
        for the endpoint.
    filesystem : str, optional (default "file")
        The ``fsspec`` filesystem to use if reading/writing files.

    Attributes
    ----------
    calls
        A list with one object per tuple in the ``calls`` initialization argument.
    """

    def __init__(
        self,
        calls: List[Tuple[str, Dict[str, Dict]]],
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
    ):
        """Init method."""
        # Parse the calls
        self.calls = []
        for obj, params in calls:
            if "output_dir" not in params:
                params["output_dir"] = output_dir
            if "filesystem" not in params:
                params["filesystem"] = filesystem
            self.calls.append(getattr(endpoints, obj)(**params))

    def get(self) -> List[BaseRequest]:
        """Retrieve the data for each API call.

        Returns
        -------
        List
            The call objects with data.
        """
        # Don't download what we already have
        LOG.info("Removing calls we already have data for...")
        remaining = [
            index for index, value in enumerate(self.calls) if not value.exists()
        ]
        with alive_bar(len(remaining)) as bar:
            for index in remaining:
                self._get(callobj=self.calls[index])

                bar()

        return self.calls

    def load(self) -> List[BaseRequest]:
        """Load data from a filesystem for each call.

        Returns
        -------
        List
            The call objects with data.
        """
        with alive_bar(len(self.calls)) as bar:
            for callobj in self.calls:
                callobj.load()

                bar()

        return self.calls

    def get_data(self, dataset_type: Optional[str] = "default") -> pd.DataFrame:
        """Retrieve and concatenate data.

        .. important::

            This will only work if every call is of the same type.

        Parameters
        ----------
        dataset_type : str, optional (default "default")
            The dataset type to retrieve from the call objects.

        Returns
        -------
        pd.DataFrame
            The concatenated dataframe.
        """
        df_list = []
        for callobj in self.calls:
            try:
                df_list.append(callobj.get_data(dataset_type=dataset_type))
            except KeyError:
                LOG.error(f"Unable to retrieve data for {str(callobj)}")
                raise ValueError(f"Unable to retrieve data for {str(callobj)}")

        return pd.concat(df_list, ignore_index=True)

    @sleep_and_retry
    @limits(calls=1, period=60)
    def _get(self, callobj: BaseRequest):
        """Run the ``get()`` method to retrieve data.

        Parameters
        ----------
        callobj : BaseRequest
            The endpoint object.
        """
        callobj.get()
