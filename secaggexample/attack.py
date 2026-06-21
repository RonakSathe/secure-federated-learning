import numpy as np
import random

def large_update_attack(model):
    model.coef_ *= 20
    return "large_update"

def sign_flip_attack(model):
    model.coef_ *= -1
    return "sign_flip"

def noise_injection_attack(model):
    model.coef_ += np.random.normal(0,1,model.coef_.shape)
    return "noise_injection"

def apply_attack(model):
    attack = random.choice([

        large_update_attack,
        sign_flip_attack,
        noise_injection_attack
    ])
    attack_name = attack(model)
    return attack_name