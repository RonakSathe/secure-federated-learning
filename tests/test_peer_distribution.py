from protocol.session import ProtocolSession
from protocol.key_registry import KeyRegistry
from protocol.peer_assignment import PeerAssignmentEngine
from protocol.peer_distribution import PeerDistributor
from protocol.packets import PublicKeyPacket
from security.key_manager import KeyManager

def main():
    #-------Creating Session----------
    #---------------------------------
    session = ProtocolSession(round_number=1)
    session.participants = [1,2,3,4]
    registry = KeyRegistry()

    print("\n =================Registering Public Keys==============")
    #-----------Simulating 4 clients
    for node in session.participants:
        km = KeyManager()
        packet = PublicKeyPacket(
            session_id=session.session_id,
            node_id=node,
            public_key=km.get_public_key_bytes(),
        )

        registry.register_key(session=session,packet=packet)
    registry.print_registry(session)

    #--------------------------
    #Assign Peers
    #--------------------------
    assignment_engine = PeerAssignmentEngine()
    session.peer_assignments = assignment_engine.assign(
        session.participants
    )

    print("\n=============Peer Assignments ==================")
    for node, peer in session.peer_assignments.items():
        print(f"{node}:- > {peer} ")

    #Creating Peer Packets
    distributor = PeerDistributor()
    packets = distributor.create_packet(
        session=session,
        registry=registry,
    )

    #Display Packets
    print("\n==========Peer Packets=================")

    for packet in packets:
        print("-------------------------------")
        print(f"Session:            {packet.session_id}")
        print(f"Sender:            {packet.sender_node}")
        print(f"Receiver:            {packet.receiver_node}")
        print(f"Peer:            {packet.peer_node}")
        print(f"Peer Key:            {packet.peer_public_key.hex()[:40]}")

if __name__ == "__main__":
    main()
    