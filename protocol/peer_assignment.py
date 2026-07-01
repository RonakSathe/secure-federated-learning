import random

class PeerAssignmentEngine:
    def assign(self,participants):
        participants = participants.copy()
        random.shuffle(participants)
        pairs={}

        while(len(participants) >= 2):
            a,b = participants.pop(), participants.pop()
            pairs[a],pairs[b] = b,a
        
        if participants:
            raise ValueError("Odd number of participants is not suported yet.")
        
        return pairs