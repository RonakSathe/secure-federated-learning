import json
from pathlib import Path
from flwr.serverapp.strategy import FedAvg
from flwr.serverapp.strategy.strategy_utils import sample_nodes
from flwr.common import log, RecordDict,MessageType,ConfigRecord,Message
from logging import INFO
#testing 
from protocol.coordinator import ProtocolCoordinator
from protocol.key_registry import PublicKeyPacket
from protocol.transport import Transport

class SecureFedAvg(FedAvg):
   def __init__(self,*args,**kwargs):
       super().__init__(*args,**kwargs)
       self.coordinator = ProtocolCoordinator()
   
   
   def _construct_protocol_messages(self,arrays,base_config,node_ids,server_round):
       messages = []
       session = self.coordinator.current_session
       for node_id in node_ids:
           config = ConfigRecord(dict(base_config))
           config["server-round"] = server_round
           config["protocol-session-id"] = session.session_id
           config["protocol-session-salt"] = Transport.encode_bytes(session.session_salt)
           peer_node = session.peer_assignments.get(node_id)
           if peer_node is not None:
               peer_packet = session.public_keys.get(peer_node)
               if peer_packet is not None:
                   config["protocol-peer-node"] = int(peer_node)
                   config["protocol-peer-public-key"] = (Transport.encode_bytes(peer_packet.public_key))
                   print(f"[Server] Node: {node_id} gets Peer: {peer_node}")
               else:
                   print(f"[Server] Peer Key for Node: {peer_node} not available yet")
           record = RecordDict({
               self.arrayrecord_key:arrays,
               self.configrecord_key:config
           })
           message = Message(content=record,message_type=MessageType.TRAIN,dst_node_id=node_id)
           messages.append(message)
       return messages




   
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

        session = self.coordinator.start_round(
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
        

        # Always inject current server round
        config["server-round"] = server_round
        
        # return
        return self._construct_protocol_messages(
            arrays=arrays,
            base_config=config,
            node_ids=allowed_node_ids,
            server_round=server_round,
        )

   #Validating replies, Updated nodes -? parition mapping, debigguing information, delegating agregatio nto fedavg.
   def aggregate_train(self,server_round,replies):
        valid_replies, failures = self._check_and_log_replies(replies,is_train=True)
        print(f"\n\n aggregated_train received: {len(valid_replies)} replies")
       
        #Mapping of Node id with the Partition id
        mapping,mapping_file = {},Path("dashboard/client_mapping.json")
        if mapping_file.exists():
            with open(mapping_file,"r") as f:
                mapping = json.load(f)
        for msg in valid_replies:
            node_id = str(msg.metadata.src_node_id)
            metrics = msg.content["metrics"]
            partition_id = int(metrics["partition_id"])
            public_key = Transport.decode_bytes(metrics["public_key"])

            
            packet = PublicKeyPacket(
                session_id = self.coordinator.current_session.session_id,
                node_id = msg.metadata.src_node_id,
                public_key = public_key,
            )
            self.coordinator.key_registry.register_key(
                self.coordinator.current_session,
                packet=packet,
            )

            print(f"Partition id: {partition_id} with public key: {public_key.hex()}")
            mapping[node_id] = { "partition_id": partition_id,"last_round": server_round,}
        
        print(f"\n ==================Publick Key Registry ===================)")
        for node,packet in self.coordinator.current_session.public_keys.items():
            print(f"Node: {node}, Session: {packet.session_id} : Key: {packet.public_key.hex()[:32]}")

        print(f"Public Keys Stored: {len(self.coordinator.current_session.public_keys)}")
        with open(mapping_file,"w") as f: json.dump(mapping,f,indent=4)
        print("\n\n =========NODE Mapping ================")
        for node, info in mapping.items():
            print(f"Node: {node} -> Partition {info['partition_id']}")
        
        return super().aggregate_train(server_round=server_round,replies=valid_replies)