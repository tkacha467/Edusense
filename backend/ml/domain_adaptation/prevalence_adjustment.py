"""Prior Probability Shift & Prevalence Adjustment Module (v1.12)."""
import numpy as np

def adjust_prior_probability(
    y_probs: np.ndarray,
    p_dev: float = 0.0925,
    p_ext: float = 0.6500,
    eps: float = 1e-6
) -> np.ndarray:
    """
    Adjusts uncalibrated model probabilities for prevalence prior shift using Bayes log-odds adjustment.
    
    Args:
        y_probs (np.ndarray): Original predicted probabilities.
        p_dev (float): Development dataset forgetting prevalence (default = 0.0925 / 9.25%).
        p_ext (float): External benchmark target prevalence (default = 0.6500 / 65.0%).
        eps (float): Numerical stability threshold.
    
    Returns:
        np.ndarray: Prior-adjusted predicted probabilities.
    """
    probs = np.clip(y_probs, eps, 1.0 - eps)
    logits = np.log(probs / (1.0 - probs))

    # Prior shift log-odds offset delta
    delta_log_odds = np.log(p_ext / (1.0 - p_ext)) - np.log(p_dev / (1.0 - p_dev))
    adj_logits = logits + delta_log_odds
    adj_probs = 1.0 / (1.0 + np.exp(-adj_logits))

    return np.clip(adj_probs, 0.0, 1.0)
