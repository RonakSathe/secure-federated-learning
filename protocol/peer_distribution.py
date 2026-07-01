from .packets import PeerPacket
from protocol.session import ProtocolSession
from protocol.key_registry import KeyRegistry
class PeerDistributor:
    def create_packet(self,session:ProtocolSession,registry:KeyRegistry):
        packets =[]
        assignments = session.peer_assignments
        visited = set()

        for node, peer in assignments.items():
            if node in visited:
                continue
            visited.add(node)
            visited.add(peer)

            peer_key = registry.get_public_key(session=session,node_id=peer)
            node_key = registry.get_public_key(session=session,node_id=node)

            packets.append(PeerPacket(
                session_id=session.session_id,
                sender_node=0,
                receiver_node=node,
                peer_node=peer,
                peer_public_key=peer_key,
            ))

            packets.append(PeerPacket(
                session_id=session.session_id,
                sender_node=0,
                receiver_node=peer,
                peer_node=node,
                peer_public_key=node_key,
            ))
        return packets