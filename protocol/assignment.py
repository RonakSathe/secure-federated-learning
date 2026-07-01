import random
from .packet import MaskPacket
class AssignmentEngine:
    def assign(self,participants):
        """Assign a zero-sum mask to every Participant."""

        n = len(participants)
        if n<2:
            raise ValueError("\n\n Need atleast two participants")
        masks = []
        total = 0
        #Generating n-1 random integers
        for _ in range(n-1):
            value = random.randint(-100,100)
            masks.append(value)
            total += value
        
        #Last value makes the sum zero
        masks.append(-total)

        random.shuffle(masks)
        assignment = {}
        for node_id , mask in zip(participants,masks):
            assignment[node_id] = MaskPacket(
                node_id=node_id,
                mask=mask,
            )
        return assignment