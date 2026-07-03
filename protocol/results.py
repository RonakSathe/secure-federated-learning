from dataclasses import dataclass
import numpy as np

@dataclass
class MaskResult:
    layer_id: int
    original: np.ndarray
    mask: np.ndarray
    masked: np.ndarray
    context: object
