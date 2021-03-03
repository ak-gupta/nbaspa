"""BaseRequest.

Create a class for base requests to the NBA API.
"""

from abc import abstractmethod
from copy import deepcopy
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Union

import fsspec
import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .parameters import ParameterValues

LOG = logging.getLogger(__name__)

SESSION = requests.Session()
RETRIES = Retry(total=5, backoff_factor=1, status_forcelist=[502, 503, 504])
SESSION.mount("http://", HTTPAdapter(max_retries=RETRIES))


class BaseRequest:
    """Base class for getting data from the NBA API.

    Parameters
    ----------
    output_dir : str, optional (default None)
        A base output directory to use. If provided, each successful request
        will stream to a JSON file in the specified directory, within a subfolder
        for the endpoint.
    filesystem : str, optional (default "file")
        The ``fsspec`` filesystem to use if reading/writing files.
    **params
        Parameters for the request

    Attributes
    ----------
    data : pd.DataFrame
        The raw data, in tabular form.
    _raw_data : Dict
        The raw output JSON from the endpoint.
    """

    base_url: str = "https://stats.nba.com/stats"
    headers = {
        "Host": "stats.nba.com",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:61.0) Gecko/20100101 Firefox/61.0"
        ),
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://stats.nba.com/",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "x-nba-stats-origin": "stats",
        "x-nba-stats-token": "true",
    }
    endpoint: str = "default"
    filename: str = "default.json"

    def __init__(
        self,
        output_dir: Optional[str] = None,
        filesystem: Optional[str] = "file",
        **params,
    ):
        """Init method."""
        self.output_dir = output_dir
        self.fs = fsspec.filesystem(filesystem)
        self.params = params

        self._response: Optional[requests.Response] = None
        self._raw_data: Dict = {}

    def get(self):
        """Get the data from the API.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Check to see if a file exists
        self.load()
        if not self._raw_data:
            self._get()
        if self.output_dir is not None and self._response is not None:
            LOG.info(f"Writing data to {str(self.fpath)}...")
            self.fs.mkdir(Path(self.output_dir, self.endpoint))
            with self.fs.open(self.fpath, "w") as outfile:
                json.dump(self._raw_data, outfile, indent=4)

    def _get(self):
        """Retrieve data from the API.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        # Retrieve the data
        self._response = SESSION.get(
            f"{self.base_url}/{self.endpoint}",
            headers=self.headers,
            params=self.params,
            timeout=(10, 15),
        )
        self._response.raise_for_status()
        self._raw_data = self._response.json()

    def get_data(self, dataset_type: Optional[str] = "default") -> pd.DataFrame:
        """Get a tabular dataset.

        Parameters
        ----------
        dataset_type : str, optional (default "default")
            The dataset type.

        Returns
        -------
        pd.DataFrame
            The tabular dataframe.
        """
        for index, value in enumerate(self.datasets):
            if value == dataset_type:
                idx = index
                break
        else:
            raise ValueError("Please provide a valid value for dataset type")

        return pd.DataFrame.from_records(
            self._raw_data["resultSets"][idx]["rowSet"],
            columns=self._raw_data["resultSets"][idx]["headers"],
        )

    def load(self):
        """Load data from JSON.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        if self.exists():
            LOG.info(f"Reading existing file {str(self.fpath)}...")
            with self.fs.open(self.fpath) as infile:
                self._raw_data = json.load(infile)

    def exists(self) -> bool:
        """Check whether the file exists.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        return bool(self.output_dir is not None and self.fs.exists(self.fpath))

    @property
    def defaults(self) -> Dict:
        """Standard parameters for the endpoint.

        Returns
        -------
        Dict
            Default values for each request parameter.
        """
        return {}

    @property
    def datasets(self) -> List[str]:
        """Datasets returned by the API.

        Returns
        -------
        List
            Datasets returned by the API.
        """
        return ["default"]

    @property
    def fpath(self) -> Union[None, Path]:
        """Define the filepath.

        Returns
        -------
        Path
            The path object.
        """
        if self.output_dir is None:
            return None
        else:
            return Path(self.output_dir, self.endpoint, self.filename.format(**self.params))

    @property
    def params(self) -> Dict:
        """Request parameters.

        Returns
        -------
        Dict
            The request parameters
        """
        return self.__params

    @params.setter
    def params(self, value: Dict):
        """Set the request parameters by updating the defaults."""
        allowed_values = ParameterValues()
        self.__params = deepcopy(self.defaults)
        # Make sure the submitted values are valid
        for param, submitted in value.items():
            if getattr(allowed_values, param) is not None:
                if submitted not in getattr(allowed_values, param):
                    raise ValueError(f"{submitted} is an invalid value for {param}")
        self.__params.update(value)
