import numpy as np
from security.key_manager import KeyManager
from protocol.context import MaskContext
from protocol.masking import generate_mask
from protocol.pairwise_mask import generate_pairwise_mask

#Creating two clients
alice = KeyManager()
bob = KeyManager()
alice_public = alice.get_public_key_bytes()
bob_public = bob.get_public_key_bytes()

alice_secret  = alice.compute_shared_secret(bob_public)
bob_secret = bob.compute_shared_secret(alice_public)

print("="*60)
print("SHared Secret: Match: ", alice_secret==bob_secret)
print("="*60)

#Fake Model Param
parameter = np.zeros((4,4), dtype=np.float32)

#Protocol COntext
context = MaskContext(
    session_id="test-session",
    round_number=1,
    layer_id=0,
    salt=b"secure-fed-learning",
)

#Generating pairwise mask
mask_a = generate_pairwise_mask(
    shared_secret=alice_secret,
    parameter=parameter,
    context=context,
    my_node_id=1,
    peer_node_id=2,
)

mask_b = generate_pairwise_mask(
    shared_secret=bob_secret,
    parameter=parameter,
    context=context,
    my_node_id=2,
    peer_node_id=1,
)

print("\n Mask a", mask_a)
print("\n Mask b:",mask_b)

print(f"\n Norm a: {np.linalg.norm(mask_a)}")
print(f"\n Norm b: {np.linalg.norm(mask_b)}")


#COncallation test
cancellation = mask_a + mask_b

print("\n Cancellation matrix")
print(cancellation)
print("\n Cancellation NOrm", np.linalg.norm(cancellation))


assert np.allclose(cancellation,0.0)
print("\n Pairwise mask cancellation sucessfully")