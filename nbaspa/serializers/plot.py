"""A ``prefect`` serializer for matplotlib plots."""

import io

import matplotlib.pyplot as plt
import numpy as np
from prefect.engine.serializers import Serializer


class Plot(Serializer):
    """Serializing ``matplotlib`` figures to bytes."""

    def serialize(self, value):
        """Serialize the plot to bytes.

        Parameters
        ----------
        value
            The input plot

        Returns
        -------
        bytes
            The byte-stream
        """
        value.tight_layout()
        buf = io.BytesIO()
        value.savefig(buf, format="png", dpi=300)
        plt.close(value)
        buf.seek(0)
        data = buf.read()
        buf.close()

        return data

    def deserialize(self, value):
        """Recover the plot from bytes.

        Parameters
        ----------
        value
            The byte-stream

        Returns
        -------
        Figure
            The figure object
        """
        fig, ax = plt.subplots()
        np_array = np.frombuffer(value, dtype=np.uint8)

        ax.plot(np_array)

        return fig
