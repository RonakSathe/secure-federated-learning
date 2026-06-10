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

    print(f"Server result:{result} ")
