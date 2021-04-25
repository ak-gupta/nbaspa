"""Test generating metrics."""

from unittest.mock import patch

import numpy as np

from nbaspa.model.tasks import AUROC, AUROCLift

@patch("nbaspa.model.tasks.metrics.roc_auc_score")
def test_auroc(mock_auc, data):
    """Test AUROC."""
    tsk = AUROC()
    tsk.run(data=data, mode="benchmark")

    assert mock_auc.call_count == 1

    _, kwargs = mock_auc.call_args_list[0]

    assert kwargs["y_true"].equals(data["WIN"])
    assert kwargs["y_score"].equals(data["NBA_WIN_PROB"])

def test_auroc_lift():
    """Test the simple lift task."""
    tsk = AUROCLift()
    output = tsk.run(benchmark=[0.5, 0.55, 0.6], test=[0.6, 0.65, 0.65])

    assert np.allclose(output, np.array([0.2, 0.18181818, 0.083333333]))
