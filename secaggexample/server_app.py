from flwr.serverapp import ServerApp, Grid
from flwr.serverapp.strategy import FedAvg
from .task import *

from flwr.app import (
    ArrayRecord,Context,
)

app = ServerApp()

@app.main()
def main(grid:Grid,context:Context):
    model = build_model()

    arrays = ArrayRecord.from_numpy_ndarrays(get_parameters(model))

    strategy = FedAvg()

    result = strategy.start(
        grid=grid,
        initial_arrays=arrays,
        num_rounds=2,
    )

    import json
    import os

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
    print(f"\n\nResult of client app training: {result.train_metrics_clientapp}")
    print(f"\n\nResult of client app evaluate: {result.evaluate_metrics_clientapp}")
    print(f"\n\nResult of server app evaluate: {result.evaluate_metrics_serverapp}")
    
