"""
Remarks on Internal Packages Imports:
    from snail.AccessArchivalData import AccessDB
    from snail.SpecProc import HomogenizeSpec, CorrectSpec
    from snail.Predict import SNAIL_Predict
    from snail.PhaseEstimate import FitSingleSpecPhase
    from snail.Train import SNAIL_Train

"""

from .AccessArchivalData import AccessDB
from .SpecProc import HomogenizeSpec, CorrectSpec
from .Predict import SNAIL_Predict_Deep, SNAIL_Predict
from .PhaseEstimate import FitSingleSpecPhase
from .Train import SNAIL_Train
