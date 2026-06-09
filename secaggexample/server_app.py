import ray
from flwr.common import ndarrays_to_parameters
from flwr.server import ServerApp, ServerAppComponents, ServerConfig
from flwr.server.strategy import FedAvg
from . import task 

if not ray.is_initialized():
    ray.init(
        _node_ip_address="127.0.0.1",
        configure_logging=False,
        include_dashboard=False
    )

def server_fn(context):
    init_model = task.build_model()
    initial_parameters = ndarrays_to_parameters(task.get_parameters(init_model))

    # Clean strategy without manual config handlers
    strategy = FedAvg(
        fraction_fit=1.0,
        min_fit_clients=3,
        min_available_clients=3,
        initial_parameters=initial_parameters,
    )
    config = ServerConfig(num_rounds=3)
    
    return ServerAppComponents(
        strategy=strategy, 
        config=config
    )

# Standard App initialization. Flower will inject the workflow 
# specified in your pyproject.toml smoothly on startup.
app = ServerApp(server_fn=server_fn)