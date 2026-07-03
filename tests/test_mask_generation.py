import secrets
import numpy as np
from protocol.context import MaskContext
from protocol.masking import generate_mask

shared_secret = secrets.token_bytes(32)

context = MaskContext(
    session_id="SESSION-001",
    round_number=2,
    layer_id=0,
    salt=secrets.token_bytes(32)
    )

parameter = np.zeros((2,3), dtype=np.float64)

mask1 = generate_mask(shared_secret,parameter,context)
mask2 = generate_mask(shared_secret,parameter,context)
mask3 = generate_mask(shared_secret,parameter,context)
context.round_number=3
mask4 = generate_mask(shared_secret,parameter,context)
print(np.allclose(mask1,mask4))