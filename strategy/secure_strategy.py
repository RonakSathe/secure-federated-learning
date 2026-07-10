import json
from pathlib import Path
from flwr.serverapp.strategy import FedAvg
from flwr.serverapp.strategy.strategy_utils import sample_nodes
from flwr.common import log
from logging import INFO
from protocol.server_protocol_engine import ServerProtocolEngine
#testing 
from protocol.key_registry import KeyRegistry
from protocol.transport import Transport
class SecureFedAvg(FedAvg):
   def __init__(self,*args,**kwargs):
       super().__init__(*args,**kwargs)
       self.server_engine = ServerProtocolEngine()
   
   
#    def _construct_protocol_messages(self,arrays,base_config,node_ids,server_round):
#        messages = []
#        session = self.server_engine.coordinator.current_session
#        for node_id in node_ids:
#            config = ConfigRecord(dict(base_config))
#            config["server-round"] = server_round
#            config["protocol-session-id"] = session.session_id
#            config["protocol-session-salt"] = Transport.encode_bytes(session.session_salt)
#            config["protocol-my-node"] = int(node_id)
#            peer_node = session.peer_assignments.get(node_id)
#            config["protocol-peer-node"] = int(peer_node)
#            if peer_node is not None:
#                peer_packet = session.public_keys.get(peer_node)
#                if peer_packet is not None:
#                    config["protocol-peer-node"] = int(peer_node)
#                    config["protocol-peer-public-key"] = (Transport.encode_bytes(peer_packet.public_key))
#                    print(f"[Server] Node: {node_id} gets Peer: {peer_node}")
#                else:
#                    print(f"[Server] Peer Key for Node: {peer_node} not available yet")
#            record = RecordDict({
#                self.arrayrecord_key:arrays,
#                self.configrecord_key:config
#            })
#            message = Message(content=record,message_type=MessageType.TRAIN,dst_node_id=node_id)
#            messages.append(message)
#        return messages




   
   def configure_train(self, server_round, arrays, config, grid):

        # return super().configure_train(server_round, arrays, config, grid)
        # Do not configure federated train if fraction_train is 0.
        
        print("\n ===========CONFIGURE TRAIN ===============")
        print(f"ROund: {server_round}")
        session = self.server_engine.current_session

        if session is None:
            print("No active session")
        else:
            print(f"Session: {session.session_id}")
            print(f"Stored : {len(session.public_keys)} keys")


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
                    blocked_partitions = {
                        int(client["partition_id"]) for client in blocked_data.get("blocked_clients",[])
                    }
            print("Blocked Partitions: ", blocked_partitions)
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

        self.server_engine.start_round(
            round_number=server_round,
            participants=allowed_node_ids,
        )
        
        print("\n\n Allowed Nodes:")
        print(allowed_node_ids)

        

                

        log(
            INFO,
            "configure_train: Sampled %s nodes (out of %s)",
            len(node_ids),
            num_total,
        )
        print("\n ===========================================================")
        print(f"ROund: {server_round}")
        print(f"INitial Sampled: {node_ids}")
        print("\n ===========================================================")
        
        # return
        return self.server_engine.build_training_messages(
            strategy=self,
            arrays=arrays,
            base_config=config,
            node_ids=allowed_node_ids,
            server_round=server_round
        )

   #Validating replies, Updated nodes -? parition mapping, debigguing information, delegating agregatio nto fedavg.
   def aggregate_train(self,server_round,replies):
        valid_replies, failures = self._check_and_log_replies(replies,is_train=True)
        print(f"\n\n aggregated_train received: {len(valid_replies)} replies")
       
        mapping = self.server_engine.process_train_replies(replies=valid_replies,server_round=server_round)  
        print(f"Public Keys Stored: {self.server_engine.public_key_count}")
        print("\n\n =========NODE Mapping ================")
        for node, info in mapping.items():
            print(f"Node: {node} -> Partition {info['partition_id']}")
        
        return super().aggregate_train(server_round=server_round,replies=valid_replies)