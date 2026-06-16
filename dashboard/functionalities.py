def calculate_trust_score(update_norm):
    return 100 if update_norm < 1 else (75 if update_norm < 5 else(50 if update_norm < 10 else 10))