import os
import sys
import numpy as np
import pandas as pd
from datetime import datetime

# Add the parent directory to the path so we can import 'app'
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.knowledge import PredictionEngineService
from app.config.settings import get_settings

def run_validation():
    print(f"[{datetime.now().isoformat()}] Starting ML Pipeline Validation...")
    
    # Initialize the engine
    engine = PredictionEngineService()
    
    if engine.__class__._loaded:
        print("[SUCCESS] ML Model loaded successfully from disk.")
    else:
        print("[FAIL] ML Model failed to load, falling back to formula.")

    # Scenarios for monotonicity check
    scenarios = [
        {"name": "Complete Beginner (1st try, wrong)", "inputs": (1, 1, 0, 0.0, 0.0, False)},
        {"name": "Beginner (1st try, correct)", "inputs": (1, 1, 1, 1.0, 1.0, False)},
        {"name": "Intermediate (5 tries, 60% acc)", "inputs": (5, 5, 3, 0.6, 0.6, False)},
        {"name": "Advanced (20 tries, 90% acc)", "inputs": (20, 20, 18, 0.9, 0.9, False)},
        {"name": "Mastered (50 tries, 100% acc)", "inputs": (50, 50, 50, 1.0, 1.0, True)},
        {"name": "Recent Decline (50 tries, past 1.0, rolling 0.2)", "inputs": (51, 51, 50, 0.98, 0.2, False)},
    ]

    print("\n--- Monotonicity & Boundary Checks ---")
    results = []
    for s in scenarios:
        fp, rs, cs = engine.predict_forgetting_probability(*s["inputs"])
        results.append({
            "Scenario": s["name"],
            "Forget Prob": fp,
            "Retention": rs,
            "Confidence": cs
        })
        print(f"Scenario: {s['name']:<45} | Forget Prob: {fp:.4f} | Retention: {rs:.4f}")

    # Test Data Leakage
    print("\n--- Data Leakage Check ---")
    fp1, rs1, cs1 = engine.predict_forgetting_probability(2, 2, 1, 0.5, 0.5, False)
    fp2, rs2, cs2 = engine.predict_forgetting_probability(2, 2, 1, 0.5, 0.5, False)
    print(f"Call 1: Forget={fp1:.4f}")
    print(f"Call 2: Forget={fp2:.4f}")
    if fp1 == fp2:
        print("[SUCCESS] No State Leakage (Deterministic outputs for same input).")
    else:
        print("[FAIL] Data Leakage detected! Model maintains state between calls.")

    df = pd.DataFrame(results)
    
    # Save the output to a CSV for further analysis if needed
    os.makedirs(os.path.join(os.path.dirname(__file__), 'output'), exist_ok=True)
    csv_path = os.path.join(os.path.dirname(__file__), 'output', 'ml_validation_results.csv')
    df.to_csv(csv_path, index=False)
    print(f"\nResults saved to {csv_path}")

if __name__ == "__main__":
    run_validation()
