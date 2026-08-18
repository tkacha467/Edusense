"""Feature Domain Normalization & Scaling for External Shift (v1.12)."""
import numpy as np
from typing import Dict, Any

class DomainFeatureNormalizer:
    """
    Offline feature domain normalizer for ASSISTments distribution shift.
    Applies scientifically justified response-time compression and feature scaling.
    """
    def __init__(self, method: str = "domain_specific"):
        self.method = method
        self.fitted = False
        self.medians = None
        self.iqrs = None

    def fit(self, X: np.ndarray) -> "DomainFeatureNormalizer":
        """Fits normalization statistics on calibration/training feature split."""
        self.medians = np.median(X, axis=0)
        q75, q25 = np.percentile(X, [75, 25], axis=0)
        self.iqrs = q75 - q25
        self.iqrs[self.iqrs == 0] = 1.0
        self.fitted = True
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        """Transforms feature matrix under specified domain normalization strategy."""
        X_out = X.copy().astype(float)

        if self.method == "raw":
            return X_out

        if self.method == "domain_specific":
            # Response-time domain normalization (index 5: avg_response_time_seconds): Log1p transformation after clipping [0.5s, 60s]
            resp_col = X_out[:, 5]
            resp_clipped = np.clip(resp_col, 0.5, 60.0)
            X_out[:, 5] = np.log1p(resp_clipped)

            # Days since last review (index 0): Log1p compression for extreme temporal gaps
            X_out[:, 0] = np.log1p(np.clip(X_out[:, 0], 0.0, 365.0))

        elif self.method == "robust_scaler":
            if not self.fitted:
                self.fit(X)
            X_out = (X_out - self.medians) / self.iqrs

        elif self.method == "quantile_transform":
            # Simple percentile-rank transformation per feature
            for col in range(X_out.shape[1]):
                vals = X_out[:, col]
                ranks = np.argsort(np.argsort(vals))
                X_out[:, col] = ranks / (len(vals) - 1 + 1e-8)

        return X_out

    def fit_transform(self, X: np.ndarray) -> np.ndarray:
        return self.fit(X).transform(X)
