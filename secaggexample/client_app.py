from flwr.client import ClientApp
from flwr.client.mod import secaggplus_mod
from flwr.common import Context

from secaggexample.task import create_client

def client_fn(context:Context):
    partition_id = int(context.node_config.get("partition-id",0))
    return create_client(partition_id).to_client()

app = ClientApp(client_fn=client_fn,mods=[secaggplus_mod])