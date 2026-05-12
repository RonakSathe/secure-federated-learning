#Core idea : weights+random mask
#Server aggregates masked values
# Clients remove mask -> get true aggregate

import numpy as np
#Shared seed
SHARED_SEED = 42

def generate_mask(shape_coef, shape_intercept):
    np.random.seed(SHARED_SEED)
    mask_coef = np.random.normal(0,0.5, shape_coef)
    mask_intercept = np.random.normal(0,0.5, shape_intercept)
    return mask_coef, mask_intercept


def apply_mask(params, client_id):
    coef, intercept = params
    masked_coef, masked_intercept = generate_mask(coef.shape, intercept.shape)

    if client_id == 0:
        print("Client A adding mask")
        return coef + masked_coef, intercept + masked_intercept
    else:
        print("Client B adding mask")
        return coef - masked_coef, intercept - masked_intercept

# def remove_mask(agg_params):
#     #The mask cancels out in the aggregate.
#     return agg_params