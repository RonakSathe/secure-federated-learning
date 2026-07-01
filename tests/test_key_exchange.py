import numpy as np
from security.key_manager import KeyManager
from protocol.masking import generate_mask

import os
import sys

print("Current directory:", os.getcwd())
print("sys.path[0]:", sys.path[0])



alice = KeyManager()
bob = KeyManager()

alice_secret = alice.compute_shared_secret(bob.get_public_key_bytes())
bob_secret = bob.compute_shared_secret(alice.get_public_key_bytes())

print("Shared Secret Mathc:")
print(alice_secret == bob_secret)

mask1 = generate_mask(
    alice_secret,
    shape=(3,4),
)

mask2 = generate_mask(
    bob_secret,
    shape=(3,4),
)

print(f"\n Mask1: {mask1} ")
print(f"\n Mask2: {mask2} ")

print(f"\n\n Maks Equal?: {np.allclose(mask1,mask2)}")
