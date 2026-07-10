import json
from pathlib import Path
from protocol.key_registry import PublicKeyPacket
from protocol.transport import Transport
from protocol.session import ProtocolSession

class ReplyProcessor:
    # Register public keys and update node/partition mapping
    def process_train_replies(self,session:ProtocolSession,replies,server_round,key_registry):
        mapping = {}
        mapping_file = Path("dashboard/client_mapping.json")
        if mapping_file.exists():
            with open(mapping_file) as f:
                mapping = json.load(f)
        for msg in replies:
            node_id = msg.metadata.src_node_id
            metrics = msg.content["metrics"]
            partition_id = int(metrics["partition_id"])
            public_key = Transport.decode_bytes(metrics["public_key"])

            packet = PublicKeyPacket(
                session_id=session.session_id,
                node_id=node_id,
                public_key=public_key,
            )
            print("Registering key")
            key_registry.register_key(session,packet)
            # print("\n------------Register Key--------")
            # print(f"Session : {session.session_id}")
            # print(f"Node: {packet.node_id}")
            # print(f"Keys: {len(session.public_keys)}")
            # print("current registry")
            # for node in session.public_keys:
            #     print(f" {node}")
            # print("Registered keys")

            print(f"Parittions: {partition_id}, Public key: {public_key.hex()[:32]}...")
            mapping[str(node_id)] = {
                "partition_id": partition_id,
                "last_round": server_round,
            }
        with open(mapping_file,"w+") as f:
            json.dump(mapping,f,indent=4)
        return mapping