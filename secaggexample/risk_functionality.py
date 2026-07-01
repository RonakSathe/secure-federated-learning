def calculate_risk(metric:dict):
    risk = 0
    reasons = []

    if metric["update_norm"] > 0.5:
        risk += 60
        reasons.append("Large Update")
    
    if metric["coef_norm"] > 8:
        risk += 20
        reasons.append("Large WEight Norm")
    
    if metric["avg_cpu"] > 80:
        risk += 10
        reasons.append("High  CPU")
    
    if metric["avg_memory"] > 86:
        risk += 10
        reasons.append("High Memory")
    
    return risk,reasons