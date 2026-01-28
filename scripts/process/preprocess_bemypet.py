import os
import sys

# Ensure src is in python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) # scripts/
PROJECT_ROOT = os.path.dirname(BASE_DIR) # project root
sys.path.append(PROJECT_ROOT)

from src.preprocessing.pipeline import run_preprocessing

INPUT_FILE = os.path.join(PROJECT_ROOT, 'data/bemypet_catlab.json')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'data/bemypet_catlab_preprocessed.json')
CHECKPOINT_FILE = os.path.join(PROJECT_ROOT, 'data/bemypet_catlab_preprocessed.json.tmp')

if __name__ == "__main__":
    run_preprocessing(INPUT_FILE, OUTPUT_FILE, CHECKPOINT_FILE)
