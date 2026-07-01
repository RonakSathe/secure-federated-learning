from .base_stage import ProtocolStage
from protocol.peer_assignment import PeerAssignmentEngine
from protocol.session import ProtocolSession

class PeerAssignmentStage(ProtocolStage):
    def run(self,session: ProtocolSession):
        engine = PeerAssignmentEngine()

        session.peer_assignments = engine.assign(
            session.participants
        )

        print(f"\n Peer Assignments")
        for node, peer in session.peer_assignments.items():
            print(f"Node: {node} -> Peer: {peer}")
            