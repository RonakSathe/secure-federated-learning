import numpy as np
from security.key_manager import KeyManager
from protocol.context import MaskContext
from protocol.pairwise_mask import generate_pairwise_mask

#Create key maangers
alice = KeyManager()
bob = KeyManager()

alice_secret = alice.compute_shared_secret(bob.get_public_key_bytes())
bob_secret = bob.compute_shared_secret(alice.get_public_key_bytes())

print("SHared Secret Match:", alice_secret == bob_secret)

#Fake model updates
model_a = np.random.randn(5,5)
model_b = np.random.randn(5,5)

print("\n Original Aggregation NOrm: ")
print(np.linalg.norm(model_a+model_b))


#COntext
context = MaskContext(
    session_id="secure-test",
    round_number=1,
    layer_id=0,
    salt=b"aggregation-test",
)

#pairwise masaks
mask_a = generate_pairwise_mask(
    shared_secret=alice_secret,
    parameter= model_a,
    context=context,
    my_node_id=1,
    peer_node_id=2,
)

mask_b = generate_pairwise_mask(
    shared_secret=bob_secret,
    parameter=model_b,
    context=context,
    my_node_id=2,
    peer_node_id=1,
)

#CLient upload masked models 

masked_a = model_a + mask_a
masked_b = model_b + mask_b

#Server aggregats
aggregated = masked_a+masked_b
expected = model_a + model_b

print("\n Recovered Aggregted norm:", np.linalg.norm(aggregated))
print("\n Expected Aggregated Nomr", np.linalg.norm(expected))

difference = np.linalg.norm(
    aggregated - expected
)

print("\n Difference: ", difference)

assert np.allclose(aggregated,expected,atol=1e-10)
print("\n Secure Aggregation property verified")