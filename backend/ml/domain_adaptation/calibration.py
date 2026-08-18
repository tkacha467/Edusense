"""Probability Calibration & Calibration Error (ECE) Evaluation (v1.12)."""
import numpy as np
from typing import Dict, Any, Tuple
from sklearn.linear_model import LogisticRegression
from sklearn.isotonic import IsotonicRegression

def compute_ece(y_true: np.ndarray, y_probs: np.ndarray, n_bins: int = 10) -> float:
    """
    Computes Expected Calibration Error (ECE) across n_bins probability intervals.
    """
    bin_boundaries = np.linspace(0, 1, n_bins + 1)
    ece = 0.0
    n_samples = len(y_true)

    for i in range(n_bins):
        bin_lower = bin_boundaries[i]
        bin_upper = bin_boundaries[i + 1]
        
        in_bin = (y_probs >= bin_lower) & (y_probs < bin_upper) if i < n_bins - 1 else (y_probs >= bin_lower) & (y_probs <= bin_upper)
        prop_in_bin = np.mean(in_bin)

        if prop_in_bin > 0:
            accuracy_in_bin = np.mean(y_true[in_bin])
            avg_confidence_in_bin = np.mean(y_probs[in_bin])
            ece += np.abs(accuracy_in_bin - avg_confidence_in_bin) * prop_in_bin

    return float(np.round(ece, 4))


class DomainCalibrator:
    """
    Fits offline calibration transforms (Platt / Isotonic) strictly on calibration split.
    """
    def __init__(self, method: str = "platt"):
        self.method = method
        self.model = None

    def fit(self, y_probs_train: np.ndarray, y_train: np.ndarray) -> "DomainCalibrator":
        """Fits calibration curve on calibration probabilities and labels."""
        if self.method == "platt":
            probs = np.clip(y_probs_train, 1e-6, 1 - 1e-6).reshape(-1, 1)
            logits = np.log(probs / (1.0 - probs))
            self.model = LogisticRegression(C=1.0, solver="lbfgs")
            self.model.fit(logits, y_train)
        elif self.method == "isotonic":
            self.model = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
            self.model.fit(y_probs_train, y_train)
        return self

    def transform(self, y_probs: np.ndarray) -> np.ndarray:
        """Transforms uncalibrated probabilities using fitted calibration model."""
        if self.model is None:
            return y_probs

        if self.method == "platt":
            probs = np.clip(y_probs, 1e-6, 1 - 1e-6).reshape(-1, 1)
            logits = np.log(probs / (1.0 - probs))
            return self.model.predict_proba(logits)[:, 1]
        elif self.method == "isotonic":
            return self.model.predict(y_probs)

        return y_probs
