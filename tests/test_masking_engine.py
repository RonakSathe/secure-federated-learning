import secrets
import numpy as np

from protocol.masking_engine import MaskingEngine

engine = MaskingEngine()
shared_secret = secrets.token_bytes(32)

parameters = [
    np.ones((2,3)),
    np.ones((1,))
]

results = engine.mask_parameters(
    parameters=parameters,
    shared_secret=shared_secret,
    session_id="SESSION-001",
    round_number=1,
    session_salt=secrets.token_bytes(32),
    )

for result in results:
    print(f"Layer: {result.layer_id}")
    print(f"Original : {result.original}")
    print(f"Mask: {result.mask}")
    print(f"Masked param: {result.masked}")
    recovered = result.masked - result.mask
    print(np.allclose(recovered,result.original))