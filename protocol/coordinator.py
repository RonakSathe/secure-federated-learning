from .session import ProtocolSession
from .peer_assignment import PeerAssignmentEngine
from .state import ProtocolState
from .key_registry import KeyRegistry


class ProtocolCoordinator:
    def __init__(self):
        self.current_session = None
        self.key_registry = KeyRegistry()
        self.session_history = []
        self.assignment_engine = PeerAssignmentEngine()

    def start_round(self,round_number,participants):
        if self.current_session is None:
            self.current_session = ProtocolSession(round_number=round_number)
            print("New Protocol Session")
        self.current_session.round_number=round_number
        self.current_session.participants = participants

        if not self.current_session.peer_assignments:
            assignment = self.assignment_engine.assign(participants=participants)
            print("\n Peer Assignments Created")
            self.current_session.peer_assignments = assignment
        self.update_state(ProtocolState.PARTICIPANTS_SELECTED)
        print("\n========== PROTOCOL STATUS ==========")
        print("Session :", self.current_session.session_id)
        print("Round   :", self.current_session.round_number)
        print("Peers   :", len(self.current_session.peer_assignments))
        print("Keys    :", len(self.current_session.public_keys))
        print("=====================================\n")
        return self.current_session


    def set_state(self,new_state):
        self.current_session.state = new_state
        print(f"\n Protocol State --> {new_state.value} \n")

    
    def update_state(self,new_state):
        self.current_session.state = new_state
        print("\n ==============")
        print(f"Protocol State Updated to: {new_state.value}")
        print("\n ==============")
    
    
    
    