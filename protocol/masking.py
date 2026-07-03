import hashlib
import numpy as np
from protocol.context import MaskContext

def secret_to_seed(shared_secret: bytes,context: MaskContext) -> int:
    """Convert a shared secret into deterministic interger seed"""

    # digest = hashlib.sha256(shared_secret).digest()
    hasher = hashlib.sha256()
    hasher.update(shared_secret)
    hasher.update(context.session_id.encode())
    hasher.update(context.round_number.to_bytes(4,"big"))
    hasher.update(context.layer_id.to_bytes(4,"big"))
    hasher.update(context.salt)
    digest = hasher.digest()

    return int.from_bytes(
        digest[:8],byteorder="big",signed=False
    )

def generate_mask(
        shared_secret: bytes,
        parameter: np.ndarray,
        context: MaskContext,
        distribution="normal",
        scale= 1.0,
        ) -> np.ndarray:
    """Generate a deterministic mask from a shared secret.
        Parameters: 
        ==================================================
        1. shared_secret: bytes
            Shared secret produced using X25519. 
        
        2. parameter: tuple
            SHape of the paramter array
        
        3. distribution: str
            'normal' or 'uniform'
        
        4. scale: float
            Standard deviation (normal)
            or range (uniform)

        Returns
        ===========
        numpy.ndarray
        ===========
    """
    seed = secret_to_seed(shared_secret=shared_secret, context=context)
    rng = np.random.default_rng(seed=seed)

    if distribution == "normal":
        mask = rng.normal(
            loc=0.0,
            scale=scale,
            size=parameter.shape,
        )
    elif distribution == "uniform":
        mask = rng.uniform(
            low=scale,
            high=scale,
            size=parameter.shape,
        )
    else:
        raise ValueError(f"Unknown distribution: {distribution}")
    return mask.astype(parameter.dtype)

    

