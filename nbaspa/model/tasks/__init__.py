"""Import the tasks."""

from typing import List

from .calibration import CalibrateClassifier, CalibrateProbability
from .data import SurvivalData, SegmentData, CollapseData
from .io import load_df, LoadData, LoadModel, SavePredictions, SavePreGamePredictions
from .lifelines import (
    InitializeLifelines,
    FitLifelinesModel,
)
from .metrics import AUROC, AUROCLift, MeanAUROCLift
from .predict import WinProbability
from .tuning import LifelinesTuning, XGBoostTuning
from .visualization import (
    PlotMetric,
    PlotProbability,
    PlotTuning,
    PlotShapSummary,
    PlotCalibration,
)
from .xgboost import FitXGBoost, XGBoostShap

__all__: List[str] = [
    "CalibrateClassifier",
    "CalibrateProbability",
    "SurvivalData",
    "SegmentData",
    "CollapseData",
    "LoadData",
    "load_df",
    "LoadModel",
    "InitializeLifelines",
    "FitLifelinesModel",
    "AUROC",
    "AUROCLift",
    "MeanAUROCLift",
    "PlotMetric",
    "WinProbability",
    "PlotProbability",
    "LifelinesTuning",
    "XGBoostTuning",
    "PlotTuning",
    "PlotShapSummary",
    "PlotCalibration",
    "FitXGBoost",
    "XGBoostShap",
    "SavePredictions",
    "SavePreGamePredictions"
]
