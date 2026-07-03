import random
from .packet import MaskPacket
class AssignmentEngine:
    def assign(self,participants):
        """Assign a zero-sum mask to every Participant."""
        participants = participants.copy()
        random.shuffle(participants)
        assignments = {}
        for i in range(0,len(participants),2):
            a = participants[i]
            b = participants[i+1]

            assignments[a],assignments[b]=b,a
        return assignments