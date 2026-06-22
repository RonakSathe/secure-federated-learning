import pandas as pd
import matplotlib.pyplot as plt

# Load files
baseline = pd.read_csv("results/baseline.csv")
attack = pd.read_csv("results/attack_fedavg.csv")
secure = pd.read_csv("results/attack_securefedavg.csv")

baseline_eval = pd.read_csv("results/baseline_eval.csv")
attack_eval = pd.read_csv("results/attack_fedavg_eval.csv")
secure_eval = pd.read_csv("results/attack_securefedavg_eval.csv")

# ==================================================
# TRAIN ACCURACY GRAPH
# ==================================================

plt.figure(figsize=(10,6))

plt.plot(
    baseline["round"],
    baseline["train_accuracy"],
    marker="o",
    label="Baseline"
)

plt.plot(
    attack["round"],
    attack["train_accuracy"],
    marker="s",
    label="Attack + FedAvg"
)

plt.plot(
    secure["round"],
    secure["train_accuracy"],
    marker="^",
    label="Attack + SecureFedAvg"
)

plt.xlabel("Round")
plt.ylabel("Training Accuracy")
plt.title("Training Accuracy Comparison")
plt.legend()
plt.grid(True)

plt.savefig(
    "results/train_accuracy_comparison.png",
    bbox_inches="tight"
)

plt.close()

# ==================================================
# EVALUATION ACCURACY GRAPH
# ==================================================

plt.figure(figsize=(10,6))

plt.plot(
    baseline_eval["round"],
    baseline_eval["accuracy"],
    marker="o",
    label="Baseline"
)

plt.plot(
    attack_eval["round"],
    attack_eval["accuracy"],
    marker="s",
    label="Attack + FedAvg"
)

plt.plot(
    secure_eval["round"],
    secure_eval["accuracy"],
    marker="^",
    label="Attack + SecureFedAvg"
)

plt.xlabel("Round")
plt.ylabel("Evaluation Accuracy")
plt.title("Evaluation Accuracy Comparison")
plt.legend()
plt.grid(True)

plt.savefig(
    "results/eval_accuracy_comparison.png",
    bbox_inches="tight"
)

plt.close()

print("Graphs Generated Successfully")


summary = pd.DataFrame([
    {
        "Scenario":"Baseline",
        "Final Train Accuracy":
            baseline["train_accuracy"].iloc[-1],
        "Final Eval Accuracy":
            baseline_eval["accuracy"].iloc[-1]
    },
    {
        "Scenario":"Attack + FedAvg",
        "Final Train Accuracy":
            attack["train_accuracy"].iloc[-1],
        "Final Eval Accuracy":
            attack_eval["accuracy"].iloc[-1]
    },
    {
        "Scenario":"Attack + SecureFedAvg",
        "Final Train Accuracy":
            secure["train_accuracy"].iloc[-1],
        "Final Eval Accuracy":
            secure_eval["accuracy"].iloc[-1]
    }
])

summary.to_csv(
    "results/performance_summary.csv",
    index=False
)

print(summary)

import pandas as pd

blocked = pd.read_json(
    "dashboard/blocked_clients.json"
)

print(blocked[
    [
        "partition_id",
        "attack_type",
        "attack_confidence"
    ]
])