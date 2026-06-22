import pandas as pd
import joblib
import json
import os

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

df = pd.read_json("dashboard/client_metrics.json")
latest_round = df["round"].max()

print(
    df[df["round"]==latest_round][["partition_id","attack_type"]]
)

df = df[df["round"]==latest_round]

X = scaler.transform(df[FEATURES])

pred = model.predict(X)

df["prediction"] = pred


blocked = df.loc[pred==1,"partition_id"].tolist()
proba = model.predict_proba(X)
df["attack_confidence"] = (
    proba[:,1]*100
)

print("Blocked clients:", blocked)

blocked_file = "dashboard/blocked_clients.json"
blocked_df = df[df["partition_id"].isin(blocked)]
blocked_data = blocked_df.to_dict(orient="records")
with open(blocked_file,"w") as f:
    json.dump(blocked_data,f,indent=4)
print("]n Saved dashboard/blocked_clients.json")

print("Total Rows:", len(df))
print("Unique Clients:", df["partition_id"].nunique())
print("Latest Round:", df["round"].max())

print(
    df[
        [
            "partition_id",
            "train_accuracy",
            "attack_type",
            "prediction",
            "attack_confidence",
            "update_norm",
            "coef_norm"
        ]
    ]
)
