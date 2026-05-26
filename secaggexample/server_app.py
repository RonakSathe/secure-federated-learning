from __future__ import annotations
from flwr.app import Context
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg
from flwr.common import ndarrays_to_parameters
import numpy as np

def server_fn(context:Context) -> ServerAppComponents:
    _ = context 

    #initializing parameters
    initial_paramters = ndarrays_to_parameters(
    [
        np.zeros((1,5)),
        np.zeros(1),
    ]
    )

    config = ServerConfig(num_rounds = 3)
    strategy = FedAvg(
        initial_parameters = initial_paramters,
    )

    return ServerAppComponents(
        config = config,
        strategy = strategy,
    )

app = ServerApp(server_fn=server_fn)