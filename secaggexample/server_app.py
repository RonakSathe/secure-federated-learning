from flwr.serverapp import ServerApp, Grid
from flwr.serverapp.strategy import FedAvg
from .task import *
from strategy.secure_strategy import SecureFedAvg
import json
import os

from flwr.app import (
    ArrayRecord,Context,
)

app = ServerApp()

@app.main()
def main(grid:Grid,context:Context):
    model = build_model()

    arrays = ArrayRecord.from_numpy_ndarrays(get_parameters(model))

    # strategy = SecureFedAvg(
    #     fraction_train= 1.0,
    # )

    strategy = SecureFedAvg(fraction_train=1.0)

    result = strategy.start(
        grid=grid,
        initial_arrays=arrays,
        num_rounds=30,
    )

    print("\nEVALUATE METRICS CLIENT APP")
    print(result.evaluate_metrics_clientapp)

    print("\nTRAIN METRICS CLIENT APP")
    print(result.train_metrics_clientapp)

    #Appending the results
    rows = []
    for rnd,metrics in result.train_metrics_clientapp.items():
        rows.append({
            "round": int(rnd),
            "train_accuracy": metrics.get("train_accuracy",0),
            "train_loss": metrics.get("train_loss", 0),
            "update_norm": metrics.get("update_norm", 0),
            "coef_norm": metrics.get("coef_norm", 0),
        })
    df = pd.DataFrame(rows)
    EXPERIMENT_NAME = "attack_securefedavg"
    os.makedirs("results",exist_ok=True)
    df.to_csv(f"results/{EXPERIMENT_NAME}.csv",index=False)
    print(f"Saved in results/{EXPERIMENT_NAME}.csv")

    eval_rows = []
    for rnd,metrics in result.evaluate_metrics_clientapp.items():
        eval_rows.append({
            "round": int(rnd),
            "accuracy": metrics.get("accuracy", 0),
            "loss": metrics.get("loss", 0),
        })
    pd.DataFrame(eval_rows).to_csv(f"results/{EXPERIMENT_NAME}_eval.csv",index=False)
    print(f"Saved in results/{EXPERIMENT_NAME}_eval.csv")
    
    train_metrics = {
        str(rnd): dict(metrics) for rnd,metrics in result.train_metrics_clientapp.items()
    }
    eval_metrics = {
        str(rnd): dict(metrics) for rnd,metrics in result.evaluate_metrics_clientapp.items()
    }
    server_metrics = {
        str(rnd): dict(metrics) for rnd,metrics in result.evaluate_metrics_serverapp.items()
    }



    dashboard_data =  {
        "train_metrics": train_metrics,
        "evaluate_metrics": eval_metrics,
        "server_metrics": server_metrics,
    }

    os.makedirs("dashboard",exist_ok=True)
    with open("dashboard/metrics.json","w") as f:
        json.dump(
            dashboard_data,
            f,
            indent=4,
        )

    print(f"\n\nServer result:{result} ")
    