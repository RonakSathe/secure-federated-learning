#Core idea : weights+random mask
#Server aggregates masked values
# Clients remove mask -> get true aggregate

import numpy as np
#Storing mask globally
mask = None

def apply_mask(params):
    global mask
    coef, intercept = params

    #generate random mask
    mask = [
        np.random.normal(0,0.5, coef.shape),
        np.random.normal(0,0.5, intercept.shape)
    ]

    masked_params = [
        coef + mask[0],
        intercept + mask[1]
    ]

    print("Mask applied before sending to server.")
    return masked_params

def remove_mask(agg_params):
    global mask
    agg_coef, agg_intercept = agg_params

    if mask is None:
        return agg_params
    
    unmasked = [
        agg_coef - mask[0],
        agg_intercept - mask[1]
    ]
    print("Mask removed after aggregation.")
    return unmasked