from flwr.app import Context
from flwr.server import ServerAppComponents,ServerConfig,ServerApp
from flwr.server.strategy import FedAvg

def server_fn(context:Context):
    num_rounds = int(context.run_config.get("numm-server-rounds",10))

    strategy = FedAvg()
    config = ServerConfig(num_rounds=num_rounds)

    return ServerAppComponents(
        strategy=strategy,
        config=config,
    )

app = ServerApp(server_fn=server_fn)