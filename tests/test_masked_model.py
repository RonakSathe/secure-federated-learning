import numpy as np
from protocol.client_protocol import CLientProtocol
from protocol.masking_engine import MaskingEngine

#Creating 2 clients

alice = CLientProtocol(partition_id=1)
bob = CLientProtocol(partition_id=2)

#Exchange public keys
alice_pk = alice.generate_public_key()
bob_pk = bob.generate_public_key()

alice.receive_peer_public_key(2,bob_pk)
bob.receive_peer_public_key(1,alice_pk)

alice_secret = alice.compute_shared_secret()
bob_secret = bob.compute_shared_secret()

print("\n Share Secret Equal:",alice_secret==bob_secret)

#Fake model Parameters
coef = np.array([[1.0,2.0,3.0]])
intercept = np.array([0.5])

params = [coef,intercept]

#Mask
engine = MaskingEngine()

masked1 = engine.mask_parameters(params,alice_secret)
masked2 = engine.mask_parameters(params,bob_secret)

print("\n Masked parameters Equal : ?")

for i, (a,b) in enumerate(zip(masked1,masked2)):
    print(f"Array {i}: {np.allclose(a,b)}")