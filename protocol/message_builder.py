from flwr.app import Message
from flwr.common import RecordDict,ConfigRecord,MessageType,Message

from protocol.transport import Transport
from protocol.session import ProtocolSession
class ProtocolMessageBuilder:
    
    # Build flwr training messages enriched with Secue Aggregation protocol metadata
    def build_train_messages(self,session:ProtocolSession,arrays,base_config,node_ids,arrayrecord_key,configrecord_key,server_round):
        print("\n=====================Message Builder===================")
        print(f"Sessiion: {session.session_id}")
        print(f"Session Object: {id(session)}")
        print(f"Public Key DIct: {id(session.public_keys)}")

        for node,packet in session.public_keys.items():
            print(node,type(node),packet.public_key.hex()[:16])
        

        messages = []
        for node_id in node_ids:
            config = ConfigRecord(dict(base_config))
            config["protocol-session-id"] = session.session_id
            config["protocol-session-salt"] = Transport.encode_bytes(session.session_salt)
            config["protocol-my-node"] = int(node_id)
            config["server-round"] = server_round
            peer_node = session.peer_assignments.get(node_id)
            if peer_node is not None:
                config["protocol-peer-node"] = int(peer_node)       
                peer_packet = session.public_keys.get(peer_node)
                if peer_packet is not None:
                    config["protocol-peer-public-key"] = Transport.encode_bytes(peer_packet.public_key)
                    print(f"[Builder] Node: {node_id} gets the peer: {peer_node}")
                else:
                    print(f"[Builder] Peer key missing for {peer_node}")
            record = RecordDict(
                {
                    arrayrecord_key:arrays,
                    configrecord_key: config,
                }
            )
            messages.append(Message(content=record,message_type=MessageType.TRAIN,dst_node_id=node_id))
        return messages
    