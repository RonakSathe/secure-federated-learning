import time
import json
import joblib
import pandas as pd

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neural_network import MLPClassifier

DATASET = "datasets/attack_dataset.csv"
STATE_FILE = "models/training_state.json"
MODEL_FILE = "models/mlp_attack_detector.pkl"
SCALER_FILE = "models/mlp_scaler.pkl"

FEATURES = [
    "train_accuracy",
    "update_norm",
    "coef_norm",
    "intercept_norm",
    "avg_cpu",
    "avg_memory",
    "avg_connections",
    "training_time",
]

RETRAIN_THRESHOLD = 50

def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE,"r") as f:
            return json.load(f)
    return {"last_rows": 0}

def save_state(rows):
    with open(STATE_FILE,"w") as f:
        json.dump(
            {"last_rows": rows},
            f,
            indent=4,
        )

def retrain():
    print("\n Retraining Neural MLP Model ")
    df = pd.read_csv(DATASET)

    X = df[FEATURES]
    y = df["label"]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_train,X_test,y_train,y_test = train_test_split(X_scaled,y,random_state=42,test_size=0.2,stratify=y)

    model = MLPClassifier(hidden_layer_sizes=(64,32),max_iter=2000,random_state=42)
    model.fit(X_train,y_train)

    acc = model.score(X_test,y_test)

    print(f"New Accuracy: {acc:.4f}")

    joblib.dump(model, MODEL_FILE)
    joblib.dump(scaler,SCALER_FILE)

    save_state(len(df))
    print("\n\n ======================MODEL UPDATED======================")

while True:
    try:
        print("Dataset Read")
        df = pd.read_csv(DATASET)
        current_rows = len(df)
        state = load_state()
        last_rows = state["last_rows"]
        if current_rows - last_rows >= RETRAIN_THRESHOLD:
            print("Retraining Starts")
            retrain()
        else:
            print("NOt much records")
        time.sleep(50)
    
    except Exception as e:
        print(e)
        