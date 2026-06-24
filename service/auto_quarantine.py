import pandas as pd
import joblib
import json
import os
import time

def run_quarantine():
    model = joblib.load("models/mlp_attack_detector.pkl")
    scaler = joblib.load("models/mlp_scaler.pkl")

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
    try:
        df = pd.read_json("dashboard/client_metrics.json")
    except Exception as e:
        print(f"Error reading metrics: {e}")
        return
    
    latest_round = df["round"].max()

    print(
        df[df["round"]==latest_round][["partition_id","attack_type"]]
    )

    df = df[df["round"]==latest_round]

    X = scaler.transform(df[FEATURES])

    pred = model.predict(X)

    df["prediction"] = pred

    proba = model.predict_proba(X)
    
    df["attack_confidence"] = (
        proba[:,1]*100
        )
    print("\n=== QUARANTINE DEBUG ===")
    print(df[
    [
        "partition_id",
        "attack_type",
        "prediction",
        "attack_confidence",
        "train_accuracy",
        "update_norm",
        "coef_norm"
        ]
    ])

    blocked = set(df.loc[df["attack_confidence"]>=90,"partition_id"].to_list())
    

    df.to_json(
        "dashboard/latest_predictions.json",orient="records",indent=4)

    print("Blocked clients:", blocked)

    blocked_file = "dashboard/blocked_clients.json"
    blocked_df = df[df["partition_id"].isin(blocked)]

    blocked_output = {
        "generated_from_round": int(latest_round),
        "blocked_clients": blocked_df.to_dict(orient="records")}

    with open(blocked_file,"w") as f:
        json.dump(blocked_output,f,indent=4)
    print("]n Saved dashboard/blocked_clients.json")

    print("Total Rows:", len(df))
    print("Unique Clients:", df["partition_id"].nunique())
    print("Latest Round:", df["round"].max())



if __name__ == "__main__":
    while True:
        try:
            run_quarantine()
        except Exception as e:
            print(f"\nExecution error pertains to the run_quarantine True Loop.\n")
            print(e)
        time.sleep(40)