import numpy as np
from protocol.masking import generate_mask

def generate_pairwise_mask(
        shared_secret,
        parameter,
        context,
        my_node_id,
        peer_node_id,):
    """Generating a pairwsie mask. smaller node ads , bigger node subtracts"""
    mask = generate_mask(
        shared_secret=shared_secret,
        parameter=parameter,
        context=context
    )

    if my_node_id < peer_node_id:
        return mask
    return -mask