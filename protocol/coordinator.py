from .session import ProtocolSession
from .assignment import AssignmentEngine
from .state import ProtocolState
class ProtocolCoordinator:
    def __init__(self):
        self.current_session = None

    def set_state(self,new_state):
        self.current_session.state = new_state
        print(f"\n Protocol State --> {new_state.value} \n")
    
    def update_state(self,new_state):
        self.current_session.state = new_state
        print("\n ==============")
        print(f"Protocol State Updated to: {new_state.value}")
        print("\n ==============")
    
    def create_session(self,round_number,participants):
        self.current_session = ProtocolSession(round_number=round_number)
        self.current_session.participants = participants

        engine = AssignmentEngine()

        assignment = engine.assign(participants=participants)
        print("\n\n ====================Mask Assignment ====================")

        #Packet Printing
        print("\n\n Packet Printing")
        for packet in assignment.values():
            packet.session_id = self.current_session.session_id
            print(packet)

        print("\n ================Session Created ====================")

        print(f"Session ID: {self.current_session.session_id}")
        print(f"ROund : {round_number}")
        print(f"Participants: {participants}")

        self.update_state(ProtocolState.PARTICIPANTS_SELECTED)
        
        return self.current_session
    
    
    
    