import csv
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATASET_PATH = BASE_DIR/"datasets"/"attack_dataset.csv"

def save_training_sample(record:dict):
    DATASET_PATH.parent.mkdir(exist_ok=True)
    file_exists = DATASET_PATH.exists()

    with open(DATASET_PATH,"a",newline="") as f:
        writer = csv.DictWriter(
            f,fieldnames=record.keys()
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(record)