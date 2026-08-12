from pathlib import Path
import os

# ======================================================
# Project Configuration
# ======================================================

PROJECT_NAME = "Personal Knowledge Decay Predictor"

# Search inside Google Drive
matches = [
    p for p in Path("/content/drive/MyDrive").rglob(PROJECT_NAME)
    if p.is_dir()
]

if len(matches) == 0:
    raise FileNotFoundError(
        f"Project folder '{PROJECT_NAME}' not found."
    )

PROJECT_ROOT = matches[0]

# Set working directory
os.chdir(PROJECT_ROOT)

# Frequently used folders
DATA_DIR = PROJECT_ROOT / "Data"
REPORT_DIR = PROJECT_ROOT / "Reports"
MODEL_DIR = PROJECT_ROOT / "Models"
NOTEBOOK_DIR = PROJECT_ROOT / "Notebooks"

print(f"✅ Project Root : {PROJECT_ROOT}")