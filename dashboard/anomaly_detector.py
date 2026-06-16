import json
import numpy as np
with open("dashboard/client_metrics.json","r") as f:
    data = json.load(f)

latest_round = data[-10:]
norms = [x["update_norm"] for x in latest_round]

mean = np.mean(norms)
std = np.std(norms)

for client in latest_round:
    zscore = abs(
        (client["update_norm"]-mean)/(std+1e-8)
    )

    if zscore > 2: client["status"] = "ATTACK"
    else: client["status"] = "NORMAL"

print(latest_round)