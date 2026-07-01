import hashlib
import numpy as np

def secret_to_seed(shared_secret: bytes) -> int:
    """Convert a shared secret into deterministic interger seed"""

    digest = hashlib.sha256(shared_secret).digest()

    return int.from_bytes(
        digest[:8],byteorder="big",signed=False
    )

def generate_mask(
        shared_secret: bytes,
        shape,
        distribution="normal",
        scale= 1.0,
        ):
    """Generate a deterministic mask from a shared secret.
        Parameters: 
        ==================================================
        1. shared_secret: bytes
            Shared secret produced using X25519. 
        
        2. shape: tuple
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
    seed = secret_to_seed(shared_secret=shared_secret)
    rng = np.random.default_rng(seed=seed)

    if distribution == "normal":
        mask = rng.normal(
            loc=0.0,
            scale=scale,
            size=shape,
        )
    elif distribution == "uniform":
        mask = rng.uniform(
            low=scale,
            high=scale,
            size=shape,
        )
    else:
        raise ValueError(f"Unknown distribution: {distribution}")
    return mask.astype(np.float64)

    

