from flwr.serverapp.strategy import FedAvg
from pathlib import Path
from flwr.serverapp.strategy.strategy_utils import sample_nodes
from flwr.common import log, RecordDict,MessageType
import json
from logging import INFO

class AdaptiveSecureFedAvg(FedAvg):

    def configure_train(self, server_round, arrays, config, grid):

        # return super().configure_train(server_round, arrays, config, grid)
        # Do not configure federated train if fraction_train is 0.
        if self.fraction_train == 0.0:
            return []
        # Sample nodes
        num_nodes = int(len(list(grid.get_node_ids())) * self.fraction_train)
        sample_size = max(num_nodes, self.min_train_nodes)
        node_ids, num_total = sample_nodes(grid, self.min_available_nodes, sample_size)

        mapping = {}
        mapping_file  = Path("dashboard/client_mapping.json")
        if mapping_file.exists():
            with open(mapping_file,"r") as f:
                mapping =  json.load(f)
        
        blocked_partitions = set()
        blocked_file = Path("dashboard/blocked_clients.json")
        try:
            if blocked_file.exists():
                with open(blocked_file,"r") as f:
                    blocked_data = json.load(f)
                previous_round = blocked_data.get("generated_from_round",-1)
                if previous_round == server_round -1:
                    blokced_partitions = {
                        int(client["partition_id"]) for client in blocked_data.get("blocked_clients",[])
                    }
            print("Blocked Partitions: ", blokced_partitions)
        except Exception as e:
            print("Blocked FLie exception",e)

        #ALlowing the specific Node id:
        allowed_node_ids = []
        for node_id in node_ids:
            info = mapping.get(str(node_id))

            if info is None:
                print(f"Unknown Node: {node_id}")
                allowed_node_ids.append(node_id)
                continue
            partition = info["partition_id"]
            if partition in blocked_partitions:
                print(f"Skipping Node: {node_id} : \n Partition : {partition}")
                continue
            allowed_node_ids.append(node_id)

                

        log(
            INFO,
            "configure_train: Sampled %s nodes (out of %s)",
            len(node_ids),
            len(num_total),
        )
        print("\n ===========================================================")
        print(f"ROund: {server_round}")
        print(f"INitial Sampled: {node_ids}")
        print("\n ===========================================================")
        

        # Always inject current server round
        config["server-round"] = server_round

        # Construct messages
        record = RecordDict(
            {self.arrayrecord_key: arrays, self.configrecord_key: config}
        )
        return self._construct_messages(record=record, node_ids=allowed_node_ids,message_type=MessageType.TRAIN)
